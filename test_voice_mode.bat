@echo off
REM Test JARVIS with voice input
REM This runs JARVIS in voice mode for testing

echo.
echo ========================================
echo JARVIS - Voice Mode Test
echo ========================================
echo.
echo To test:
echo 1. JARVIS will greet you
echo 2. Say "jarvis" to activate (or just skip the wake word)
echo 3. Ask a question like "What time is it?"
echo 4. Say "goodbye" to exit
echo.
echo Press Ctrl+C to stop anytime
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    pause
    exit /b 1
)

.venv\Scripts\python.exe -m jarvis.main
