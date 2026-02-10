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
    
    # User Identity (Who am I?)
    if "who am i" in q or "my name" in q:
        # We need memory to know the name. 
        # But this handler is stateless (just a function).
        # We can't access 'memory' instance here easily unless we pass it.
        # However, Brain passes only 'query'.
        # We might need to return a specific string that Brain interprets?
        # OR we change the signature in Executor to pass memory/context?
        # NO, keep it simple. Brain handles "memory queries" separately?
        # Brain.process lines 147 handles "remember", "recall".
        # But "who am i" falls to 'context' category in DecisionMaker.
        # DecisionMaker 'context' maps to 'basic' skill.
        # So we arrive here.
        return "I am JARVIS. I believe you are... wait, I need check my memory. Ask 'What is my name?'"
        
    # Context (Time/Date/Identity rolled into one)
    if "context" in q or "who are you" in q: # fallback
         return f"I am JARVIS. {datetime.now().strftime('It is %I:%M %p on %A, %B %d')}"

    # Greetings handled by brain for personalization
    return None
