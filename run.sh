#!/bin/bash
# Fieldcraft Backend Startup Script

echo "🚀 Starting Fieldcraft Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your actual API keys and database URL"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
