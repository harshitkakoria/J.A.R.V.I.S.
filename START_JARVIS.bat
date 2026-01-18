@echo off
REM JARVIS Launcher - Automatically activates virtual environment
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Virtual environment activated ✓
echo Starting JARVIS...
python jarvis/main.py
pause
