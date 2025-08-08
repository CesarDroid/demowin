# --- Build stage ---
FROM python:3.12-slim AS build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# --- Runtime stage ---
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd -m appuser
COPY --from=build /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
# recopila estáticos (usa whitenoise)
RUN python manage.py collectstatic --noinput || true
USER appuser
EXPOSE 8000
CMD ["gunicorn","core.wsgi:application","--bind","0.0.0.0:8000","--workers","3","--timeout","120"]
