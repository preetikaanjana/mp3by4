@echo off
echo 🚀 Starting MP3by4 Server...
echo.
set PYTHONIOENCODING=utf-8
call .venv\Scripts\activate.bat
cd mp3by4
python simple_working_server.py
pause
