#!/bin/bash
# Run the Natural Language to Pinecone Query Agent with pip (Unix/Linux/Mac)

echo "🐍 Starting Natural Language to Pinecone Query Agent with pip"
echo "==========================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install dependencies
echo "📦 Installing dependencies with pip..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Run FastAPI app
echo "🌟 Starting FastAPI application..."
echo "📍 Access the app at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo "🔍 Health check at: http://localhost:8000/health"
echo

python apps/fastapi_app.py
