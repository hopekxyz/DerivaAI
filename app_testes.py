import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate
import psycopg2
from streamlit import session_state as ss

# Configurações de conexão para o PostgreSQL.
# Agora, elas serão lidas exclusivamente das variáveis de ambiente.
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

def get_db_connection():
    """Função para conectar ao banco de dados PostgreSQL."""
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def setup_database():
    """Função para criar a tabela de mensagens e usuários se não existir."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            subscription_status TEXT NOT NULL,
            free_interactions_left INTEGER DEFAULT 0,
            last_interaction_date TIMESTAMP WITH TIME ZONE
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# --- INÍCIO DA MODIFICAÇÃO ---

def create_or_get_user(user_id):
    """
    Verifica se um usuário existe. Se não existir, o cria com o status 'free'.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Verifica se o usuário já existe
    cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        # Se o usuário não existe, o cria com o status 'free'
        cur.execute(
            "INSERT INTO users (user_id, subscription_status, free_interactions_left) VALUES (%s, %s, %s)",
            (user_id, 'free', 10) # 10 interações grátis para teste
        )
        conn.commit()
    
    conn.close()

# --- FIM DA MODIFICAÇÃO ---

def save_message(user_id, tipo, conteudo):
    """Função para salvar uma mensagem no banco de dados."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_id, type, content) VALUES (%s, %s, %s)",
        (user_id, tipo, conteudo)
    )
    conn.commit()
    conn.close()

def load_messages(user_id):
    """Função para carregar o histórico de mensagens de um usuário."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT type, content FROM messages WHERE user_id = %s ORDER BY timestamp", (user_id,))
    mensagens = cur.fetchall()
    conn.close()
    return mensagens

# --- CHAVE DE API PARA TESTE LOCAL ---
# ATENÇÃO: Esta chave deve ser removida para a produção e substituída por um segredo.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("A chave de API da OpenAI não foi encontrada.")
    st.stop()


# Aqui, é uma interface PROTÓTIPO de memória de usuários baseada no id, onde vou usar session_state + propelauth para adicionar.
user_id = "1"

# Configuração da página
st.set_page_config(
    page_title="DerivaAI",
    page_icon="🧠",
    layout="wide"
)

# Carregar CSS personalizado
def load_css():
    with open('style.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inicialmente, eu importo o prompt que será utilizado:
with open('prompt_revisado.txt', 'r', encoding='utf-8') as f:
    prompt = f.read().replace("{", "{{").replace("}", "}}")

# Aqui, importo bibliotecas e inicializo o chat.
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# Crio o template com memória:
template = ChatPromptTemplate.from_messages([
    ('placeholder', '{memoria}'),
    ('system', prompt),
    ('human', '{pergunta}')
])
chain_memoria = template | llm

# A função principal do chatbot
def pagina_chat():
    # Aqui, defino um cabeçalho pro chat
    st.header("Bem-vindo ao DerivaAI! 🧠")

    # Aqui, crio a tabela no banco se ainda não existir
    setup_database()

    # --- INÍCIO DA MODIFICAÇÃO ---
    # Garante que o usuário exista na tabela antes de prosseguir
    create_or_get_user(user_id)
    # --- FIM DA MODIFICAÇÃO ---

    # Inicializa a memória da conversa no session_state do Streamlit
    if "memoria" not in ss:
        ss.memoria = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=1000,
            return_messages=True
        )
        # Carrega as mensagens salvas na memória da sessão
        mensagens_salvas = load_messages(user_id)
        for tipo, conteudo in mensagens_salvas:
            if tipo == "user":
                ss.memoria.chat_memory.add_user_message(conteudo)
            elif tipo == "ai":
                ss.memoria.chat_memory.add_ai_message(conteudo)

    # Exibe as mensagens do histórico no chat
    for tipo, conteudo in load_messages(user_id):
        if tipo == "user":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
                <div style="background: #1E3A8A; color: white; padding: 12px 20px; border-radius: 16px 16px 0 16px; max-width: 70%; word-break: break-word; box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif tipo == "ai":
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
                <div style="background: transparent; color: white; padding: 12px 20px; border-radius: 16px 16px 16px 0; max-width: 70%; word-break: break-word;">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Aqui, o campo de entrada do usuário
    prompt = st.chat_input("Como posso te ajudar?")
    if prompt:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
            <div style="background: #1E3A8A; color: white; padding: 12px 20px; border-radius: 16px 16px 0 16px; max-width: 70%; word-break: break-word; box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);">
                {prompt}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        save_message(user_id, "user", prompt)
        ss.memoria.chat_memory.add_user_message(prompt)

        with st.spinner("DerivaAI está pensando..."):
            resposta = chain_memoria.invoke({'memoria': ss.memoria.buffer, 'pergunta': prompt})
            resposta_texto = resposta.content
            
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
                <div style="background: transparent; color: white; padding: 12px 20px; border-radius: 16px 16px 16px 0; max-width: 70%; word-break: break-word;">
                    {resposta_texto}
                </div>
            </div>
            """, unsafe_allow_html=True)
            save_message(user_id, "ai", resposta_texto)
            ss.memoria.chat_memory.add_ai_message(resposta_texto)

# Executa a função principal
def main():
    load_css()
    pagina_chat()

if __name__ == "__main__":
    main()
