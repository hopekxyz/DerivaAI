# --------------------------------------------------------------------------
# DerivaAI - Professor Particular de Cálculo
#
# Fase 1 - MVP Robusto com Banco de Dados
#
# Este script representa a aplicação funcional conectada a um banco de 
# dados PostgreSQL para persistência de dados.
# --------------------------------------------------------------------------

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.sql import text # Para executar SQL de forma segura

# --- 1. CONFIGURAÇÃO INICIAL E CHAVES DE API ---

# Carrega a chave da API da OpenAI a partir dos "Secrets" do Streamlit
# Este é o método seguro para usar credenciais em produção.
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("A chave de API da OpenAI não foi encontrada. Por favor, configure-a nos Secrets do Streamlit.")
    st.stop()

# TODO: Substituir user_id hardcoded por um sistema de autenticação dinâmico no Passo 3.
user_id = 1 

# --- 2. CONFIGURAÇÃO DA PÁGINA E ESTILOS ---

st.set_page_config(
    page_title="DerivaAI",
    page_icon="🧠",
    layout="wide"
)

# Função para carregar CSS a partir de um arquivo externo
def load_css(file_path="style.css"):
    try:
        with open(file_path, encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo de estilo '{file_path}' não encontrado.")

# --- 3. LÓGICA DO CHATBOT (LANGCHAIN E OPENAI) ---

# Carrega o prompt principal do sistema a partir de um arquivo de texto
def carregar_prompt_sistema(file_path="prompt_revisado.txt"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Substituir chaves para evitar conflito com o f-string do Python
            return f.read().replace("{", "{{").replace("}", "}}")
    except FileNotFoundError:
        st.error(f"Arquivo de prompt '{file_path}' não encontrado. Verifique se ele está no repositório.")
        st.stop()

# Inicializa o modelo de linguagem (LLM) da OpenAI
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Cria o template do prompt que será usado na cadeia
template = ChatPromptTemplate.from_messages([
    ('placeholder', '{memoria}'),
    ('system', carregar_prompt_sistema()),
    ('human', '{pergunta}')
])

# Cria a cadeia de conversação que une o template e o LLM
chain_memoria = template | llm

# --- 4. FUNÇÕES DE INTERAÇÃO COM O BANCO DE DADOS (POSTGRESQL) ---

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
    Carrega o histórico de mensagens de um usuário específico do banco de dados.
    Retorna uma lista de tuplas (sender, message_content).
    """
    try:
        conn = st.connection("postgres", type="sql")
        df = conn.query(
            'SELECT sender, message_content FROM conversas WHERE user_id = :user_id ORDER BY timestamp;',
            params={"user_id": user_id},
            ttl=0  # Desativa o cache para sempre ter o histórico mais recente
        )
        return [(row.sender, row.message_content) for index, row in df.iterrows()]
    except Exception as e:
        st.error(f"Erro ao carregar mensagens: {e}")
        return []

# --- 5. LÓGICA DA PÁGINA DE CHAT (INTERFACE DO USUÁRIO) ---

def pagina_chat():
    st.header("Bem-vindo ao DerivaAI! 🧠")

    # Inicializa a memória da conversa para a sessão atual
    memoria = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    # Carrega o histórico de mensagens do banco de dados e exibe na tela
    mensagens_salvas = carregar_mensagens(user_id)
    for tipo, conteudo in mensagens_salvas:
        # Adiciona a mensagem à memória do LangChain para manter o contexto
        if tipo == "user":
            memoria.chat_memory.add_user_message(conteudo)
        elif tipo == "ai":
            memoria.chat_memory.add_ai_message(conteudo)
        
        # Exibe a mensagem na interface do usuário
        with st.chat_message(tipo):
            st.markdown(conteudo)

    # Campo de entrada de texto do usuário
    prompt_usuario = st.chat_input("Como posso te ajudar com Cálculo?")
    if prompt_usuario:
        # Salva e exibe a mensagem do usuário
        salvar_mensagem(user_id, "user", prompt_usuario)
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        # Processa a pergunta e obtém a resposta da IA
        with st.spinner("DerivaAI está pensando..."):
            resposta = chain_memoria.invoke({'memoria': memoria.buffer, 'pergunta': prompt_usuario})
            resposta_texto = resposta.content
        
        # Salva e exibe a resposta da IA
        salvar_mensagem(user_id, "ai", resposta_texto)
        with st.chat_message("ai"):
            st.markdown(resposta_texto)

# --- FUNÇÃO PRINCIPAL ---

def main():
    load_css()
    pagina_chat()

if __name__ == "__main__":
    main()