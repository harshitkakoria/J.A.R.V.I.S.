@echo off
REM Demo mode for JARVIS (no microphone needed)
REM This simulates commands for testing

echo Starting JARVIS in DEMO MODE (no microphone needed)...
cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Run JARVIS in demo mode
.venv\Scripts\python.exe -c "from jarvis.settings import UserSettings; from jarvis.core.speech import SpeechEngine; from jarvis.core.response import ResponseHandler; settings = UserSettings.load(); engine = SpeechEngine(rate=settings.voice_rate, volume=settings.voice_volume, voice_id=settings.voice_id); handler = ResponseHandler(engine); handler.respond(f'Hello {settings.name}, I am JARVIS. Ready for testing.'); handler.respond('Test message: The bot is working!')"

pause
