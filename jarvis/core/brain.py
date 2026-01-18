"""Brain - Routes commands to skills."""
from typing import Dict, Callable, List
from jarvis.utils.memory import Memory
from jarvis.core.decision import DecisionMaker
from jarvis.core.task_handler import RealTimeSearch, ChatBot, Automation


class Brain:
    """Smart command router with memory and Groq AI."""
    
    def __init__(self, use_ai_decision=False):  # Disabled Cohere by default
        self.skills: Dict[str, tuple] = {}
        self.memory = Memory()
        self.use_ai_decision = use_ai_decision
        
        # Initialize task handlers
        self.realtime_search = RealTimeSearch()
        self.chatbot = ChatBot()
        self.automation = None  # Will be set after skills registration
        
        if use_ai_decision:
            try:
                self.decision_maker = DecisionMaker()
                print("✅ AI Decision Maker initialized")
            except Exception as e:
                print(f"⚠️ AI Decision Maker failed: {e}, using keyword matching")
                self.use_ai_decision = False
                self.decision_maker = None
    
    def register(self, name: str, handler: Callable, keywords: List[str]):
        """Register a skill handler with keywords."""
        self.skills[name] = (handler, [kw.lower() for kw in keywords])
        # Initialize automation after all skills registered
        if self.automation is None:
            self.automation = Automation(self.skills)
    
    def process(self, query: str) -> str:
        """Process query and return response."""
        if not query:
            return "I didn't catch that."
        
        q = query.lower().strip()
        
        # Handle memory queries
        if "remember" in q or "recall" in q or "what did" in q:
            return self._handle_memory_query(query)
        
        # Extract name if user introduces themselves
        if "my name is" in q or "i am" in q or "i'm" in q:
            name = self._extract_name(query)
            if name:
                self.memory.set_context("user_name", name)
                response = f"Nice to meet you, {name}! How can I help you today?"
                self.memory.add(query, response)
                return response
        
        # Use AI Decision Maker if available
        if self.use_ai_decision and self.decision_maker:
            try:
                decision = self.decision_maker.categorize(query)
                category = decision.get("category", "general")
                
                # Route based on AI decision and task type
                response = self._route_by_decision(category, query)
                if response:
                    self.memory.add(query, response)
                    return response
            except Exception as e:
                print(f"⚠️ AI routing failed: {e}, falling back to keyword matching")
        
        # Fallback to keyword matching
        response = None
        for name, (handler, keywords) in self.skills.items():
            if any(kw in q for kw in keywords):
                try:
                    response = handler(query)
                    if not response:
                        response = "Done."
                    break
                except Exception as e:
                    response = f"Error: {str(e)}"
                    break
        if not response:
            response = self._contextual_response(query)
        
        # Save to memory
        self.memory.add(query, response)
        
        return response
    
    def _route_by_decision(self, category: str, query: str) -> str:
        """Route query using task handlers (RealTimeSearch, ChatBot, Automation)."""
        q = query.lower()
        
        # Automation tasks
        if category in ["open", "close", "play", "system", "google search", "youtube search"]:
            if self.automation:
                return self.automation.route_automation(category, query)
        
        # Real-time search
        elif category == "realtime":
            return self.realtime_search.search(query)
        
        # General conversation
        elif category == "general":
            memory_context = self.memory.get_summary()
            return self.chatbot.chat(query, memory=memory_context)
        
        # Exit
        elif category == "exit":
            return "Goodbye!"
        
        return None
    
    def _route_by_category(self, category: str, query: str) -> str:
        """Route query based on AI category decision."""
        q = query.lower()
        
        # Map categories to skills
        if category in ["open", "close", "play", "system"]:
            if "apps" in self.skills:
                handler, _ = self.skills["apps"]
                try:
                    return handler(query)
                except:
                    pass
        
        elif category in ["google search"]:
            if "web" in self.skills:
                handler, _ = self.skills["web"]
                try:
                    return handler(query)
                except:
                    pass
        
        elif category in ["youtube search", "play"]:
            if "youtube" in self.skills:
                handler, _ = self.skills["youtube"]
                try:
                    return handler(query)
                except:
                    pass
        
        elif category == "exit":
            return "Goodbye!"
        
        # For general, realtime, content - let contextual handler take it
        return None
    
    def _handle_memory_query(self, query: str) -> str:
        """Handle queries about past conversation."""
        q = query.lower()
        
        # User asking what they said/asked
        if "what did i" in q or "what was" in q:
            recent = self.memory.get_recent(1)
            if recent:
                return f"You asked: '{recent[0]['user']}'"
            return "I don't recall our conversation yet."
        
        # Summary
        if "remember" in q:
            return self.memory.get_summary()
        
        return "What would you like me to recall?"
    
    def _extract_name(self, query: str) -> str:
        """Extract user's name from introduction."""
        q = query.lower()
        try:
            if "my name is" in q:
                parts = query.split("my name is", 1)[1].strip().split()
                if parts:
                    return parts[0].capitalize()
            elif "i am" in q:
                parts = query.split("i am", 1)[1].strip().split()
                if parts:
                    name = parts[0].lower()
                    if name not in ["here", "back", "ready", "fine", "good", "ok", "jarvis"]:
                        return parts[0].capitalize()
            elif "i'm" in q:
                parts = query.split("i'm", 1)[1].strip().split()
                if parts:
                    name = parts[0].lower()
                    if name not in ["here", "back", "ready", "fine", "good", "ok", "jarvis"]:
                        return parts[0].capitalize()
        except (IndexError, AttributeError):
            pass
        return None
    
    def _contextual_response(self, query: str) -> str:
        """Generate contextual response using memory."""
        q = query.lower()
        
        # Greetings
        if any(kw in q for kw in ["hi", "hello", "hey", "sup"]):
            name = self.memory.get_context("user_name")
            if name:
                return f"Hello {name}! How can I help?"
            return "Hello! How can I help?"
        
        # Thanks
        if any(kw in q for kw in ["thank", "thanks"]):
            return "You're welcome! Anything else?"
        
        # Default
        return "I don't understand. Try: 'what time is it', 'play music', 'open chatgpt', etc."
