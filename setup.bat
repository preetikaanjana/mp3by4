@echo off
echo 🚀 MP3by4 Chrome Extension Setup
echo =================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing Python dependencies...
cd mp3by4
pip install -r requirements.txt
cd ..

echo.
echo ✅ Setup completed!
echo.
echo 📋 Next steps:
echo 1. Edit mp3by4\simple_working_server.py and add your Gemini API key
echo 2. Run start_server.bat to start the server
echo 3. Load the extension in Chrome: chrome://extensions/ -^> Load unpacked -^> select 'extension' folder
echo.
pause
