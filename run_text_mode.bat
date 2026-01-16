@echo off
REM TEXT MODE for JARVIS (type commands instead of speaking)
REM No microphone needed - perfect for testing!

echo Starting JARVIS in TEXT MODE...
cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment not found!
    echo.
    pause
    exit /b 1
)

REM Run JARVIS in text mode
.venv\Scripts\python.exe run_text_mode.py

pause
