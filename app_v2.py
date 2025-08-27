# ======================================================================
# 1. SEÇÃO DE IMPORTS (no topo, apenas uma vez)
# ======================================================================
import streamlit as st
import streamlit_authenticator as stauth
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.sql import text
import bcrypt

# ======================================================================
# 2. SEÇÃO DE CONFIGURAÇÃO E INICIALIZAÇÃO (OpenAI, LLM, etc.)
# ======================================================================
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("A chave de API da OpenAI não foi encontrada. Por favor, configure-a nos Secrets do Streamlit.")
    st.stop()

st.set_page_config(
    page_title="DerivaAI",
    page_icon="🧠",
    layout="wide"
)

llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# ======================================================================
# 3. SEÇÃO COM TODAS AS SUAS DEFINIÇÕES DE FUNÇÕES
# ======================================================================

def load_css(file_path="style.css"):
    try:
        with open(file_path, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo de estilo '{file_path}' não encontrado.")

def carregar_prompt_sistema(file_path="prompt_revisado.txt"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().replace("{", "{{").replace("}", "}}")
    except FileNotFoundError:
        st.error(f"Arquivo de prompt '{file_path}' não encontrado. Verifique se ele está no repositório.")
        st.stop()

def get_user_from_db(email: str):
    """Busca um usuário completo no banco de dados pelo email."""
    conn = st.connection("postgres", type="sql")
    query = 'SELECT user_id, name, password_hash FROM usuarios WHERE TRIM(LOWER(email)) = LOWER(:email);'
    result = conn.query(query, params={"email": email})
    if not result.empty:
        return result.iloc[0]
    return None

def create_user_in_db(email, name, plain_password):
    """Cria um novo usuário no banco, com senha hasheada."""
    conn = st.connection("postgres", type="sql")
    
    query = 'SELECT user_id FROM usuarios WHERE TRIM(LOWER(email)) = LOWER(:email);'
    existing_user = conn.query(query, params={"email": email})
    
    if not existing_user.empty:
        return False

    hashed_password = stauth.Hasher().hash(plain_password)
    
    with conn.session as s:
        s.execute(
            text('INSERT INTO usuarios (email, name, password_hash, account_type, trial_ends_at) VALUES (:email, :name, :password, :type, NOW() + INTERVAL \'1 month\');'),
            params=dict(email=email, name=name, password=hashed_password, type='assinante')
        )
        s.commit()
    return True

def salvar_mensagem(user_id, tipo, conteudo):
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
    try:
        conn = st.connection("postgres", type="sql")
        df = conn.query(
            'SELECT sender, message_content FROM conversas WHERE user_id = :user_id ORDER BY timestamp;',
            params={"user_id": user_id},
            ttl=0
        )
        return [(row.sender, row.message_content) for index, row in df.iterrows()]
    except Exception as e:
        st.error(f"Erro ao carregar mensagens: {e}")
        return []

def pagina_chat(user_id):
    st.header("Bem-vindo ao DerivaAI! 🧠")

    template = ChatPromptTemplate.from_messages([
        ('placeholder', '{memoria}'),
        ('system', carregar_prompt_sistema()),
        ('human', '{pergunta}')
    ])
    chain_memoria = template | llm

    memoria = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    mensagens_salvas = carregar_mensagens(user_id)
    for tipo, conteudo in mensagens_salvas:
        if tipo == "user":
            memoria.chat_memory.add_user_message(conteudo)
        elif tipo == "ai":
            memoria.chat_memory.add_ai_message(conteudo)
        
        with st.chat_message(tipo):
            st.markdown(conteudo)

    prompt_usuario = st.chat_input("Como posso te ajudar com Cálculo?")
    if prompt_usuario:
        salvar_mensagem(user_id, "user", prompt_usuario)
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.spinner("DerivaAI está pensando..."):
            resposta = chain_memoria.invoke({'memoria': memoria.buffer, 'pergunta': prompt_usuario})
            resposta_texto = resposta.content
        
        salvar_mensagem(user_id, "ai", resposta_texto)
        with st.chat_message("ai"):
            st.markdown(resposta_texto)

# ======================================================================
# 4. A ÚNICA E CORRETA FUNÇÃO main()
# ======================================================================
def main():
    load_css()
    # --- INÍCIO DO AVISO DE FASE BETA ---
    st.info(
        """
        🧪 **Você está participando da fase de testes (Beta) do DerivaAI!** Nesta fase, sua experiência e feedback são essenciais para nos ajudar a construir a melhor 
        ferramenta de aprendizado possível. Se encontrar qualquer problema ou tiver sugestões, entre em contato no Instagram @deriva.ai .
        """, 
        icon="🧪"
    )
    # --- FIM DO AVISO ---

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if st.session_state.get("authentication_status"):
        with st.sidebar:
             st.write(f'Bem-vindo *{st.session_state["name"]}*!')
             if st.button("Logout"):
                 st.session_state["authentication_status"] = None
                 st.session_state["name"] = None
                 st.session_state["user_id"] = None
                 st.rerun()
        
        pagina_chat(st.session_state["user_id"])
        
    else:
        choice = st.selectbox("Escolha uma opção:", ["Login", "Registrar"])
        if choice == "Login":
            st.subheader("Faça seu Login")
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Senha", type="password")
                login_submitted = st.form_submit_button("Login")

                if login_submitted:
                    user_data = get_user_from_db(email)
                    if user_data is not None:
                        # Usando bcrypt.checkpw para verificar a senha
                        if bcrypt.checkpw(password.encode(), user_data['password_hash'].encode()):
                            st.session_state["authentication_status"] = True
                            st.session_state["name"] = user_data['name']
                            st.session_state["user_id"] = int(user_data['user_id'])
                            st.rerun()
                        else:
                            st.error("Usuário ou senha incorretos.")
                    else:
                        st.error("Usuário ou senha incorretos.")
        
        elif choice == "Registrar":
            st.subheader("Crie sua Conta")
            with st.form("registration_form"):
                new_email = st.text_input("Email*")
                new_name = st.text_input("Nome*")
                new_password = st.text_input("Senha*", type="password")
                confirm_password = st.text_input("Confirme a Senha*", type="password")
                submitted = st.form_submit_button("Registrar")

                if submitted:
                    if not new_email or not new_name or not new_password:
                        st.error("Por favor, preencha todos os campos obrigatórios.")
                    elif new_password != confirm_password:
                        st.error("As senhas não coincidem.")
                    else:
                        user_created = create_user_in_db(new_email, new_name, new_password)
                        if user_created:
                            st.success("Usuário criado com sucesso! Por favor, volte para a tela de Login.")
                            st.balloons()
                        else:
                            st.error("Este email já está cadastrado.")

# ======================================================================
# 5. PONTO DE ENTRADA DO SCRIPT (no final, apenas uma vez)
# ======================================================================
if __name__ == "__main__":
    main()