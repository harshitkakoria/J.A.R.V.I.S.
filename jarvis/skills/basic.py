"""
Basic skills: time, joke, wikipedia, exit, who are you, reminders.
"""
from datetime import datetime
import pyjokes
import wikipedia
from typing import Optional
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import format_time, extract_query_after_keyword, sanitize_search_term

# Optional: lazy-load spaCy for better entity extraction on Wikipedia queries
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy  # type: ignore
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = None
    return _nlp

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle basic commands.
    
    Args:
        query: User query
        
    Returns:
        Response text or None
    """
    query_lower = query.lower()
    
    # Greetings
    if any(kw in query_lower for kw in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"]):
        import random
        greetings = [
            "Yes, sir. What can I do for you?",
            "Hello. How may I help?",
            "Yes, sir. I'm here.",
            "Good to hear from you. What do you need?",
            "Hello. What's on your mind?",
            "Yes, sir. Go ahead.",
            "I'm here. What can I help with?",
            "Hello. What would you like?",
            "Yes, sir. What's the task?",
            "At your service. What do you need?"
        ]
        return random.choice(greetings)
    
    # Time
    if any(kw in query_lower for kw in ["time", "what time", "current time"]):
        now = datetime.now()
        time_str = format_time(now.hour, now.minute)
        return f"The current time is {time_str}"
    
    # Date
    if any(kw in query_lower for kw in ["date", "what date", "today's date"]):
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        return f"Today's date is {date_str}"
    
    # Joke
    if any(kw in query_lower for kw in ["joke", "tell me a joke", "make me laugh"]):
        try:
            joke = pyjokes.get_joke()
            return joke
        except Exception as e:
            logger.error(f"Error getting joke: {e}")
            # Fallback jokes
            jokes = [
                "Why did the AI break up with the computer? It had too many bugs!",
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                "Why do Java developers wear glasses? Because they don't C#!",
                "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
                "Why did the developer go broke? Because he used up all his cache!",
                "How many Prolog programmers does it take to change a lightbulb? No, that's not how Prolog works.",
                "Why do we call it debugging? Because in the 1940s, a real bug caused a computer error!"
            ]
            import random
            return random.choice(jokes)
    
    # Wikipedia search
    # Wikipedia search (but NOT for weather-related or math queries)
    weather_keywords = ["weather", "temperature", "forecast", "rain", "cold", "hot", "climate", "humid"]
    is_weather_query = any(kw in query_lower for kw in weather_keywords)
    
    # Skip Wikipedia for math questions - let LLM handle them
    math_patterns = ["+", "-", "*", "/", "×", "÷", "plus", "minus", "times", "divided", "multiply", "subtract", "add"]
    is_math_query = any(pattern in query_lower for pattern in math_patterns)
    
    if not is_weather_query and not is_math_query and any(kw in query_lower for kw in ["wikipedia", "search wikipedia", "what is", "who is", "tell me about"]):
        # Extract search term
        search_term = None
        for keyword in ["wikipedia", "search wikipedia", "what is", "who is", "tell me about"]:
            search_term = extract_query_after_keyword(query, keyword)
            if search_term:
                break
        
        if not search_term:
            # Try to get the last part of query
            words = query.split()
            if len(words) > 2:
                search_term = " ".join(words[-3:])
        
        if search_term:
            # Sanitize extracted term (strip trailing punctuation, quotes)
            search_term = sanitize_search_term(search_term)

            # Try to refine the search term using NER (PERSON/ORG/GPE) if spaCy is available
            try:
                nlp = _get_nlp()
                if nlp is not None:
                    doc = nlp(query)
                    # Prefer PERSON, then ORG, then GPE for Wikipedia-style lookups
                    candidates = [
                        ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE")
                    ]
                    if candidates:
                        search_term = sanitize_search_term(candidates[0])
            except Exception:
                # If NER fails for any reason, continue with the original cleaned term
                pass
            try:
                # Set language to English for now
                wikipedia.set_lang("en")
                # Try direct summary first
                summary = wikipedia.summary(search_term, sentences=2)
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Multiple results found. Could you be more specific? Options include: {', '.join(e.options[:5])}"
            except wikipedia.exceptions.PageError:
                # Retry using Wikipedia search to suggest closest titles and try multiple candidates
                try:
                    results = wikipedia.search(search_term)
                    if results:
                        # Try up to 5 candidates to find a resolvable page
                        for title in results[:5]:
                            try:
                                summary = wikipedia.summary(title, sentences=2)
                                if summary:
                                    return summary
                            except wikipedia.exceptions.DisambiguationError:
                                continue
                            except wikipedia.exceptions.PageError:
                                continue
                            except Exception:
                                continue
                        # If none succeeded, present suggestions
                        suggestions = ", ".join(results[:5])
                        return (
                            "I couldn't find an exact page, but here are some suggestions: "
                            + suggestions
                        )
                    return f"Sorry, I couldn't find information about '{search_term}' on Wikipedia."
                except Exception:
                    return f"Sorry, I couldn't find information about '{search_term}' on Wikipedia."
            except Exception as e:
                logger.error(f"Wikipedia error: {e}")
                return "Sorry, I encountered an error while searching Wikipedia."
        else:
            return "What would you like me to search on Wikipedia?"
    
    # Who are you
    if any(kw in query_lower for kw in ["who are you", "what are you", "introduce yourself", "your name"]):
        import random
        intros = [
            "I am JARVIS, Just A Rather Very Intelligent System. I serve as your personal AI assistant.",
            "I am JARVIS, your virtual assistant designed to help with various tasks and information.",
            "JARVIS here - Just A Rather Very Intelligent System. I am programmed to assist you efficiently.",
            "I am JARVIS, an artificial intelligence assistant at your disposal.",
            "JARVIS, your dedicated AI assistant. I am here to provide comprehensive support."
        ]
        return random.choice(intros)
    
    # Exit/Bye
    if any(kw in query_lower for kw in ["exit", "bye", "goodbye", "quit", "shut down", "stop"]):
        return "Goodbye! Have a great day!"
    
    # Not handled
    return None


def handle_reminder(query: str, brain=None) -> Optional[str]:
    """
    Handle reminders, notifications, and tasks.
    Requires brain object for task scheduler access.
    
    Args:
        query: User query
        brain: Brain instance with task scheduler
        
    Returns:
        Response confirming task was added
    """
    if not brain or not hasattr(brain, 'task_scheduler'):
        return None
    
    query_lower = query.lower()
    
    # Check for reminder/notification keywords
    is_reminder = any(kw in query_lower for kw in ["remind", "remember", "notification", "notify"])
    is_todo = any(kw in query_lower for kw in ["todo", "task", "add to", "need to", "remember to"])
    is_list = any(kw in query_lower for kw in ["list reminders", "show reminders", "my reminders", "what reminders"])
    
    # List reminders
    if is_list:
        from jarvis.utils.task_scheduler import TaskScheduler
        scheduler = brain.task_scheduler if hasattr(brain, 'task_scheduler') else TaskScheduler()
        summary = scheduler.list_tasks_human_readable()
        return summary
    
    # Add reminder or todo
    if is_reminder or is_todo:
        from jarvis.utils.task_scheduler import TaskScheduler
        scheduler = brain.task_scheduler if hasattr(brain, 'task_scheduler') else TaskScheduler()
        
        # Extract task info
        task_info = scheduler.extract_task_info(query)
        
        if task_info:
            task_type = task_info['type']
            content = task_info['content']
            time_str = task_info['time']
            
            # Add task
            task = scheduler.add_task(
                task_type=task_type,
                content=content,
                scheduled_time=time_str,
                recurring="once"
            )
            
            if time_str:
                response = f"Got it. I'll {task_type} you to {content} at {time_str}. Even if you close me, I'll remember this."
            else:
                response = f"Added to your {task_type}s: {content}. I'll keep this in memory."
            
            return response
        else:
            return "I can't quite understand the reminder. Could you say something like 'Remind me to call mom at 5 pm'?"
    
    return None
