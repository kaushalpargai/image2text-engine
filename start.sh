#!/bin/sh
set -e

WORKERS=${GUNICORN_WORKERS:-1}
PORT=${IMAGE2TEXT_PORT:-8000}

if [ "$APP_ENV" = "production" ]; then
    echo "Starting in PRODUCTION mode with Gunicorn ($WORKERS workers)..."
    exec gunicorn main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:$PORT \
        --timeout 600 \
        --graceful-timeout 600 \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting in DEVELOPMENT mode..."
    exec python main.py
fi
