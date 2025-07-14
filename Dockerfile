FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://get.docker.com | bash

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY . .

RUN pip install --no-cache-dir -e .

ENV PORT=8000 \
    HOST=0.0.0.0 \
    DEBUG=false

# Expose port
EXPOSE 8000

CMD alembic upgrade head && python -m scripts.run_seeders && uvicorn src.main:app --host $HOST --port $PORT 