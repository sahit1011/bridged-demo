@echo off
REM Run the Natural Language to Pinecone Query Agent with uv (Windows)

echo 🚀 Starting Natural Language to Pinecone Query Agent with uv
echo ============================================================

REM Set uv path
set UV_PATH=%USERPROFILE%\.local\bin\uv.exe

REM Check if uv is installed
if not exist "%UV_PATH%" (
    echo ❌ uv is not installed. Installing uv...
    echo 📦 Installing uv globally...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    timeout /t 3 /nobreak >nul
    if not exist "%UV_PATH%" (
        echo ❌ uv installation failed. Please install manually:
        echo    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        pause
        exit /b 1
    )
    echo ✅ uv installed successfully!
) else (
    echo ✅ uv found at: %UV_PATH%
)

REM Change to project root directory
cd /d "%~dp0\.."

REM Create virtual environment if it doesn't exist
if not exist "venv-uv" (
    echo 📦 Creating virtual environment with uv...
    "%UV_PATH%" venv venv-uv
)

REM Install dependencies with uv
echo 📦 Installing dependencies with uv...
"%UV_PATH%" pip install -r requirements.txt --python venv-uv\Scripts\python.exe

REM Run FastAPI app
echo 🌟 Starting FastAPI application...
echo 📍 Access the app at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo 🔍 Health check at: http://localhost:8000/health
echo.

REM Set PYTHONPATH and run the app
set PYTHONPATH=.
venv-uv\Scripts\python.exe apps/fastapi_app.py
