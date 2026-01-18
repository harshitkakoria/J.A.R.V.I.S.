"""Memory - Simple conversation history."""
from collections import deque
from datetime import datetime


class Memory:
    """Track recent conversation."""
    
    def __init__(self, max_size=10):
        self.history = deque(maxlen=max_size)  # Last 10 exchanges
        self.context = {}  # Store context like user name, preferences
    
    def add(self, user_query: str, jarvis_response: str):
        """Save exchange."""
        self.history.append({
            'time': datetime.now().strftime("%H:%M"),
            'user': user_query,
            'jarvis': jarvis_response
        })
    
    def get_recent(self, count=3) -> list:
        """Get last N exchanges."""
        return list(self.history)[-count:]
    
    def recall(self, keyword: str) -> str:
        """Find if keyword was mentioned recently."""
        for exchange in reversed(self.history):
            if keyword.lower() in exchange['user'].lower():
                return exchange['jarvis']
        return None
    
    def set_context(self, key: str, value: str):
        """Store context (name, preferences, etc)."""
        self.context[key] = value
    
    def get_context(self, key: str) -> str:
        """Get stored context."""
        return self.context.get(key)
    
    def get_summary(self) -> str:
        """Get conversation summary."""
        if not self.history:
            return "No conversation history yet."
        
        recent = self.get_recent(3)
        summary = "Recent conversation:\n"
        for ex in recent:
            summary += f"{ex['time']} You: {ex['user'][:50]}...\n"
        return summary
