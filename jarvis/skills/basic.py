"""Basic commands - time, date, jokes."""
from datetime import datetime
import pyjokes

def handle(query: str) -> str:
    """Handle basic commands."""
    q = query.lower()
    
    # Time
    if "time" in q:
        return datetime.now().strftime("It's %I:%M %p")
    
    # Date
    if "date" in q:
        return datetime.now().strftime("Today is %B %d, %Y")
    
    # Joke
    if "joke" in q:
        return pyjokes.get_joke()
    
    # Who are you
    if "who are you" in q or "your name" in q:
        return "I'm JARVIS, your voice assistant."
    
    # Exit
    if any(w in q for w in ["exit", "quit", "bye", "goodbye"]):
        return "Goodbye!"
    
    # Greetings handled by brain for personalization
    return None
