"""Memory - Simple conversation history with persistence."""
import json
from collections import deque
from datetime import datetime
from pathlib import Path


class Memory:
    """Track recent conversation and persist to file."""
    
    def __init__(self, max_size=10, filename="data/memory.json"):
        self.history = deque(maxlen=max_size)  # Last 10 exchanges
        self.context = {}  # Store context like user name, preferences
        self.filename = filename
        self.load()
    
    def add(self, user_query: str, jarvis_response: str):
        """Save exchange."""
        self.history.append({
            'time': datetime.now().strftime("%H:%M"),
            'user': user_query,
            'jarvis': jarvis_response
        })
        self.save()
    
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
        self.save()
    
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

    def save(self):
        """Save memory to file."""
        try:
            data = {
                "history": list(self.history),
                "context": self.context
            }
            # Ensure directory exists
            path = Path(self.filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def load(self):
        """Load memory from file."""
        path = Path(self.filename)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.history = deque(data.get("history", []), maxlen=self.history.maxlen)
                    self.context = data.get("context", {})
            except Exception as e:
                print(f"Error loading memory: {e}")
