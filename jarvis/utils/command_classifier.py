"""
Command classifier - Distinguishes between commands and casual chat using LLM.
Provides reliable routing without deviation.
"""
from typing import Tuple, Optional
from jarvis.utils.logger import setup_logger
from jarvis.config import (
    USE_GROQ, USE_OPENROUTER, USE_GEMINI,
    GROQ_API_KEY, GROQ_MODEL,
    OPENROUTER_API_KEY, OPENROUTER_MODEL,
    GEMINI_API_KEY, GEMINI_MODEL
)

logger = setup_logger(__name__)


class CommandClassifier:
    """Classifies queries as commands or casual chat."""
    
    CLASSIFICATION_PROMPT = """You are a query classifier. Analyze the user query and determine if it's a COMMAND or CHAT.

COMMAND: Explicit request to do something (create, open, search, tell me, show, calculate, etc.)
CHAT: Casual conversation, questions, greetings, discussions (how are you, what's up, tell me about, etc.)

Respond ONLY with:
command: [short command name like: create_document, open_app, search_news, tell_joke, get_weather]
OR
chat: [your brief response if it's casual, or empty if you should just classify]

Examples:
Query: "Make a PDF on AI" -> command: create_pdf
Query: "Open Chrome" -> command: open_app
Query: "What's up?" -> chat: Not much, ready to help!
Query: "Tell me a joke" -> command: tell_joke
Query: "How's the weather in Pune?" -> command: get_weather
Query: "Hey JARVIS" -> chat: Hey! What can I do for you?
Query: "Create a presentation on climate change" -> command: create_presentation
"""
    
    def __init__(self):
        """Initialize the classifier."""
        self.client = None
        self.setup_client()
    
    def setup_client(self) -> None:
        """Setup LLM client (Groq > OpenRouter > Gemini)."""
        try:
            if USE_GROQ and GROQ_API_KEY:
                from groq import Groq
                self.client = ("groq", Groq(api_key=GROQ_API_KEY), GROQ_MODEL)
                logger.info("Classifier using Groq")
            elif USE_OPENROUTER and OPENROUTER_API_KEY:
                from openai import OpenAI
                self.client = (
                    "openrouter",
                    OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY),
                    OPENROUTER_MODEL
                )
                logger.info("Classifier using OpenRouter")
            elif USE_GEMINI and GEMINI_API_KEY:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.client = ("gemini", genai.GenerativeModel("gemini-pro"), None)
                logger.info("Classifier using Gemini")
            else:
                logger.warning("No LLM configured for classifier")
        except Exception as e:
            logger.error(f"Failed to setup classifier client: {e}")
    
    def classify(self, query: str) -> Tuple[str, str]:
        """Classify a query as command or chat.
        
        Args:
            query: User's input query
        
        Returns:
            Tuple of (type, value) where type is 'command' or 'chat'
            Example: ('command', 'create_pdf') or ('chat', 'Hey! How can I help?')
        """
        if not self.client:
            logger.debug("Classifier not initialized, defaulting to keyword matching")
            return self._keyword_fallback(query)
        
        try:
            client_type, client, model = self.client
            
            if client_type == "groq":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.CLASSIFICATION_PROMPT},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,  # Low temp for consistent classification
                    max_tokens=50
                )
                result = response.choices[0].message.content.strip()
            
            elif client_type == "openrouter":
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self.CLASSIFICATION_PROMPT},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,
                    max_tokens=50
                )
                result = response.choices[0].message.content.strip()
            
            elif client_type == "gemini":
                response = client.generate_content(
                    f"{self.CLASSIFICATION_PROMPT}\n\nQuery: {query}"
                )
                result = response.text.strip()
            
            # Parse result
            if result.startswith("command:"):
                command = result.split("command:")[1].strip().lower()
                return ("command", command)
            elif result.startswith("chat:"):
                chat_response = result.split("chat:")[1].strip()
                return ("chat", chat_response)
            else:
                logger.warning(f"Unexpected classifier output: {result}")
                return ("chat", "")
        
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return self._keyword_fallback(query)
    
    def _keyword_fallback(self, query: str) -> Tuple[str, str]:
        """Fallback classification using keywords."""
        query_lower = query.lower()
        
        command_keywords = [
            ("create", "create_"),
            ("make", "create_"),
            ("generate", "create_"),
            ("open", "open_app"),
            ("search", "search"),
            ("tell", "tell_"),
            ("play", "play_"),
            ("get", "get_"),
            ("show", "show_"),
            ("find", "search"),
            ("set", "set_"),
            ("turn", "turn_"),
        ]
        
        for keyword, action in command_keywords:
            if keyword in query_lower:
                return ("command", action)
        
        return ("chat", "")
