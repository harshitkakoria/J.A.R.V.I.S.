"""
Basic skills: time, joke, wikipedia, exit, who are you.
"""
from datetime import datetime
import pyjokes
import wikipedia
from typing import Optional
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import format_time, extract_query_after_keyword

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
            return "Why did the AI break up with the computer? It had too many bugs!"
    
    # Wikipedia search
    if any(kw in query_lower for kw in ["wikipedia", "search wikipedia", "what is", "who is", "tell me about"]):
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
            try:
                # Set language to English for now
                wikipedia.set_lang("en")
                summary = wikipedia.summary(search_term, sentences=2)
                return summary
            except wikipedia.exceptions.DisambiguationError as e:
                return f"Multiple results found. Could you be more specific? Options include: {', '.join(e.options[:5])}"
            except wikipedia.exceptions.PageError:
                return f"Sorry, I couldn't find information about '{search_term}' on Wikipedia."
            except Exception as e:
                logger.error(f"Wikipedia error: {e}")
                return "Sorry, I encountered an error while searching Wikipedia."
        else:
            return "What would you like me to search on Wikipedia?"
    
    # Who are you
    if any(kw in query_lower for kw in ["who are you", "what are you", "introduce yourself", "your name"]):
        return ("I am JARVIS, Just A Rather Very Intelligent System. "
                "I'm your personal AI assistant, ready to help you with various tasks. "
                "How can I assist you today?")
    
    # Exit/Bye
    if any(kw in query_lower for kw in ["exit", "bye", "goodbye", "quit", "shut down", "stop"]):
        return "Goodbye! Have a great day!"
    
    # Not handled
    return None
