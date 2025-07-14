#!/bin/bash
# Run the Natural Language to Pinecone Query Agent with uv

echo "🚀 Starting Natural Language to Pinecone Query Agent with uv"
echo "============================================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies with uv..."
source venv/bin/activate
uv pip install -r requirements.txt

# Run FastAPI app
echo "🌟 Starting FastAPI application..."
echo "📍 Access the app at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"
echo ""

python apps/fastapi_app.py
