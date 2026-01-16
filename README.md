# J.A.R.V.I.S
**Just A Rather Very Intelligent System**

I am trynna to be Iron man.

## Project Structure

```
Jarvis/
├── jarvis/                     # Main Python package (importable)
│   ├── __init__.py             # Makes the folder a package
│   ├── main.py                 # Entry point: starts listening loop + greeting
│   ├── config.py               # API keys, paths, constants, voice settings
│   ├── settings.py             # User preferences (wake word, language, voice speed, etc.)
│   │
│   ├── core/                   # Heart of the assistant
│   │   ├── __init__.py
│   │   ├── speech.py           # STT (speech recognition) + TTS (text-to-speech)
│   │   ├── listener.py         # Wake-word detection + command recording
│   │   ├── brain.py            # Command parser / LLM integration / decision making
│   │   └── response.py         # Formatting + speaking replies
│   │
│   ├── skills/                 # Individual features / commands (modular!)
│   │   ├── __init__.py
│   │   ├── basic.py            # time, joke, wikipedia, exit
│   │   ├── web.py              # open youtube/google, play song (pywhatkit)
│   │   ├── system.py           # shutdown, screenshot, volume (pyautogui + os)
│   │   ├── scrape.py           # BeautifulSoup + requests (gold price, news, weather)
│   │   ├── browser.py          # Selenium tasks (login, search jobs, fill forms)
│   │   └── custom.py           # Your own new skills (Spotify, email, reminders…)
│   │
│   ├── utils/                  # Helper functions used everywhere
│   │   ├── __init__.py
│   │   ├── audio.py            # Record/play sound (pyaudio/sounddevice)
│   │   ├── logger.py           # Logging setup
│   │   ├── paths.py            # Project paths, user folders
│   │   └── helpers.py          # date formatting, string cleaning, etc.
│   │
│   └── resources/              # Non-code assets
│       ├── sounds/             # wake-up chime, error sound, etc. (.wav)
│       └── voices/             # If using local TTS → model files or cache
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   └── test_speech.py          # Example: test TTS/STT stubs
│
├── data/                       # Persistent data (optional)
│   ├── memory.json             # Conversation history / short-term memory
│   └── known_faces/            # If you add face recognition later
│
├── .env                        # Secrets: API keys (Groq, OpenAI, ElevenLabs…)
├── .gitignore                  # Ignore venv, __pycache__, .env, etc.
├── requirements.txt            # pip freeze > requirements.txt
├── README.md                   # This file
└── run.bat                     # Windows: quick double-click launcher
```

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - The `.env` file is already created with Gemini API configuration
   - Your Gemini API key is already configured
   - You can change `GEMINI_MODEL` in `.env` to use different models:
     - `gemini-1.5-flash` (fast, recommended)
     - `gemini-1.5-pro` (more capable)
     - `gemini-pro` (older version)
   - Optional: Add API keys for Groq/OpenAI if you want to use them instead

## Running JARVIS

### Windows
- Double-click `run.bat`, or
- Run: `python -m jarvis.main`

### Linux/Mac
```bash
python -m jarvis.main
```

## Features

- 🎤 **Voice Recognition**: Wake-word detection and command recording
- 🧠 **AI Brain**: LLM integration for intelligent responses
- 🔊 **Text-to-Speech**: Natural voice responses
- 🌐 **Web Skills**: Open websites, play music, search
- 💻 **System Control**: Screenshots, volume control, shutdown
- 📊 **Web Scraping**: Get news, weather, gold prices
- 🤖 **Browser Automation**: Selenium-based tasks
- 🔧 **Modular Skills**: Easy to add new capabilities

## Development

This is a modular project. Add new skills by creating functions in the `jarvis/skills/` directory.

## License

Personal project - feel free to use and modify!
