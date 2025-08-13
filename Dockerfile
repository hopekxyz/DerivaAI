# Usa uma imagem oficial do Python como base.
# Escolhemos a versão 3.9 slim-buster porque é leve e contém apenas o essencial para Python.
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner.
# Todos os comandos subsequentes serão executados a partir deste diretório.
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho do contêiner.
# Fazemos isso antes de copiar o restante do código para que o Docker possa
# cachear esta camada. Se suas dependências não mudarem, a reconstrução será mais rápida.
COPY requirements.txt .

# Instala todas as bibliotecas Python listadas no requirements.txt.
# `--no-cache-dir` ajuda a manter o tamanho da imagem menor, não armazenando o cache do pip.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os outros arquivos do seu projeto (como app.py, prompt_revisado.txt, style.css)
# para o diretório de trabalho dentro do contêiner.
COPY . .

# Expõe a porta 8080.
# Isso informa ao Docker que a aplicação dentro do contêiner estará escutando nesta porta.
# O Google Cloud Run, que usaremos, espera que a aplicação escute na porta 8080.
EXPOSE 8080

# Define o comando que será executado quando o contêiner for iniciado.
# - `streamlit run app.py`: Inicia sua aplicação Streamlit.
#   (Lembre-se de que `app.py` deve ser o nome do seu arquivo principal do Streamlit)
# - `--server.port 8080`: Garante que o Streamlit use a porta 8080 dentro do contêiner.
# - `--server.address 0.0.0.0`: Permite que o Streamlit seja acessível de qualquer IP
#   dentro do contêiner, o que é crucial para que o serviço de nuvem possa alcançá-lo.
CMD ["streamlit", "run", "app_testes.py", "--server.port", "8080", "--server.address", "0.0.0.0", "--server.enableXsrfProtection", "false", "--server.baseUrlPath", "/", "--server.enableCORS", "true", "--server.headless", "true"]