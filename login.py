import streamlit as st
import sqlite3
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate

# Aqui, é uma interface PROTÓTIPO de memória de usuários baseada no id, onde vou usar session_state + propelauth para adicionar.
config = {'configurable': {'session_id' : 'ivo'}}

# Configuração da página
st.set_page_config(
    page_title="DerivaAI",
    page_icon="🧠",
    layout="wide"
)

# Carregar CSS personalizado
def load_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inicialmente, eu importo o prompt que será utilizado:
with open('prompt_revisado.txt', 'r', encoding='utf-8') as f:
    prompt = f.read().replace("{", "{{").replace("}", "}}")

# Aqui, importo bibliotecas e inicializo o chat.
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
    api_key="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"
)

# Crio o template com memória:
template = ChatPromptTemplate.from_messages([
    ('placeholder', '{memoria}'),
    ('system', prompt),
    ('human', '{pergunta}')
])
chain_memoria = template | llm

# Aqui defino as funções para persistência em banco SQLite:
def criar_tabela():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mensagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            conteudo TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def salvar_mensagem(tipo, conteudo):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO mensagens (tipo, conteudo) VALUES (?, ?)", (tipo, conteudo))
    conn.commit()
    conn.close()

def carregar_mensagens():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT tipo, conteudo FROM mensagens ORDER BY id")
    mensagens = c.fetchall()
    conn.close()
    return mensagens

# A função principal do chatbot
def pagina_chat():
    # Aqui, defino um cabeçalho pro chat
    st.header("Bem-vindo ao DerivaAI! 🧠")

    # Aqui, crio a tabela no banco se ainda não existir
    criar_tabela()

    # E aqui, eu defino como a memória vai funcionar: Vai resumir o histórico de conversas, para ter o tamanho de até 1000 tokens.
    memoria = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=1000,
        return_messages=True
    )

    # Aqui é pra persistir com as mensagens já digitadas.
    mensagens_salvas = carregar_mensagens()
    for tipo, conteudo in mensagens_salvas:
        if tipo == "user":
            # Mensagem do usuário à direita
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
                <div style="background: #1E3A8A; color: white; padding: 12px 20px; border-radius: 16px 16px 0 16px; max-width: 70%; word-break: break-word; box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)
            memoria.chat_memory.add_user_message(conteudo)
        elif tipo == "ai":
            # Mensagem do bot à esquerda
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
                <div style="background: transparent; color: white; padding: 12px 20px; border-radius: 16px 16px 16px 0; max-width: 70%; word-break: break-word;">
                    {conteudo}
                </div>
            </div>
            """, unsafe_allow_html=True)
            memoria.chat_memory.add_ai_message(conteudo)

    # Aqui, o campo de entrada do usuário
    prompt = st.chat_input("Como posso te ajudar?")
    if prompt:
        # Mostro a mensagem do usuário na janela (à direita):
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
            <div style="background: #1E3A8A; color: white; padding: 12px 20px; border-radius: 16px 16px 0 16px; max-width: 70%; word-break: break-word; box-shadow: 0 2px 8px 0 rgba(0,0,0,0.10);">
                {prompt}
            </div>
        </div>
        """, unsafe_allow_html=True)
        salvar_mensagem("user", prompt)
        memoria.chat_memory.add_user_message(prompt)

        # E aqui, escrevo em tempo real na janela também (à esquerda):
        with st.spinner("DerivaAI está pensando..."):
            resposta = chain_memoria.invoke({'memoria': memoria.buffer, 'pergunta': prompt}, config = config)
            resposta_texto = resposta.content
            
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 1rem;">
                <div style="background: transparent; color: white; padding: 12px 20px; border-radius: 16px 16px 16px 0; max-width: 70%; word-break: break-word;">
                    {resposta_texto}
                </div>
            </div>
            """, unsafe_allow_html=True)
            salvar_mensagem("ai", resposta_texto)
            memoria.chat_memory.add_ai_message(resposta_texto)

# Executa a função principal
def main():
    load_css()
    pagina_chat()

if __name__ == "__main__":
    main()
