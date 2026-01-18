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
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "allenai/molmo-2-8b:free")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

# LLM Configuration - Groq Free Tier (Primary)
USE_OPENROUTER = os.getenv("USE_OPENROUTER", "false").lower() == "true"
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() == "true"
USE_GROQ = os.getenv("USE_GROQ", "true").lower() == "true"
USE_COHERE = os.getenv("USE_COHERE", "true").lower() == "true"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Free models: llama-3.3-70b-versatile, llama-3.2-90b-vision-preview
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-v1:7k-token-free-trial")  # Free trial model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

# Assistant/User naming (from .env)
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "JARVIS")
USER_NAME = os.getenv("USER_NAME", "Sir")

# JARVIS System Prompt (concise, English-only, no time unless asked, no notes/training data)
JARVIS_SYSTEM_PROMPT = f"""
Hello, I am {USER_NAME}. You are a very accurate and advanced AI chatbot named {ASSISTANT_NAME}.

Behavior Rules:
- Answer directly and concisely; avoid overexplaining.
- Reply in English only, even if the input is in another language.
- Do not include "Notes" or meta sections; just provide the answer.
- Never mention training data, model internals, or limitations unless explicitly asked.
- Do not tell the current time unless the user explicitly asks for it.
- If the user asks for up-to-date information, prefer accurate, verifiable facts. When appropriate, you may suggest using web/search capabilities.
- If unsure, say "I don't know" rather than guessing.

Style:
- Polite, efficient, subtly witty when appropriate; serious and clear for technical topics.
"""

# Real-Time Search System Prompt (for web search refinement with proper grammar)
REALTIME_SEARCH_PROMPT = f"""Hello, I am {USER_NAME}. You are a very accurate and advanced AI chatbot named {ASSISTANT_NAME} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Speech Recognition (Selenium Web Speech API only)
# No additional config needed - language is set via STT_INPUT_LANGUAGE in .env

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
