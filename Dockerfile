FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
        default-libmysqlclient-dev \
        python3-dev \
        # Dependências para unstructured
        pandoc \
        poppler-utils \
        tesseract-ocr \
        libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Instalar pip e atualizar setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar poetry
RUN pip install --no-cache-dir poetry==1.4.2

# Copiar arquivos de dependência
COPY pyproject.toml poetry.lock* ./

# Configurar poetry e instalar dependências
RUN poetry config virtualenvs.create false \
    && poetry add langchain-community langchain-openai unstructured \
    && poetry install --no-interaction --no-ansi

# Copiar o código
COPY . .

# Expor a porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]