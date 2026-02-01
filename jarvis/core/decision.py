"""Decision Making Model using Groq."""
import os
import groq
import json
from rich.console import Console
from dotenv import load_dotenv
from jarvis.utils.helpers import is_ambiguous

load_dotenv()

console = Console()


class DecisionMaker:
    """AI-powered decision making for query categorization using Groq."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = groq.Groq(api_key=self.api_key)
            print("[+] Groq AI Decision Maker initialized")
        else:
            self.client = None
            print("[!] GROQ_API_KEY not found. AI decision making disabled.")
        
        self.functions = [
            "exit", "general", "realtime", "open", "close", 
            "play", "system", "content", "google search", 
            "youtube search", "reminder"
        ]
        
        # Optimized system prompt for Llama 3 on Groq (JSON Mode)
        self.preamble = """You are a precise Command classifier.
Your job is to categorize user queries into specific function calls and output JSON.

Available Functions:
1. general (query) -> For conversational questions, math, facts, or greetings.
2. realtime (query) -> For questions requiring up-to-date live data (news, stock prices, weather, current events).
3. open (app_name) -> To launch an application or website.
4. close (app_name) -> To close an application.
5. play (song_name) -> To play music or video.
6. system (action) -> For volume control, mute/unmute, screenshot.
7. google search (topic) -> For explicit web searches.
8. youtube search (topic) -> For explicit YouTube searches.
9. files (action) -> To create, delete, or find/search for files.
10. exit -> When user says goodbye.

Rules:
- Output ONLY a valid JSON object.
- Format (Single Step): {"category": "function_name", "args": "content", "confidence": 0.0-1.0, "alternatives": ["alt 1", "alt 2"]}
- Format (Multi-Step): {"plan": [{"category": "cat1", "args": "args1"}, {"category": "cat2", "args": "args2"}], "confidence": 0.0-1.0}
- Use "plan" ONLY if the user asks for multiple distinct actions.
- "confidence" should be a float between 0.0 and 1.0 indicating your certainty.
- If unsure or ambiguous, set confidence < 0.75 and provide 2-3 logical alternatives.
- Do not write any explanations before or after the JSON.
- Context Awareness: If 'context' is provided, use 'active_window' or 'app_name' to resolve pronouns like 'it', 'this', 'close it', 'pause'.
"""
    
    def categorize(self, query: str, memory=None, context=None) -> dict:
        """Categorize query using Rules (Fast) then Groq AI (Smart)."""
        
        # 0. Ambiguity Guard (v3.6) - UPDATED v4.0
        # Check against memory and CONTEXT
        # Note: Brain handles the hard block. Here we use context to potentially resolve it in Rule Matching.
        
        # 1. Fast Rule Matching
        rule_decision = self._match_rules(query, context)
        if rule_decision:
            return rule_decision

        if not self.client:
            return {
                "query": query,
                "category": "general",
                "args": query,
                "confidence": 1.0 # Fallback assumes general conversation if no AI
            }

        try:
            # v4.0: Context Injection
            system_prompt = self.preamble
            user_content = query
            if context:
                ctx_str = f"\nSystem Context: Active Window='{context.get('active_window')}', App='{context.get('app_name')}'"
                system_prompt += ctx_str
                # We can also append to user message for stronger attention
                # user_content = f"{query} [Context: {context.get('app_name')}]"

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=100,
                temperature=0.1,  # Low temperature for deterministic output
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"} # Enforce JSON mode
            )
            
            content = response.choices[0].message.content.strip()
            decision_data = json.loads(content)
            
            # Normalize keys if needed (AI determines structure but let's be safe)
            category = decision_data.get("category", "general")
            args = decision_data.get("args", query)
            confidence = decision_data.get("confidence", 0.5)
            alternatives = decision_data.get("alternatives", [])
            plan = decision_data.get("plan", [])
            
            return {
                "query": query,
                "category": category,
                "args": args,
                "confidence": confidence,
                "alternatives": alternatives,
                "plan": plan
            }
        
        except Exception as e:
            console.print(f"[red]Decision Error: {e}[/red]")
            return {
                "query": query,
                "category": "general",
                "args": query,
                "confidence": 0.0 # Error implies zero confidence
            }
    
    def _match_rules(self, query: str, context=None) -> dict:
        """Match query against hardcoded rules for speed."""
        q = query.lower().strip()
        
        # Skip rules if multi-step indicators are present (Let AI handle plans)
        if " and " in q or " then " in q or "," in q:
            return None
        
        # App/Web Opening
        if q.startswith("open ") or q.startswith("launch ") or q.startswith("start "):
            action = q.split(" ", 1)[1].strip()
            
            # v3.6 Safety: Rules must respect ambiguity
            if action in ["it", "this", "that", "them", "those", "something", "anything"]:
                 # v4.0 Exception: If we have context, allow it?
                 # No, "Open it" usually implies opening a file or something else,
                 # "active window" is already open.
                 # "Open it" might mean "Open the selected file". Not implemented yet.
                 # So we stick to 0.0 confidence.
                 return {
                     "query": query,
                     "category": "open",
                     "args": action,
                     "confidence": 0.0,
                     "needs_clarification": True,
                     "alternatives": [],
                     "plan": []
                 }
                 
            return {"query": query, "category": "open", "args": action, "confidence": 0.95, "alternatives": [], "plan": []}
            
        # App Closing
        if q.startswith("close ") or q.startswith("exit ") or q.startswith("kill "):
            action = q.split(" ", 1)[1]
            
            # Contextual "Close it"
            if action in ["it", "this", "that"]:
                if context and context.get("app_name"):
                    # Resolve to active app
                    target_app = context.get("app_name")
                    return {
                        "query": query, 
                        "category": "close", 
                        "args": target_app, 
                        "confidence": 0.95, # High confidence now!
                        "alternatives": [], 
                        "plan": []
                    }
                else:
                     return {"query": query, "category": "close", "args": action, "confidence": 0.0, "needs_clarification": True, "alternatives": [], "plan": []}

            return {"query": query, "category": "close", "args": action, "confidence": 0.95, "alternatives": [], "plan": []}
            
        # YouTube/Media
        if q.startswith("play ") or q.startswith("watch "):
            action = q.split(" ", 1)[1]
            return {"query": query, "category": "play", "args": action, "confidence": 0.95, "alternatives": [], "plan": []}
            
        # System
        if any(x in q for x in ["volume", "mute", "screenshot", "capture"]):
             return {"query": query, "category": "system", "args": q, "confidence": 0.95, "alternatives": [], "plan": []}
             
        return None
