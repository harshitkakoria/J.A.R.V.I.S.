"""Memory - Simple conversation history with persistence."""
import os
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
        
        # Session Logging (User Request)
        self.chats_dir = Path("data/chats")
        self.chats_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_file = self.chats_dir / f"chat_{self.session_id}.json"
        
        # Initialize session file
        if not self.session_file.exists():
            with open(self.session_file, 'w') as f:
                json.dump([], f)
                
        # v7.6 Feature: Reload recent history from previous session?
        # User wants continuity. We should check if there's a recent previous session.
        self._load_recent_history()
        
        # Vector Memory (Long-term) can be very heavy (chromadb + embeddings).
        # To keep startup fast/reliable, it's disabled by default and can be enabled via env var.
        enable_vector = os.getenv("JARVIS_ENABLE_VECTOR_MEMORY", "").strip().lower() in {"1", "true", "yes", "on"}
        self.vector_memory = None
        if enable_vector:
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
        """Save exchange with tag and log to session file."""
        entry = {
            'time': datetime.now().strftime("%H:%M:%S"),
            'user': user_query,
            'jarvis': jarvis_response,
            'tag': tag
        }
        
        # Update Short-term Memory
        self.history.append(entry)
        
        # Log to Session File (Full History)
        self._log_to_session(entry)
        
        if self.vector_memory:
             # Store full interaction in long-term memory
             # Format: "User: [query]\nJARVIS: [response]"
             # This allows semantic search to find what user asked OR what Jarvis said.
             full_text = f"User: {user_query}\nJARVIS: {jarvis_response}"
             
             # Metadata for context
             meta = {
                 "timestamp": datetime.now().isoformat(),
                 "type": tag # Preserve tag in metadata
             }
             
             try:
                self.vector_memory.add(full_text, metadata=meta)
             except Exception as e:
                print(f"[!] Vector Memory Add Error: {e}")
             
        self.save() # Update memory.json (snapshot)

    def _log_to_session(self, entry: dict):
        """Append entry to session JSON log."""
        try:
            # Read-Modify-Write to keep valid JSON array
            # Optimization: Could use a file-lock or just append to list
            if self.session_file.exists():
                with open(self.session_file, 'r+') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
                    
                    data.append(entry)
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
            else:
                 with open(self.session_file, 'w') as f:
                    json.dump([entry], f, indent=4)
                    
        except Exception as e:
            print(f"[!] Error logging to session file: {e}")

    def _load_recent_history(self):
        """Load recent history from the latest session file (if any)."""
        try:
            # Find all chat files
            chat_files = list(self.chats_dir.glob("chat_*.json"))
            if not chat_files:
                return

            # Sort by modification time (most recent last)
            # Actually filename has timestamp, sorting by name is safer?
            # chat_YYYY-MM-DD_HH-MM-SS.json
            chat_files.sort(key=lambda x: x.name)
            
            # v7.6 User Request: "Access to ALL conversations"
            # Instead of just the last file, we load ALL files.
            print(f"[Memory] Loading ALL conversation history from {len(chat_files)} sessions...")
            
            # If start up, current session file is empty (or just created).
            # We skip the current session file if it's empty to avoid reading what we just wrote (empty logic handled by logic)?
            # Actually, `chat_files` includes the current one.
            
            total_count = 0
            all_data = []
            
            for chat_file in chat_files:
                # Skip current session file if it's empty/new (to avoid issues, though json.load handles valid json)
                if chat_file.name == self.session_file.name:
                    continue
                    
                try:
                    with open(chat_file, 'r') as f:
                        file_data = json.load(f)
                        if isinstance(file_data, list):
                           all_data.extend(file_data)
                except Exception as e:
                    print(f"[!] Warning: Failed to load {chat_file.name}: {e}")

            # v7.6 User Request: "Not last 20 but all"
            # If maxlen is None, we load everything.
            if self.history.maxlen is not None:
                 # Override purely for this request
                 self.history = deque(maxlen=None)

            # Load ALL items
            for item in all_data:
                self.history.append(item)
                
            print(f"[Memory] Restored GLOBAL history: {len(self.history)} exchanges.")
            
        except Exception as e:
            print(f"[!] Error loading recent history: {e}")
    
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
            
        # v7.6 Update: VectorMemory.search now returns combined string or None
        return self.vector_memory.search(query)
    
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
    
    def get_summary(self, max_exchanges: int = 10) -> str:
        """Get a prompt-safe conversation summary including context.

        Note: We intentionally cap the number of exchanges included to keep LLM prompts
        small and responses fast/reliable.
        """
        summary_parts = []
        
        # 1. Add Context (User info)
        if self.context:
            context_str = "Known Context:\n"
            for k, v in self.context.items():
                context_str += f"- {k}: {v}\n"
            summary_parts.append(context_str)
        
        # 2. Add Recent History (CAPPED)
        if self.history:
            history_str = "Recent Conversation:\n"
            recent = list(self.history)[-max_exchanges:] if max_exchanges else list(self.history)
            for ex in recent:
                history_str += f"[{ex['time']}] User: {ex['user']}\n"
                history_str += f"[{ex['time']}] JARVIS: {ex['jarvis']}\n"
            summary_parts.append(history_str)
        else:
            summary_parts.append("No recent conversation.")
            
        return "\n".join(summary_parts)

    def save(self):
        """Save memory. (No-op: memory.json removed)."""
        pass

    def has_recent_entity(self) -> bool:
        """Check if there's a recent entity to resolve pronouns against."""
        # v3.6: Placeholder - always False to enforce safety for now.
        return False

    def summarize_session(self):
        """Summarize current session using LLM and save for long-term learning."""
        try:
            if not self.session_file.exists():
                return
                
            # Read current session
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                
            if not data:
                return
                
            # Filter for conversation only
            conversation_text = ""
            for entry in data:
                if entry.get('tag') == 'conversation':
                    conversation_text += f"User: {entry['user']}\nJARVIS: {entry['jarvis']}\n"
            
            if not conversation_text:
                return
                
            print("\n[Memory] Summarizing session for long-term storage...")
            
            # Lazy import to avoid circular dependency
            from jarvis.core.llm import LLM
            llm = LLM()
            
            if not llm.client:
                print("[!] LLM not available for summarization.")
                return

            prompt = f"""Summarize the following conversation into a concise list of KEY FACTS about the User (preferences, projects, identity) and important context.
Ignore small talk, greetings, and temporary commands (like "open spotify").
Focus on PERMANENT information that should be remembered.

Conversation:
{conversation_text}

Output format:
- User is a [role]
- User is working on [project]
- User likes [preference]
"""
            
            summary = llm.chat(prompt, system_instruction="You are a Memory Compresson System.")
            
            if summary:
                # Save to learning data
                summary_file = Path("data/learning_data") / f"summary_{self.session_id}.txt"
                with open(summary_file, 'w') as f:
                    f.write(f"Session Summary ({self.session_id}):\n{summary}")
                print(f"[+] Session summary saved to {summary_file.name}")
                
        except Exception as e:
            print(f"[!] Summarization failed: {e}")
            
    def load(self):
        """Load memory. (No-op: memory.json removed)."""
        pass
