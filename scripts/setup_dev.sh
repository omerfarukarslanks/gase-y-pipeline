#!/bin/bash
set -e

echo "=== Gase-Y Pipeline - Development Setup ==="

# Copy env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

# Start infrastructure
echo "Starting PostgreSQL and Redis..."
docker compose up -d db redis

# Wait for DB
echo "Waiting for PostgreSQL..."
sleep 3

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv .venv 2>/dev/null || true
source .venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
alembic upgrade head

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install

cd ..

echo ""
echo "=== Setup complete! ==="
echo "Run the following commands in separate terminals:"
echo "  make dev-backend    # Start FastAPI server"
echo "  make dev-frontend   # Start React dev server"
echo "  make dev-worker     # Start Celery worker"
