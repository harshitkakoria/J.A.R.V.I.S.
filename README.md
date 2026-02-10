# J.A.R.V.I.S v2.0
**Simple, Fast Voice Assistant - Talks & Remembers**

## About
**J.A.R.V.I.S v2.5** is a high-speed, voice-activated AI assistant designed for Windows. 
It uses **Groq (Llama 3)** for intelligence, **Selenium** for eyes, and **Python** for system control.

- **� Ultra-Fast**: Powered by Groq's LPU.
- **⚡ Real-time**: Live news, stocks, and weather.
- **✨ Talks back**: Natural voice response (Edge-TTS).
- **🧠 Remembers**: Context-aware memory of past conversations.

## Features
✅ **Basic**: time, date, jokes, exit
✅ **Web**: Google search, open websites
✅ **YouTube**: play videos (auto-play), search
✅ **Apps**: open/close ANY app (fuzzy match, shortcuts, Store apps, PWAs)
✅ **System**: screenshot, volume, brightness, clipboard manager
✅ **Media**: global play/pause, next/prev track control
✅ **Monitoring**: CPU, RAM, battery status
✅ **Weather**: current weather (free API)
✅ **Files**: create Word/PDF/PowerPoint, delete, list, folder search
✅ **Real-time AI**: news headlines, gold prices, stocks, weather (via Groq/Llama 3)
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

Apps (Powered by AppOpener):
- "open spotify" (launches native app)
- "open sptfy" (autocorrects typo)
- "close spotify"

System & Media:
- "take a screenshot"
- "volume up" / "mute"
- "play music" / "pause" / "next track"
- "cpu usage" / "battery status"
- "read clipboard" / "clear clipboard"

Weather:
- "what's the weather"
- "temperature"

Files:
- "create word document"
- "create pdf"
- "list files"
- "find my 'Resume' folder"
- "delete file confirm"

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
│   ├── brain.py       # Routing + memory
│   ├── listener.py    # Selenium STT
│   └── llm.py         # Groq Integration
├── skills/
│   ├── basic.py       # time, date, jokes
│   ├── web.py         # search, websites
│   ├── youtube.py     # play, search
│   ├── apps.py        # open/close
│   ├── system.py      # screenshot, volume, media, clipboard, status
│   ├── weather.py     # current weather
│   └── file_manager.py# create docs, delete, list, search folders
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
   - The `.env` file should contain:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - (Optional) `OPENAI_API_KEY` if you use OpenAI handlers.

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
