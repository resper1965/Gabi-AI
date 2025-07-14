FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs /app/static

# Make scripts executable
RUN chmod +x scripts/init-database.py

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Gabi AI Backend..."\n\
\n\
echo "Initializing database..."\n\
python scripts/init-database.py\n\
\n\
echo "Running seeders..."\n\
python -m scripts.run_seeders\n\
\n\
echo "Starting application..."\n\
exec uvicorn src.main:app --host $HOST --port $PORT --workers 1\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["/app/start.sh"] 