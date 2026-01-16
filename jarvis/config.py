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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# LLM Configuration
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"

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
