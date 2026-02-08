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
        self.pending_clarification = None # Store ambiguous state
        self.filename = filename
        self.load()
        
        # Initialize Vector Memory (Long-term)
        try:
             from jarvis.utils.vector_memory import VectorMemory
             self.vector_memory = VectorMemory()
             print("[+] Long-term Memory initialized")
        except ImportError:
             print("[!] Vector Memory dependencies missing. Running in Short-term mode.")
             self.vector_memory = None
        except Exception as e:
             print(f"[!] Vector Memory failed to load: {e}")
             self.vector_memory = None
    
    def add(self, user_query: str, jarvis_response: str, tag: str = "conversation"):
        """Save exchange with tag (conversation, action, fact)."""
        self.history.append({
            'time': datetime.now().strftime("%H:%M"),
            'user': user_query,
            'jarvis': jarvis_response,
            'tag': tag
        })
        if self.vector_memory and tag == "conversation":
             # Try to store in long-term memory (internally checks filters)
             self.vector_memory.add(user_query, metadata={"response": jarvis_response})
             
        self.save()
    
    def get_recent(self, count=3) -> list:
        """Get last N exchanges."""
        return list(self.history)[-count:]
    
    def recall(self, keyword: str) -> str:
        """Find if keyword was mentioned recently (Short-term)."""
        for exchange in reversed(self.history):
            if keyword.lower() in exchange['user'].lower():
                return exchange['jarvis']
        return None

    def recall_semantic(self, query: str) -> str:
        """Recall from long-term memory using vector search."""
        if not self.vector_memory:
            return None
            
        result = self.vector_memory.search(query)
        if result:
            text, distance = result
            # Return just the text for now, Brain handles formatting
            return text
        return None
    
    def set_context(self, key: str, value: str):
        """Store context (name, preferences, etc)."""
        self.context[key] = value
        self.save()
    
    def get_context(self, key: str) -> str:
        """Get stored context."""
        return self.context.get(key)
        
    def set_pending_clarification(self, data: dict):
        """Store details about an ambiguous request."""
        self.pending_clarification = data
        self.save()
        
    def get_pending_clarification(self):
        """Retrieve pending clarification if any."""
        return self.pending_clarification
        
    def clear_pending_clarification(self):
        """Clear pending clarification state."""
        self.pending_clarification = None
        self.save()
    
    def get_summary(self) -> str:
        """Get conversation summary including context."""
        summary_parts = []
        
        # 1. Add Context (User info)
        if self.context:
            context_str = "Known Context:\n"
            for k, v in self.context.items():
                context_str += f"- {k}: {v}\n"
            summary_parts.append(context_str)
        
        # 2. Add Recent History (Full)
        if self.history:
            history_str = "Recent Conversation:\n"
            for ex in self.history: # Use all 10 items in deque
                history_str += f"[{ex['time']}] User: {ex['user']}\n"
                history_str += f"[{ex['time']}] JARVIS: {ex['jarvis']}\n"
            summary_parts.append(history_str)
        else:
            summary_parts.append("No recent conversation.")
            
        return "\n".join(summary_parts)

    def save(self):
        """Save memory to file."""
        try:
            data = {
                "history": list(self.history),
                "context": self.context,
                "pending_clarification": self.pending_clarification
            }
            # Ensure directory exists
            path = Path(self.filename)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def has_recent_entity(self) -> bool:
        """Check if there's a recent entity to resolve pronouns against."""
        # v3.6: Placeholder - always False to enforce safety for now.
        # Future: Check context or recent history for apps/concepts.
        return False

    def load(self):
        """Load memory from file."""
        path = Path(self.filename)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.history = deque(data.get("history", []), maxlen=self.history.maxlen)
                    self.context = data.get("context", {})
                    self.pending_clarification = data.get("pending_clarification")
            except Exception as e:
                print(f"Error loading memory: {e}")
