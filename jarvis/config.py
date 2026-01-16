"""
Configuration file for API keys, paths, constants, and voice settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# API Keys (from .env)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "google/gemma-3-27b-it:free")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# LLM Configuration
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "true").lower() == "true"
USE_TOGETHER = os.getenv("USE_TOGETHER", "false").lower() == "true"
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# Speech Recognition
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large
USE_WHISPER = os.getenv("USE_WHISPER", "true").lower() == "true"

# Paths
RESOURCES_DIR = PROJECT_ROOT / "jarvis" / "resources"
SOUNDS_DIR = RESOURCES_DIR / "sounds"
VOICES_DIR = RESOURCES_DIR / "voices"
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_FILE = DATA_DIR / "memory.json"
LOG_DIR = PROJECT_ROOT / "logs"

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
RECORD_SECONDS = 5  # Max recording duration

# Wake word settings
WAKE_WORD = "jarvis"  # Default, can be overridden in settings
WAKE_WORD_SENSITIVITY = 0.5
