"""
Conversation memory management for JARVIS.
Stores and retrieves conversation history for contextual responses.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from jarvis.utils.logger import setup_logger
from jarvis.config import MEMORY_FILE

logger = setup_logger(__name__)

# Max exchanges to keep in memory (each exchange = user + assistant)
MAX_MEMORY_SIZE = 5


class ConversationMemory:
    """Manages conversation history for context-aware responses."""
    
    def __init__(self, memory_file: Path = MEMORY_FILE):
        """Initialize conversation memory.
        
        Args:
            memory_file: Path to memory.json file
        """
        self.memory_file = memory_file
        self.conversation_history: List[Dict] = []
        self.load_memory()
    
    def load_memory(self) -> None:
        """Load conversation history from memory.json."""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversation_history', [])
                    logger.debug(f"Loaded {len(self.conversation_history)} memory items")
            else:
                self.conversation_history = []
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.conversation_history = []
    
    def save_memory(self) -> None:
        """Save conversation history to memory.json."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing data (to preserve other fields)
            existing_data = {}
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Update conversation history
            existing_data['conversation_history'] = self.conversation_history
            existing_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def add_exchange(self, user_message: str, assistant_response: str) -> None:
        """Add a user-assistant exchange to memory.
        
        Args:
            user_message: User's query
            assistant_response: JARVIS's response
        """
        # Add new exchange
        exchange = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation_history.append(exchange)
        
        # Keep only last MAX_MEMORY_SIZE exchanges
        if len(self.conversation_history) > MAX_MEMORY_SIZE:
            self.conversation_history = self.conversation_history[-MAX_MEMORY_SIZE:]
        
        # Save to file
        self.save_memory()
        logger.debug(f"Added exchange to memory. Total: {len(self.conversation_history)}")
    
    def get_context(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM context.
        
        Returns:
            List of messages in OpenAI format: [{"role": "user"/"assistant", "content": "..."}, ...]
        """
        messages = []
        for exchange in self.conversation_history:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})
        return messages
    
    def clear_memory(self) -> None:
        """Clear all conversation history."""
        self.conversation_history = []
        self.save_memory()
        logger.info("Conversation memory cleared")
    
    def get_summary(self) -> str:
        """Get a brief summary of recent topics discussed."""
        if not self.conversation_history:
            return "No previous conversations."
        
        recent = self.conversation_history[-3:]
        summary = "Recent topics: " + " | ".join([exc["user"][:30] + "..." for exc in recent])
        return summary
