# Use Python 3.14 como base
FROM python:3.14

# Defina variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configure o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instale dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie o arquivo requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação
COPY . .

# Crie o diretório de logs
RUN mkdir -p /app/logs && \
    chmod -R 755 /app/logs

# Defina o comando padrão
CMD ["python", "main.py"]

