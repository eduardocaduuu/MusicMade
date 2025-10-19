#!/usr/bin/env bash
# Render start script for backend

set -e

echo "Starting MusicMade Backend..."

# Run database migrations if needed
# python -m alembic upgrade head

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
