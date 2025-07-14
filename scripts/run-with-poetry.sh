#!/bin/bash
# Run the Natural Language to Pinecone Query Agent with Poetry

echo "🎭 Starting Natural Language to Pinecone Query Agent with Poetry"
echo "================================================================"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
poetry install --no-root

# Run FastAPI app
echo "🌟 Starting FastAPI application..."
echo "📍 Access the app at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"
echo ""

poetry run python fastapi_app.py
