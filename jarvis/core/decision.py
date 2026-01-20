"""Decision Making Model using Groq."""
import os
import groq
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()


class DecisionMaker:
    """AI-powered decision making for query categorization using Groq."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = groq.Groq(api_key=self.api_key)
            print("✅ Groq AI Decision Maker initialized")
        else:
            self.client = None
            print("⚠️ GROQ_API_KEY not found. AI decision making disabled.")
        
        self.functions = [
            "exit", "general", "realtime", "open", "close", 
            "play", "system", "content", "google search", 
            "youtube search", "reminder"
        ]
        
        # Optimized system prompt for Llama 3 on Groq
        self.preamble = """You are a precise Command classifier.
Your job is to categorize user queries into specific function calls.

Available Functions:
1. general (query) -> For conversational questions, math, facts, or greetings.
2. realtime (query) -> For questions requiring up-to-date live data (news, stock prices, weather, current events).
3. open (app_name) -> To launch an application or website.
4. close (app_name) -> To close an application.
5. play (song_name) -> To play music or video.
6. system (action) -> For volume control, mute/unmute, screenshot.
7. google search (topic) -> For explicit web searches.
8. youtube search (topic) -> For explicit YouTube searches.
9. exit -> When user says goodbye.

Rules:
- Output ONLY the function call format: "function_name (content)".
- Do not write any explanations.
- If unsure, use "general (original_query)".
- Map "price of X", "value of X" to realtime.
- Map "weather in X" to realtime.
- Map "increase volume", "mute" to system.

Examples:
User: "Hi" -> general (Hi)
User: "Price of BTC" -> realtime (Price of BTC)
User: "Open Notepad" -> open (Notepad)
User: "Play Believer" -> play (Believer)
User: "Turn up volume" -> system (volume up)
"""
    
    def categorize(self, query: str) -> dict:
        """Categorize query using Groq AI."""
        if not self.client:
            return {
                "query": query,
                "decision": "error",
                "category": "general",
                "action": query
            }

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=60,
                temperature=0.1,  # Low temperature for deterministic output
                messages=[
                    {"role": "system", "content": self.preamble},
                    {"role": "user", "content": query}
                ]
            )
            
            decision = response.choices[0].message.content.strip()
            
            # Clean up potential extra text (sometimes Llama can be chatty despite instructions)
            if "\n" in decision:
                decision = decision.split("\n")[0]
            
            # Parse decision
            category = self._parse_decision(decision)
            
            return {
                "query": query,
                "decision": decision,
                "category": category,
                "action": self._extract_action(decision)
            }
        
        except Exception as e:
            console.print(f"[red]Decision Error: {e}[/red]")
            return {
                "query": query,
                "decision": "error",
                "category": "general",
                "action": query
            }
    
    def _parse_decision(self, decision: str) -> str:
        """Extract category from decision text."""
        decision_lower = decision.lower()
        for func in self.functions:
            # Check for "func (" format to be safer
            if decision_lower.startswith(f"{func}"):
                return func
        return "general"
    
    def _extract_action(self, decision: str) -> str:
        """Extract action details from decision."""
        try:
            # Extract content inside parentheses
            if "(" in decision and decision.endswith(")"):
                start = decision.find("(") + 1
                end = decision.rfind(")")
                return decision[start:end].strip()
        except:
            pass
        return decision
