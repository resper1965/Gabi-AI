# Backend Dockerfile - Gabi AI Agent
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/uploads

# Make scripts executable
RUN chmod +x scripts/init-database.py && \
    chmod +x scripts/run_seeders.py

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Starting Gabi AI Backend..."\n\
\n\
# Wait for database to be ready\n\
echo "⏳ Waiting for database connection..."\n\
until pg_isready -h $(echo $POSTGRES_CONNECTION_STRING | sed -n "s/.*@\\([^:]*\\):.*/\\1/p") -p 5432; do\n\
  echo "Database not ready, waiting..."\n\
  sleep 2\n\
done\n\
\n\
echo "✅ Database connection established"\n\
\n\
# Initialize database\n\
echo "🗄️ Initializing database..."\n\
python scripts/init-database.py\n\
\n\
# Run seeders\n\
echo "🌱 Running seeders..."\n\
python -m scripts.run_seeders\n\
\n\
# Start application\n\
echo "🚀 Starting FastAPI application..."\n\
exec uvicorn src.main:app --host $HOST --port $PORT --workers 1 --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["/app/start.sh"] 