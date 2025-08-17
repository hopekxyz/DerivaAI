# --- Bibliotecas utilizadas --- #
import streamlit_authenticator as stauth
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.sql import text

def main():
    # Carrego o CSS do chat (formataÃ§Ã£o front-end).
    load_css()

    # Carrega a configuraÃ§Ã£o do autenticador a partir dos secrets, jÃ¡ que estamos autenticando o usuÃ¡rio usando o streamlit_authenticator.
    config = st.secrets
    
    authenticator = stauth.Authenticate(
        config['credentials'].to_dict(), # Converte a seÃ§Ã£o de credenciais para dicionÃ¡rio
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Renderiza o formulÃ¡rio de login na tela
    authenticator.login()

    # --- Controle de acesso. Se ele estiver autenticado, authentication_status retornarÃ¡ True. Se nÃ£o tiver (visitante), retornarÃ¡ None. Caso o login dÃª errado, retorna False ---

    if st.session_state["authentication_status"]:
        # --- USUÃRIO LOGADO (ASSINANTE), dÃ¡ uma olhada aqui de novo ---
        with st.sidebar:
             st.write(f'Bem-vindo *{st.session_state["name"]}*!')
             authenticator.logout() # Mostra o botÃ£o de logout na sidebar

        # A biblioteca salva o login (ex: 'jsmith') em st.session_state["username"]
        user_login = st.session_state["username"]
        user_email = config['credentials']['usernames'][user_login]['email']
        user_id = get_user_id_by_email(user_email)
        
        if user_id:
            pagina_chat(user_id) # Inicia o chat com o ID do usuÃ¡rio correto

        # Tem necessidade desse else aqui? Tem como o usuÃ¡rio logar sem ele estar na base de dados?
        else:
            st.error("Erro: UsuÃ¡rio autenticado nÃ£o encontrado em nosso banco de dados. Contate o suporte.")

    elif st.session_state["authentication_status"] is False:
        st.error('UsuÃ¡rio ou senha incorretos.')

    elif st.session_state["authentication_status"] is None:
        # --- Caso de ser visitante ---
        st.info("ðŸ‘‹ Bem-vindo ao DerivaAI! FaÃ§a o login para acessar seu histÃ³rico de conversas.")
        st.warning("No momento, a funcionalidade para visitantes estÃ¡ em desenvolvimento. Por favor, utilize uma das contas de teste para acessar.")
        # Futuramente, aqui entrarÃ¡ a lÃ³gica do chat limitado para visitantes.


# --- ObtÃ©m o ID do usuÃ¡rio a partir do email, utilizado para autenticaÃ§Ã£o. --- #
def get_user_id_by_email(email: str):
    """Busca o user_id no banco de dados a partir de um email."""
    conn = st.connection("postgres", type="sql")
    query = 'SELECT user_id FROM usuarios WHERE TRIM(LOWER(email)) = LOWER(:email);'
    result = conn.query(query, params={"email": email})
    if not result.empty:
        return int(result.iloc[0]['user_id'])
    return None

# Carrega a chave da API da OpenAI a partir dos Secrets do Streamlit.

try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("A chave de API da OpenAI nÃ£o foi encontrada. Por favor, configure-a nos Secrets do Streamlit.")
    st.stop()

# ConfiguraÃ§Ãµes de favicon e tÃ­tulo de aba

st.set_page_config(
    page_title="DerivaAI",
    page_icon="ðŸ§ ",
    layout="wide"
)

# FunÃ§Ã£o para carregar CSS a partir de um arquivo externo
def load_css(file_path="style.css"):
    try:
        with open(file_path, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo de estilo '{file_path}' nÃ£o encontrado.")

# --- Aqui vai a lÃ³gica do agente em si. ---

# Carrega o prompt principal do sistema a partir de um arquivo de texto
def carregar_prompt_sistema(file_path="prompt_revisado.txt"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Substituir chaves para evitar conflito com o f-string do Python
            return f.read().replace("{", "{{").replace("}", "}}")
    except FileNotFoundError:
        st.error(f"Arquivo de prompt '{file_path}' nÃ£o encontrado. Verifique se ele estÃ¡ no repositÃ³rio.")
        st.stop()

# Inicializa o modelo de linguagem (LLM) da OpenAI
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Cria o template do prompt que serÃ¡ usado na cadeia
template = ChatPromptTemplate.from_messages([
    ('placeholder', '{memoria}'),
    ('system', carregar_prompt_sistema()),
    ('human', '{pergunta}')
])

# Cria a cadeia de conversaÃ§Ã£o que une o template e o LLM
chain_memoria = template | llm

def salvar_mensagem(user_id, tipo, conteudo):
    """
    Salva uma nova mensagem no banco de dados PostgreSQL.
    'tipo' pode ser 'user' ou 'ai'.
    """
    try:
        conn = st.connection("postgres", type="sql")
        with conn.session as s:
            s.execute(
                text('INSERT INTO conversas (user_id, sender, message_content) VALUES (:user_id, :sender, :content);'),
                params=dict(user_id=user_id, sender=tipo, content=conteudo)
            )
            s.commit()
    except Exception as e:
        st.error(f"Erro ao salvar mensagem: {e}")

def carregar_mensagens(user_id):
    """
    Carrega o histÃ³rico de mensagens de um usuÃ¡rio especÃ­fico do banco de dados.
    Retorna uma lista de tuplas (sender, message_content).
    """
    try:
        conn = st.connection("postgres", type="sql")
        df = conn.query(
            'SELECT sender, message_content FROM conversas WHERE user_id = :user_id ORDER BY timestamp;',
            params={"user_id": user_id},
            ttl=0 # Desativa o cache para sempre ter o histÃ³rico mais recente
        )
        return [(row.sender, row.message_content) for index, row in df.iterrows()]
    except Exception as e:
        st.error(f"Erro ao carregar mensagens: {e}")
        return []

# --- 5. LÃ“GICA DA PÃGINA DE CHAT (INTERFACE DO USUÃRIO) ---

def pagina_chat(user_id):
    st.header("Bem-vindo ao DerivaAI! ðŸ§ ")

    # Inicializa a memÃ³ria da conversa para a sessÃ£o atual
    # Utilizo o SummaryBuffer pra economizar memÃ³ria e nÃ£o perder contexto a longo-prazo: o melhor dos dois mundos.
    memoria = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    # Carrega o histÃ³rico de mensagens do banco de dados e exibe na tela
    mensagens_salvas = carregar_mensagens(user_id)
    for tipo, conteudo in mensagens_salvas:
        # Adiciona a mensagem Ã  memÃ³ria do LangChain para manter o contexto
        # Vai carregar esse contexto toda vez que o usuÃ¡rio reiniciar a aplicaÃ§Ã£o, supostamente. A longo prazo, Ã© insustentÃ¡vel: O jeito vai ser armazenar contexto no DB?
        if tipo == "user":
            memoria.chat_memory.add_user_message(conteudo)
        elif tipo == "ai":
            memoria.chat_memory.add_ai_message(conteudo)
        
        # Exibe a mensagem na interface do usuÃ¡rio
        with st.chat_message(tipo):
            st.markdown(conteudo)

    # Campo de entrada de texto do usuÃ¡rio
    prompt_usuario = st.chat_input("Como posso te ajudar com CÃ¡lculo?")
    if prompt_usuario:
        # Salva e exibe a mensagem do usuÃ¡rio
        # EstÃ¡ tendo um delay do usuÃ¡rio mandar a mensagem e aparecer na tela. DÃ¡ uma olhada aqui depois pra ver o que pode ser.
        salvar_mensagem(user_id, "user", prompt_usuario)
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        # Processa a pergunta e obtÃ©m a resposta da IA
        # Aqui dÃ¡ pra colocar um stream pra escrever em tempo real, ficaria melhor?
        with st.spinner("DerivaAI estÃ¡ pensando..."):
            resposta = chain_memoria.invoke({'memoria': memoria.buffer, 'pergunta': prompt_usuario})
            resposta_texto = resposta.content
        
        # Salva e exibe a resposta da IA
        salvar_mensagem(user_id, "ai", resposta_texto)
        with st.chat_message("ai"):
            st.markdown(resposta_texto)
            

if __name__ == "__main__":
    main()