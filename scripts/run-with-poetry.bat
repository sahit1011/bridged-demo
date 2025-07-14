@echo off
REM Run the Natural Language to Pinecone Query Agent with Poetry (Windows)

echo 🎭 Starting Natural Language to Pinecone Query Agent with Poetry
echo ================================================================

REM Set Poetry path
set POETRY_PATH=%USERPROFILE%\AppData\Roaming\Python\Scripts\poetry.exe

REM Check if Poetry is installed
if not exist "%POETRY_PATH%" (
    echo ❌ Poetry is not installed. Installing Poetry...
    echo 📦 Installing Poetry globally...
    powershell -c "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    if not exist "%POETRY_PATH%" (
        echo ❌ Poetry installation failed. Please install manually:
        echo    powershell -c "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
        pause
        exit /b 1
    )
    echo ✅ Poetry installed successfully!
)

REM Install dependencies with Poetry
echo 📦 Installing dependencies with Poetry...
"%POETRY_PATH%" install --no-root

REM Run FastAPI app
echo 🌟 Starting FastAPI application...
echo 📍 Access the app at: http://localhost:8000
echo 📚 API docs at: http://localhost:8000/docs
echo 🔍 Health check at: http://localhost:8000/health
echo.

"%POETRY_PATH%" run python fastapi_app.py
