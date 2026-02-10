"""Decision Making Model using Google Gemini."""
import os
import json
from dotenv import load_dotenv
from jarvis.core.llm import LLM

load_dotenv()

try:
    from rich.console import Console  # type: ignore
    console = Console()
except Exception:
    # `rich` is optional; fall back to plain printing if not installed.
    class _ConsoleFallback:
        def print(self, *args, **kwargs):
            print(*args)

    console = _ConsoleFallback()


class DecisionMaker:
    """AI-powered decision making for query categorization using Gemini."""
    
    def __init__(self):
        self.llm = LLM()
        if self.llm.client:
            print("[+] Groq AI Decision Maker initialized")
        else:
            print("[!] AI decision making disabled (LLM Init Failed).")
        
        self.functions = [
            "exit", "general", "realtime", "weather", "open", "close", 
            "play", "system", "content", "context", "google search", 
            "youtube search", "reminder", "files",
            "document_generation"
        ]
        
        # Optimized system prompt for Llama 3 on Groq (JSON Mode)
        self.preamble = """You are a precise Command classifier.
Your job is to categorize user queries into specific function calls and output JSON.

Available Functions:
1. general (query) -> Conversational questions, math, facts, chit-chat.
2. realtime (query) -> Live data & News. "Who is the president?", "Stock price of Apple", "Score of the game", "Latest news on AI".
3. weather (query) -> Weather.
4. open (app_name) -> Launch app/site.
5. close (app_name) -> Close app.
6. play (song_name) -> Media.
7. system (action) -> PC Control. "volume up", "brightness 100%", "screenshot", "wifi off".
    - Media: "play music", "next track", "pause video".
    - Status: "cpu usage", "how much ram", "battery level".
    - Clipboard: "read clipboard", "clear clipboard", "copy hello world".
8. google search (topic) -> Web search.
9. youtube search (topic) -> Video search.
10. files (action, details) -> File Management.
    - Search: {"action": "search", "name_contains": "invoice", "time_range": "yesterday", "type": "pdf", "location": "downloaded"}
    - Search Folders: {"action": "search", "type": "folder", "name_contains": "project"}
    - Create: {"action": "create", "name": "notes.txt", "content": "optional"} (For blank/simple files)
    - Delete: {"action": "delete", "name": "notes.txt", "confirm": true}
11. document_generation (topic) -> For AI WRITING (essays, reports). {"topic": "cover letter", "format": "pdf"}
12. image_generation (prompt) -> Generate images.
13. context (query) -> Current Time, Current Date, JARVIS Identity ("who are you"). (NOT user identity or facts).
14. exit -> Quit.

Rules:
- Output ONLY a valid JSON object.
- **CRITICAL**: Distinguish between `files` (System ops) and `document_generation` (AI Writing).
  - "Create a new text file" -> `files` (action="create")
  - "Write a story and save as PDF" -> `document_generation`
  - "Find my resume" -> `files` (action="search")
  - "Delete that file" -> `files` (action="delete")
- Use specific functions over 'general'.
- Format: {"category": "function_name", "args": {arguments}, "confidence": 0.0-1.0}
- Example: "Find pdfs from yesterday" -> {"category": "files", "args": {"action": "search", "type": "pdf", "time_range": "yesterday"}}
- Example: "Find that PDF I downloaded yesterday" -> {"category": "file_search", "args": {"type": "pdf", "time_range": "yesterday", "action": "downloaded"}}
- Use "plan" ONLY if the user asks for multiple distinct actions.
- "confidence" should be a float between 0.0 and 1.0 indicating your certainty.
- If unsure or ambiguous, set confidence < 0.75 and provide 2-3 logical alternatives.
- Do not write any explanations before or after the JSON.
- Context Awareness: If 'context' is provided, use 'active_window' or 'app_name' to resolve pronouns like 'it', 'this', 'close it', 'pause'.
-Don't give any explanation before or after the JSON.
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

        if not self.llm.client:
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

            # Call Gemini via LLM Wrapper
            content = self.llm.chat(
                prompt=user_content,
                system_instruction=system_prompt,
                json_mode=True
            )
            
            # content is already the string response
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
        
        # v7.6 Hardcoded Greetings (Prevent LLM Hallucinations on short inputs)
        # Strip punctuation for robust matching "hello!" -> "hello"
        clean_q = q.strip(".,!? ")
        if clean_q in ["hello", "hi", "hey", "hola", "greetings", "good morning", "good evening", "how are you", "what's up"]:
             return {
                "query": query,
                "category": "general",
                "args": query,
                "confidence": 1.0,
                "alternatives": [],
                "plan": []
            }
        
        # Skip rules if multi-step indicators are present (Let AI handle plans)
        # v7.2 - Allowing rules to run even on "and" because AI is fallback?
        # Actually, if we return a single step for "open X and Y", we lose the second part.
        # But if the rule matches "open X and Y" as a whole, it likely fails.
        # However, for Automation Bias, we want "open chrome" to hit automation.
        # If user says "open chrome and search x", rule "open" might catch "chrome and search x" as arg.
        # This is risky.
        # SAFE OPTION: Keep this skipped. Let AI handle complex sentences.
        # The prompt BIAS is what matters.
        if " and " in q or " then " in q or "," in q:
            return None
        
        # App/Web Opening
        if q.startswith("open ") or q.startswith("launch ") or q.startswith("start "):
            action = q.split(" ", 1)[1].strip()
            
            # v7.3 Fix: Don't hijack file commands!
            # If user says "open pdf", "open file", "open downloaded", pass to AI for 'file_search'
            if any(kw in action for kw in ["pdf", "doc", "txt", "image", "photo", "file", "downloaded", "presentation", "ppt", "excel", "sheet"]):
                return None
            
            # v3.6 Safety: Rules must respect ambiguity
            if action in ["it", "this", "that", "them", "those", "something", "anything"]:
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
             
        # Google Search (Explicit Rule)
        if q.startswith("search "):
            # Exception: "Search file" should go to files (handled by AI or add rule later if needed)
            if any(kw in q for kw in ["file", "pdf", "doc", "downloaded"]):
                return None # Let AI handle file_search
                
            topic = q.split(" ", 1)[1]
            return {"query": query, "category": "google search", "args": topic, "confidence": 0.95, "alternatives": [], "plan": []}

        # v7.3 Fix: "Find" rule
        if q.startswith("find "):
             action = q.split(" ", 1)[1]
             # If it looks like a file search, route to AI (file_search params are complex)
             # OR map to file_search with raw args and let FileManager parse?
             # FileManager expects {"args": {"type":...}}
             # If we return category="file_search", args=action -> Executor maps it to FileManager.handle({"category":"file_search", "args": action})
             # FileManager._parse_constraints handles natural language now?
             # Looking at FileManager code: 
             # args = intent.get("args", {})
             # constraints = self._parse_constraints(args)
             # _parse_constraints expects a DICT like {"type": "pdf"}. 
             # It does NOT appear to handle a raw string "pdf i downloaded today".
             # So we MUST let AI parse the natural language into JSON.
             
             return None # Let AI parse "find pdf..." into {"type": "pdf", ...}

        return None
