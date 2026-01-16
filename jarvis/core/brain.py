"""
Command parser, LLM integration, and decision making.
"""
from typing import Dict, Callable, Optional
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import extract_keywords, clean_text
from jarvis.config import (
    USE_OPENROUTER, USE_GEMINI, USE_GROQ, 
    OPENROUTER_API_KEY, OPENROUTER_MODEL, 
    GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY,
    JARVIS_SYSTEM_PROMPT
)

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
            # Prioritize more specific action keywords
            # Priority: system_commands > scrape > system > app_control > file_manager > weather > web > basic
            priority_map = {
                "system_commands": 8,  # Most dangerous, highest priority
                "scrape": 7,
                "system": 6,
                "app_control": 5,
                "file_manager": 4,
                "weather": 3,
                "web": 2,
                "basic": 1
            }
            
            best_keyword = matched_keywords[0]
            best_priority = priority_map.get(self.keyword_map.get(best_keyword), 0)
            
            for keyword in matched_keywords[1:]:
                keyword_skill = self.keyword_map.get(keyword)
                keyword_priority = priority_map.get(keyword_skill, 0)
                
                if keyword_priority > best_priority:
                    best_keyword = keyword
                    best_priority = keyword_priority
            
            skill_name = self.keyword_map[best_keyword]
            handler = self.skills.get(skill_name)
            
            if handler:
                try:
                    logger.debug(f"Executing skill '{skill_name}' (keyword: '{best_keyword}')")
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
            if USE_OPENROUTER:
                return self._query_openrouter(query)
            elif USE_GEMINI:
                return self._query_gemini(query)
            elif USE_GROQ:
                return self._query_groq(query)
            else:
                logger.warning("No LLM configured, returning default response")
                return "I'm not sure how to help with that. Could you rephrase?"
        except Exception as e:
            logger.error(f"LLM fallback error: {e}")
            return "I'm having trouble understanding. Could you try again?"
    
    def _query_openrouter(self, query: str) -> Optional[str]:
        """Query OpenRouter API using OpenAI-compatible client."""
        try:
            from openai import OpenAI  # type: ignore
            
            if not OPENROUTER_API_KEY:
                logger.error("OPENROUTER_API_KEY not set")
                return "I need an OpenRouter API key to function. Please set OPENROUTER_API_KEY in your .env file."
            
            # OpenRouter is OpenAI-compatible, use OpenAI client
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            
            # Try llama-3.1-70b-instruct:free first, fallback to qwen2.5-72b-instruct
            model = OPENROUTER_MODEL
            
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,  # Lower temperature for more consistent & thoughtful responses
                top_p=0.9,
                max_tokens=400,
            )
            
            if completion.choices and len(completion.choices) > 0:
                response_text = completion.choices[0].message.content.strip()
                if response_text:
                    return response_text
            
            logger.warning("OpenRouter returned empty response")
            return "I'm not sure how to help with that. Could you rephrase?"
                
        except ImportError:
            logger.error("openai library not available. Install with: pip install openai")
            return "OpenAI library not installed. Please install openai."
        except Exception as e:
            logger.error(f"OpenRouter query error: {e}")
            # Try fallback models if primary fails
            fallback_models = [
                "xiaomi/mimo-v2-flash:free",
                "nvidia/nemotron-3-nano-30b-a3b:free",
                "qwen/qwen3-next-80b-a3b-instruct:free"
            ]
            logger.info("Trying fallback models...")
            for fallback_model in fallback_models:
                try:
                    result = self._query_openrouter_fallback(query, fallback_model)
                    if result:
                        logger.info(f"Fallback model '{fallback_model}' succeeded")
                        return result
                except Exception as fallback_error:
                    logger.debug(f"Fallback '{fallback_model}' failed: {fallback_error}")
                    continue
            return f"I encountered an error: {str(e)}"
    
    def _query_openrouter_fallback(self, query: str, fallback_model: str) -> Optional[str]:
        """Fallback query with alternative model."""
        try:
            from openai import OpenAI  # type: ignore
            
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            
            completion = client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                top_p=0.9,
                max_tokens=400,
            )
            
            if completion.choices and len(completion.choices) > 0:
                return completion.choices[0].message.content.strip()
            return None
        except Exception as e:
            logger.error(f"Fallback model error: {e}")
            return None
    
    def _query_gemini(self, query: str) -> Optional[str]:
        """Query Google Gemini API."""
        try:
            import google.generativeai as genai  # type: ignore
            
            if not GEMINI_API_KEY:
                logger.error("GEMINI_API_KEY not set")
                return "I need a Gemini API key to function. Please set GEMINI_API_KEY in your .env file."
            
            # Configure Gemini
            genai.configure(api_key=GEMINI_API_KEY)
            
            # Create model instance
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            # System prompt + user query
            prompt = f"""You are JARVIS, a helpful AI assistant inspired by Iron Man. 
You are witty, efficient, and always ready to assist. Respond concisely and naturally to the user's request.

User: {query}
JARVIS:"""
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=200,
                    temperature=0.7,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini returned empty response")
                return "I'm not sure how to help with that. Could you rephrase?"
                
        except ImportError:
            logger.error("google-generativeai library not available. Install with: pip install google-generativeai")
            return "Gemini library not installed. Please install google-generativeai."
        except Exception as e:
            logger.error(f"Gemini query error: {e}")
            return f"I encountered an error: {str(e)}"
    
    def _query_groq(self, query: str) -> Optional[str]:
        """Query Groq LLM."""
        try:
            from groq import Groq  # type: ignore
            
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
