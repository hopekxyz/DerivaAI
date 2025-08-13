import streamlit as st
import sqlite3
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate

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
    st.header("Bem-vindo ao DerivaAI 🧠", divider=True)

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
        chat = st.chat_message(tipo)
        chat.markdown(conteudo)
        if tipo == "user":
            memoria.chat_memory.add_user_message(conteudo)
        elif tipo == "ai":
            memoria.chat_memory.add_ai_message(conteudo)

    # Aqui, o campo de entrada do usuário
    prompt = st.chat_input("Como posso te ajudar?")
    if prompt:
        # Mostro a mensagem do usuário na janela:
        st.chat_message("user").markdown(prompt)
        salvar_mensagem("user", prompt)
        memoria.chat_memory.add_user_message(prompt)

        # E aqui, escrevo em tempo real na janela também.
        chat = st.chat_message("ai")
        resposta = chat.write_stream(chain_memoria.stream({'memoria': memoria.buffer, 'pergunta': prompt}))
        salvar_mensagem("ai", resposta)
        memoria.chat_memory.add_ai_message(resposta)

# Executa a função principal
def main():
    pagina_chat()

if __name__ == "__main__":
    main()
