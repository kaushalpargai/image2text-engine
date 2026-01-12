#!/bin/bash
set -e

# If GUNICORN_WORKERS is not set, default to 1 (safe default)
# In production, you might set this higher (e.g., 2-4) via env var
WORKERS=${GUNICORN_WORKERS:-1}
PORT=${IMAGE2TEXT_PORT:-8000}

if [ "$APP_ENV" = "production" ]; then
    echo "Starting in PRODUCTION mode with Gunicorn ($WORKERS workers)..."
    # Timeout set to 120s for long OCR jobs
    exec gunicorn main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$PORT \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting in DEVELOPMENT mode with source reload..."
    # Config is read from main.py which uses IMAGE2TEXT_PORT env var
    exec python main.py
fi
