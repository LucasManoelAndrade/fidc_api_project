FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar libs
RUN pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY . .

# Porta do Flask
EXPOSE 5000

# Start
CMD ["python", "main.py"]
