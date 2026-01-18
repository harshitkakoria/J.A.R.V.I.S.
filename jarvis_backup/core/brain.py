"""
Command parser, LLM integration, and decision making.
"""
import asyncio
import threading
from typing import Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import extract_keywords, clean_text
from jarvis.utils.intent_parser import IntentParser, CommandExecutor
from jarvis.utils.conversation_memory import ConversationMemory
from jarvis.utils.personality import PersonalityConfig, PersonalityType
from jarvis.utils.command_classifier import CommandClassifier
from jarvis.utils.task_scheduler import TaskScheduler
from jarvis.utils.async_utils import AsyncManager, ParallelExecutor
from jarvis.config import (
    USE_OPENROUTER, USE_GEMINI, USE_GROQ, 
    OPENROUTER_API_KEY, OPENROUTER_MODEL, 
    GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL,
    JARVIS_SYSTEM_PROMPT
)

logger = setup_logger(__name__)


class Brain:
    """Command dispatcher with AI intent parsing, personality, and memory."""
    
    def __init__(self, max_workers: int = 4, personality: PersonalityType = PersonalityType.CASUAL):
        """Initialize brain with skill mappings, AI parsing, and personality.
        
        Args:
            max_workers: Maximum number of worker threads for parallel skill execution
            personality: Personality type for responses (casual, witty, sarcastic, etc.)
        """
        self.skills: Dict[str, Callable[[str], Optional[str]]] = {}
        self.keyword_map: Dict[str, str] = {}  # keyword -> skill_name
        self.intent_parser = IntentParser()  # AI intent parser
        self.command_executor = CommandExecutor(brain=self)  # Command executor
        self.executor = ThreadPoolExecutor(max_workers=max_workers)  # Thread pool for parallel execution
        self.async_manager = AsyncManager(max_workers=max_workers)  # Async manager
        self._lock = threading.Lock()  # Lock for thread-safe operations
        
        # New systems
        self.memory = ConversationMemory()  # Conversation memory
        self.personality = PersonalityConfig(personality)  # Personality system
        self.classifier = CommandClassifier()  # Command/chat classifier
        self.task_scheduler = TaskScheduler()  # Task scheduler for reminders
        
        logger.info(f"Brain initialized with AI intent parsing, personality ({personality.value}), memory, task scheduler, and async support")
    
    def register_skill(self, skill_name: str, handler: Callable[[str], Optional[str]], keywords: list):
        """
        Register a skill with its handler and keywords.
        Thread-safe registration.
        
        Args:
            skill_name: Name of the skill
            handler: Function that handles the command
            keywords: List of keywords that trigger this skill
        """
        with self._lock:
            self.skills[skill_name] = handler
            for keyword in keywords:
                self.keyword_map[keyword.lower()] = skill_name
            logger.debug(f"Registered skill '{skill_name}' with keywords: {keywords}")
    
    def process(self, query: str) -> Optional[str]:
        """
        Process user query with priority: Real-Time Keywords → Keywords → AI Commands → LLM Questions.
        
        Priority:
        1. Real-time query detection (latest, current, breaking news)
        2. Direct keywords (fast execution)
        3. AI intent parsing (natural language commands)
        4. LLM fallback (questions/general info)
        
        Args:
            query: User's spoken command
            
        Returns:
            Response text or None
        """
        if not query:
            return None
        
        query_clean = clean_text(query)
        logger.info(f"Processing query: {query_clean}")

        # Handle very short or unclear queries with a clarification prompt
        tokens = query_clean.split()
        if len(tokens) <= 1:
            ambiguous = {"?", "what", "huh", "uh", "ok", "okay"}
            if query_clean in ambiguous:
                return "Could you clarify what you'd like me to do or know?"
        
        # Step 0: Detect real-time queries BEFORE general keyword matching
        # This prevents "latest news" from being routed to scrape instead of realtime search
        realtime_indicators = ["latest", "current", "recent", "today", "breaking", 
                               "real time", "right now", "find out", "search for"]
        has_realtime_indicator = any(indicator in query_clean.lower() for indicator in realtime_indicators)
        
        if has_realtime_indicator and "realtime_search" in self.skills:
            logger.debug("Real-time query detected, prioritizing real-time search engine...")
            handler = self.skills.get("realtime_search")
            if handler:
                try:
                    response = handler(query_clean)
                    if response:
                        logger.debug("Real-time search succeeded")
                        return response
                    else:
                        logger.debug("Real-time search returned no results, continuing to other methods...")
                except Exception as e:
                    logger.error(f"Real-time search error: {e}")
                    logger.debug("Falling back to other methods...")
        
        # Step 1: Try keyword matching for direct commands (after real-time check)
        logger.debug("Attempting keyword matching for direct commands...")
        matched_keywords = extract_keywords(query_clean, list(self.keyword_map.keys()))
        
        if matched_keywords:
            # Prioritize more specific action keywords
            priority_map = {
                "system_commands": 8,
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
                    logger.debug(f"Direct execution: skill '{skill_name}' (keyword: '{best_keyword}')")
                    response = handler(query_clean)
                    return response
                except Exception as e:
                    logger.error(f"Error executing skill '{skill_name}': {e}")
                    return f"Sorry, I encountered an error: {str(e)}"
        
        # Step 2: Try AI intent parsing (for unclear natural language commands)
        logger.debug("Attempting AI intent parsing for natural language...")
        command = self.intent_parser.parse_command(query_clean)
        
        if command and command.get("intent") != "unknown" and command.get("confidence", 0) > 0.5:
            intent = command.get("intent")
            logger.debug(f"AI parsed as: {intent} (confidence: {command.get('confidence')})")
            
            # If AI thinks it's a question, skip to LLM
            if intent == "get_info":
                # Prefer built-in skills for common patterns like Wikipedia queries
                if any(kw in query_clean for kw in ["who is", "what is", "tell me about", "wikipedia"]):
                    handler = self.skills.get("basic")
                    if handler:
                        return handler(query_clean)
                logger.debug("AI classified as information question, using LLM...")
                return self._llm_fallback(query_clean)
            
            try:
                response = self.command_executor.execute(command)
                if response:
                    return response
            except Exception as e:
                logger.error(f"Error executing AI-parsed command: {e}")
                logger.debug("Falling back to LLM...")
        
        # Step 3: Fallback to LLM for questions and general queries
        logger.debug("Using LLM for general response...")
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
            # Groq first (no rate limits on free tier)
            if USE_GROQ:
                return self._query_groq(query)
            # Fallback to OpenRouter
            elif USE_OPENROUTER:
                return self._query_openrouter(query)
            elif USE_GEMINI:
                return self._query_gemini(query)
            else:
                logger.warning("No LLM configured, returning default response")
                return "I'm not sure how to help with that. Could you rephrase?"
        except Exception as e:
            logger.error(f"LLM fallback error: {e}")
            return "I'm having trouble understanding. Could you try again?"

    def _style_response(self, text: str) -> Optional[str]:
        """
        Rephrase plain responses into the JARVIS persona using the configured LLM.
        Falls back to original text if no LLM is configured or if an error occurs.

        Args:
            text: Plain response text

        Returns:
            Styled response or None
        """
        if not text:
            return None

        prompt = (
            "Rewrite the following answer in the voice of JARVIS — concise, helpful,"
            " and slightly witty. Keep facts intact.\n\nAnswer:\n" + text
        )

        try:
            # Groq first (no rate limits on free tier)
            if USE_GROQ:
                return self._query_groq(prompt)
            # Fallback to OpenRouter
            elif USE_OPENROUTER:
                return self._query_openrouter(prompt)
            elif USE_GEMINI:
                return self._query_gemini(prompt)
            elif USE_GROQ:
                return self._query_groq(prompt)
            else:
                return text
        except Exception as e:
            logger.error(f"Styling error: {e}")
            return text
    
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
            error_str = str(e)
            # Check for rate limit error
            if "429" in error_str or "rate limit" in error_str.lower():
                logger.warning(f"OpenRouter rate limited: {e}")
                logger.info("Switching to Groq (no rate limits)...")
                # Skip fallback models and go directly to Groq
                return self._query_groq(query)
            
            # Try fallback models for other errors
            fallback_models = [
                "xiaomi/mimo-v2-flash:free",
                "nvidia/nemotron-3-nano-30b-a3b:free",
                "qwen/qwen3-next-80b-a3b-instruct:free"
            ]
            logger.info("Trying fallback OpenRouter models...")
            for fallback_model in fallback_models:
                try:
                    result = self._query_openrouter_fallback(query, fallback_model)
                    if result:
                        logger.info(f"Fallback model '{fallback_model}' succeeded")
                        return result
                except Exception as fallback_error:
                    logger.debug(f"Fallback '{fallback_model}' failed: {fallback_error}")
                    # If this fallback also rate limited, switch to Groq
                    if "429" in str(fallback_error) or "rate limit" in str(fallback_error).lower():
                        logger.warning("Fallback also rate limited, using Groq...")
                        return self._query_groq(query)
                    continue
            
            # Final fallback: Groq
            logger.info("Final fallback: using Groq...")
            groq_response = self._query_groq(query)
            if groq_response:
                return groq_response
            
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
        """Query Groq LLM using free tier models."""
        try:
            from groq import Groq  # type: ignore
            
            if not GROQ_API_KEY:
                logger.error("GROQ_API_KEY not set")
                return "I need a Groq API key. Get one free at: https://console.groq.com"
            
            client = Groq(api_key=GROQ_API_KEY)
            
            # Use free tier models with fallback
            model = GROQ_MODEL
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            
            logger.warning("Groq returned empty response")
            return "I'm not sure how to help with that. Could you rephrase?"
            
        except ImportError:
            logger.error("groq library not available. Install with: pip install groq")
            return "Groq library not installed. Please install groq."
        except Exception as e:
            logger.error(f"Groq query error: {e}")
            # Try fallback model
            try:
                logger.info("Trying fallback Groq model...")
                client = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": JARVIS_SYSTEM_PROMPT},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=400,
                    temperature=0.3
                )
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
            except Exception as fallback_error:
                logger.error(f"Groq fallback error: {fallback_error}")
            
            return f"I encountered an error: {str(e)}"
    
    def execute_skill_parallel(self, skill_name: str, query: str) -> Optional[str]:
        """
        Execute a skill in a background thread (non-blocking).
        
        Args:
            skill_name: Name of the skill to execute
            query: User query to pass to skill
            
        Returns:
            Future object for the result
        """
        if skill_name not in self.skills:
            logger.warning(f"Skill '{skill_name}' not found")
            return None
        
        handler = self.skills[skill_name]
        logger.debug(f"Submitting skill '{skill_name}' to thread pool for parallel execution")
        
        try:
            future = self.executor.submit(handler, query)
            return future  # Return future object - caller can call .result() to wait
        except Exception as e:
            logger.error(f"Error submitting skill to executor: {e}")
            return None
    
    def execute_multiple_skills(self, skills_list: list, query: str) -> Dict[str, Optional[str]]:
        """
        Execute multiple skills in parallel and wait for all to complete.
        
        Args:
            skills_list: List of skill names to execute in parallel
            query: User query to pass to each skill
            
        Returns:
            Dictionary mapping skill names to their results
        """
        futures = {}
        results = {}
        
        logger.info(f"Executing {len(skills_list)} skills in parallel")
        
        # Submit all tasks to executor
        for skill_name in skills_list:
            if skill_name not in self.skills:
                logger.warning(f"Skill '{skill_name}' not found")
                results[skill_name] = None
                continue
            
            try:
                handler = self.skills[skill_name]
                future = self.executor.submit(handler, query)
                futures[skill_name] = future
            except Exception as e:
                logger.error(f"Error submitting skill '{skill_name}': {e}")
                results[skill_name] = None
        
        # Wait for all tasks and collect results
        for skill_name, future in futures.items():
            try:
                result = future.result(timeout=10)  # Wait max 10 seconds per skill
                results[skill_name] = result
                logger.debug(f"Skill '{skill_name}' completed: {str(result)[:50]}...")
            except Exception as e:
                logger.error(f"Error in skill '{skill_name}': {e}")
                results[skill_name] = None
        
        return results
    
    async def process_async(self, query: str) -> Optional[str]:
        """
        Process query asynchronously.
        
        Args:
            query: User query
            
        Returns:
            Response text
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, query)
    
    async def execute_skills_parallel(self, queries: list) -> Dict[str, Optional[str]]:
        """
        Execute multiple skills in parallel with async.
        
        Args:
            queries: List of (skill_name, query) tuples
            
        Returns:
            Dict of skill results
        """
        tasks = []
        skill_names = []
        
        for skill_name, query in queries:
            if skill_name in self.skills:
                handler = self.skills[skill_name]
                task = self._run_skill_async(handler, query)
                tasks.append(task)
                skill_names.append(skill_name)
        
        if not tasks:
            return {}
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {}
        for skill_name, result in zip(skill_names, results_list):
            results[skill_name] = result if not isinstance(result, Exception) else None
        
        return results
    
    async def _run_skill_async(self, handler: Callable, query: str) -> Optional[str]:
        """Run a skill handler asynchronously.
        
        Args:
            handler: Skill function
            query: Query string
            
        Returns:
            Skill result
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, handler, query)
            return result
        except Exception as e:
            logger.error(f"Async skill error: {e}")
            return None
    
    def shutdown_executor(self):
        """Gracefully shutdown the thread pool executor."""
        logger.info("Shutting down thread pool executor")
        self.executor.shutdown(wait=True)
        logger.info("Thread pool executor shut down successfully")
