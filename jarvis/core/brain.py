"""
Command parser, LLM integration, and decision making.
"""
from typing import Dict, Callable, Optional
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import extract_keywords, clean_text
from jarvis.config import USE_OLLAMA, USE_GROQ, OLLAMA_BASE_URL, OLLAMA_MODEL, GROQ_API_KEY

logger = setup_logger(__name__)


class Brain:
    """Command dispatcher with keyword matching and LLM fallback."""
    
    def __init__(self):
        """Initialize brain with skill mappings."""
        self.skills: Dict[str, Callable[[str], Optional[str]]] = {}
        self.keyword_map: Dict[str, str] = {}  # keyword -> skill_name
        logger.info("Brain initialized")
    
    def register_skill(self, skill_name: str, handler: Callable[[str], Optional[str]], keywords: list):
        """
        Register a skill with its handler and keywords.
        
        Args:
            skill_name: Name of the skill
            handler: Function that handles the command
            keywords: List of keywords that trigger this skill
        """
        self.skills[skill_name] = handler
        for keyword in keywords:
            self.keyword_map[keyword.lower()] = skill_name
        logger.debug(f"Registered skill '{skill_name}' with keywords: {keywords}")
    
    def process(self, query: str) -> Optional[str]:
        """
        Process user query and return response.
        
        Args:
            query: User's spoken command
            
        Returns:
            Response text or None
        """
        if not query:
            return None
        
        query_clean = clean_text(query)
        logger.info(f"Processing query: {query_clean}")
        
        # Try keyword matching first
        matched_keywords = extract_keywords(query_clean, list(self.keyword_map.keys()))
        
        if matched_keywords:
            # Get the skill for the first matched keyword
            skill_name = self.keyword_map[matched_keywords[0].lower()]
            handler = self.skills.get(skill_name)
            
            if handler:
                try:
                    logger.debug(f"Executing skill '{skill_name}'")
                    response = handler(query_clean)
                    return response
                except Exception as e:
                    logger.error(f"Error executing skill '{skill_name}': {e}")
                    return f"Sorry, I encountered an error: {str(e)}"
        
        # Fallback to LLM
        logger.debug("No keyword match, trying LLM fallback")
        return self._llm_fallback(query_clean)
    
    def _llm_fallback(self, query: str) -> Optional[str]:
        """
        Use LLM to generate response when no skill matches.
        
        Args:
            query: User query
            
        Returns:
            LLM-generated response
        """
        try:
            if USE_OLLAMA:
                return self._query_ollama(query)
            elif USE_GROQ:
                return self._query_groq(query)
            else:
                logger.warning("No LLM configured, returning default response")
                return "I'm not sure how to help with that. Could you rephrase?"
        except Exception as e:
            logger.error(f"LLM fallback error: {e}")
            return "I'm having trouble understanding. Could you try again?"
    
    def _query_ollama(self, query: str) -> Optional[str]:
        """Query Ollama LLM using chat API (better for instruction-tuned models)."""
        try:
            import requests
            
            # Use chat API for instruction-tuned models
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are JARVIS, a helpful AI assistant inspired by Iron Man. Respond concisely and naturally."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "stream": False
                },
                timeout=30  # Increased timeout for larger models
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("message", {})
                return message.get("content", "I'm not sure how to help with that.")
            else:
                error_text = response.text
                logger.error(f"Ollama API error: {response.status_code} - {error_text}")
                # Try fallback to generate API if chat fails
                return self._query_ollama_generate_fallback(query)
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Make sure Ollama is running.")
            return "I cannot connect to my AI brain. Please make sure Ollama is running."
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "The request took too long. Please try again."
        except ImportError:
            logger.error("requests library not available for Ollama")
            return None
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return None
    
    def _query_ollama_generate_fallback(self, query: str) -> Optional[str]:
        """Fallback to generate API if chat API fails."""
        try:
            import requests
            
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": f"You are JARVIS, a helpful AI assistant. Respond concisely to: {query}",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "I'm not sure how to help with that.")
            else:
                logger.error(f"Ollama generate API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Ollama generate fallback error: {e}")
            return None
    
    def _query_groq(self, query: str) -> Optional[str]:
        """Query Groq LLM."""
        try:
            from groq import Groq
            
            if not GROQ_API_KEY:
                logger.error("GROQ_API_KEY not set")
                return None
            
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are JARVIS, a helpful AI assistant. Respond concisely."},
                    {"role": "user", "content": query}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except ImportError:
            logger.error("groq library not available")
            return None
        except Exception as e:
            logger.error(f"Groq query error: {e}")
            return None
