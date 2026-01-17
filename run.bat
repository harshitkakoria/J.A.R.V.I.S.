@echo off
REM Quick launcher for JARVIS on Windows
REM Double-click this file to start JARVIS

echo.
echo ========================================
echo JARVIS - Voice Mode
echo ========================================
echo.
echo HOW TO USE:
echo 1. JARVIS will greet you
echo 2. Speak your command directly (no wake word needed)
echo 3. Wait for the response
echo 4. Say "goodbye" to exit
echo.
echo Example commands:
echo - "What time is it?"
echo - "Tell me a joke"
echo - "What's the weather?"
echo - "Open Google"
echo - "Who is Albert Einstein?"
echo - "Take a screenshot"
echo.
echo Press Ctrl+C anytime to stop
echo.

cd /d "%~dp0"

REM Check if .venv exists
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Run JARVIS and capture errors
.venv\Scripts\python.exe -m jarvis.main

echo.
echo JARVIS has shut down.
pause
if errorlevel 1 (
    echo.
    echo ERROR: JARVIS encountered an error (see above for details)
    echo.
)

pause

