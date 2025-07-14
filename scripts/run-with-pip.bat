@echo off
REM Run the Natural Language to Pinecone Query Agent with pip (Windows)

echo 🐍 Starting Natural Language to Pinecone Query Agent with pip
echo ===========================================================

REM Check if Python is installed
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv-pip" (
    echo 📦 Creating virtual environment...
    python -m venv venv-pip
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .\venv-pip\Scripts\activate

REM Upgrade pip and install dependencies
echo 📦 Installing dependencies with pip...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Run FastAPI app
echo 🌟 Starting FastAPI application...
echo 📍 Access the app at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo 🔍 Health check at: http://localhost:8000/health
echo.

python fastapi_app.py
