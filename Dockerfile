FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

# Copiar código fuente
COPY . .

# Crear directorios y permisos
RUN mkdir -p staticfiles media data && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod +x /app/entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
