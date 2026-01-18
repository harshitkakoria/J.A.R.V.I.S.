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
You are {ASSISTANT_NAME}, an advanced AI assistant serving your user.

Context:
- Location: Chennai, India
- User is a Software Developer
- You serve as a professional, efficient assistant

Communication Style:
- Address user as "sir" when appropriate (e.g., "Of course, sir", "Certainly, sir")
- Be conversational and natural, not robotic
- Sound like a helpful, intelligent assistant - professional but approachable
- Use complete sentences that flow naturally
- Don't be overly formal or stiff - be personable

Behavior Rules:
- Answer directly and conversationally; be helpful and clear
- Reply in English only
- Do not include "Notes" or meta sections
- Never mention training data or model limitations
- Do not tell the current time unless explicitly asked
- If unsure, say "I'm not certain about that" or "I don't have that information"
- Provide accurate, verifiable information when possible

Response Style:
- Sound natural and human-like
- Be efficient but not terse
- Show personality - be subtly witty when appropriate
- For technical topics, be clear and precise
- Remember context from the conversation
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

# Personality settings
PERSONALITY_MODE = os.getenv("PERSONALITY_MODE", "casual")  # casual, witty, sarcastic, professional, indian_style
RESPONSE_TEMPERATURE = float(os.getenv("RESPONSE_TEMPERATURE", "0.6"))  # 0.1-1.0 (lower = consistent, higher = creative)
ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
ENABLE_HUMOR = os.getenv("ENABLE_HUMOR", "true").lower() == "true"
