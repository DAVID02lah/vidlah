@echo off
REM AI Trading Overlay System - Quick Start Script for Windows

echo 🚀 AI Trading Overlay System - Quick Start
echo ========================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install Python dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️ Creating environment file...
    copy .env.example .env
    echo 🔑 Please edit .env file with your API keys!
)

REM Install Node.js dependencies
if exist "package.json" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Create necessary directories
mkdir data 2>nul
mkdir models 2>nul
mkdir logs 2>nul

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python main.py (to start backend)
echo 3. Run: npm start (to start frontend)
echo.
echo See ACTION_PLAN.md for detailed instructions.

pause
