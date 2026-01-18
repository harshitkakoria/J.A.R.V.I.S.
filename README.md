# J.A.R.V.I.S v2.0
**Simple, Fast Voice Assistant - Talks & Remembers**

## What Changed in v2.0?
- **91% code reduction** (152KB → 14KB)
- **All features working** - nothing removed
- **✨ Talks back** - TTS with edge-tts (natural voice)
- **✨ Remembers conversations** - tracks last 10 exchanges
- **✨ Knows your name** - personalized responses
- **No complex interactions** - each skill is independent
- **No duplicate functions** - clean, single implementation
- **Simple error handling** - fails fast, no nested try-catch
- **Fast startup** - instant response

## Features
✅ **Basic**: time, date, jokes, exit
✅ **Web**: Google search, open websites
✅ **YouTube**: play videos (auto-play), search
✅ **Apps**: open/close apps, Chrome PWAs, Start Menu apps, web fallback
✅ **System**: screenshot, volume control
✅ **Weather**: current weather (free API)
✅ **Files**: create Word/PDF/PowerPoint, delete, list
✅ **Scrape**: news headlines, gold prices, stocks
✅ **Memory**: remembers conversations, your name, context

## Quick Start
```bash
# Text mode (recommended for testing)
python run_text_mode.py

# Voice mode (speaks back)
python -m jarvis.main
```

## Commands
```
Conversation & Memory:
- "my name is [name]"
- "hello" (will use your name)
- "what did I say"
- "remember" (shows conversation history)
- "thanks" / "thank you"

Basic:
- "what time is it"
- "tell me a joke"
- "who are you"

Web:
- "search for python tutorials"
- "open github"

YouTube:
- "play relaxing music"
- "search youtube for tutorials"

Apps (now with PWA support):
- "open chatgpt"
- "open chrome"
- "open notepad"
- "close chrome"

System:
- "take a screenshot"
- "volume up"
- "mute"

Weather:
- "what's the weather"
- "temperature"

Files:
- "create word document"
- "create pdf"
- "create presentation"
- "list files"
- "delete file confirm"

Scrape:
- "latest news"
- "gold price"
- "stock market"

Exit:
- "exit" (will say goodbye with your name)
- "quit"
- "bye"
```

## Memory System
JARVIS now remembers:
- ✅ Your name (introduce yourself: "my name is...")
- ✅ Last 10 conversations
- ✅ What you asked recently
- ✅ Context for personalized responses

Example:
```
You: my name is Harshit
JARVIS: Nice to meet you, Harshit! How can I help you today?

You: hello
JARVIS: Hello Harshit! How can I help?

You: what did I say
JARVIS: You asked: 'hello'
```

## Architecture
```
jarvis/
├── core/
│   ├── brain.py       # 80 lines - routing + memory
│   ├── listener.py    # 60 lines - Selenium STT
│   └── speech.py      # 30 lines - edge-tts
├── skills/
│   ├── basic.py       # time, date, jokes
│   ├── web.py         # search, websites
│   ├── youtube.py     # play, search (pywhatkit)
│   ├── apps.py        # open/close (Start Menu + PWA + web fallback)
│   ├── system.py      # screenshot, volume
│   ├── weather.py     # current weather
│   ├── files.py       # create docs, delete, list
│   └── scrape.py      # news, gold, stocks
└── utils/
    ├── helpers.py     # text cleaning
    └── memory.py      # conversation tracking
```

## How It Works
1. **Listens** via Selenium STT (real-time)
2. **Brain** routes to skills + checks memory
3. **Skills** execute independently
4. **Memory** saves exchange automatically
5. **Speaks** response with edge-tts

## Dependencies
```bash
pip install selenium webdriver-manager edge-tts pywhatkit pyjokes psutil pyautogui python-dotenv requests beautifulsoup4 python-docx python-pptx reportlab pycaw
```

## Backup
Your old complex version is in `jarvis_backup/` folder
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
