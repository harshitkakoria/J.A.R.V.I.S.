"""Brain - Routes commands to skills."""
from typing import Dict, Callable, List
from jarvis.utils.memory import Memory
from jarvis.utils.helpers import clean_text
from jarvis.core.decision import DecisionMaker
from jarvis.core.executor import Executor
from jarvis.core.models import ExecutionResult
from jarvis.core.context import ContextManager
from jarvis.core.vision import VisionManager
from jarvis.core.health import HealthManager
from jarvis.core.capabilities import build_capability_manifest
from jarvis.core.explainer import Explainer

class Brain:
    """Core logic engine combining Memory, Decision, and Execution."""
    
    def __init__(self, use_ai_decision=True):
        self.memory = Memory()
        self.executor = Executor(self.memory)
        self.context_manager = ContextManager()
        self.vision_manager = VisionManager()
        self.health_manager = HealthManager() # v7.2 Autonomy
        self.explainer = Explainer() # v7.4 Explanation
        
        self.use_ai_decision = use_ai_decision
        self.decision_maker = None # Will be set below
        
        # Check critical health on startup
        health_status = self.health_manager.check_all()
        self.capabilities = build_capability_manifest(health_status)
        
        if self.capabilities["llm_reasoning"] == "ENABLED" and use_ai_decision:
            try:
                self.decision_maker = DecisionMaker()
                print("[+] AI Decision Maker initialized")
            except Exception as e:
                print(f"[!] AI Decision Maker init failed: {e}")
                self.use_ai_decision = False
        else:
             print("[!] AI Decision Disabled (Offline or Missing Key)")
             self.use_ai_decision = False
    
    def register(self, name: str, handler: Callable, keywords: List[str]):
        """Register a skill handler with keywords."""
        self.executor.register(name, handler, keywords)
    
    def process(self, query: str) -> str:
        """
        Process a user query through the pipeline:
        Normalize -> Context -> Ambiguity Check -> Decide -> Execute
        """
        if not query:
            return "I didn't catch that."
        
        # 0. Normalize Query
        # Remove "can you", fix typos, map synonyms
        # Note: We keep original query for some context if needed, but for processing we use cleaned
        raw_query = query
        query = clean_text(query)
        q = query # clean_text already lowercases and strips
        
        # 0.1 Get System Context (v4.0)
        # Identify active window/process
        system_context = self.context_manager.get_context()
        
        # 0.4 Refresh Capabilities (v7.2)
        # Check health periodically (cached in manager)
        health_status = self.health_manager.check_all()
        self.capabilities = build_capability_manifest(health_status)
        
        # 0.5 System Status Report (v7.2)
        if "status" in q and ("system" in q or "report" in q or "health" in q or "operational" in q):
            return self._generate_status_report(health_status, self.capabilities)
            
        # 0.6 Explanation Mode (v7.4)
        # Check for "Why" / "Explain" triggers
        # CRITICAL: Context Sensitivity - Only answer "Why" if we have a recent trace.
        # If trace is empty, "Why is sky blue?" should fall through to AI General.
        explanation_triggers = ["why", "explain", "what happened", "reason"]
        is_explanation = any(t in q.split() for t in explanation_triggers)
        # Also simple "why?" or "why did you..."
        if q.startswith("why"):
            is_explanation = True
            
        if is_explanation and self.executor.execution_trace:
             # We have actions to explain!
             # Explainer might need last decision too, but for now trace is the source of truth.
             last_decision = {} 
             return self.explainer.explain(self.executor.execution_trace, last_decision, health_status)
        


        # 0.2 Check for Vision Triggers (v6.0)
        # Explicit request to see/read screen
        vision_triggers = ["look at this", "look at my screen", "what is on my screen", "read this", "describe this", "what am i looking at"]
        if any(vt in q for vt in vision_triggers):
             if self.capabilities["vision"] != "ENABLED":
                 return "I cannot see the screen right now. Vision module is unavailable."
             return self.vision_manager.analyze(query)
        
        # 0.3 Handle File Selection (v7.1)
        # If we have file candidates in context and user says "first one", etc.
        if self.memory.get_context("file_candidates"):
             selection_result = self._handle_file_selection(query)
             if selection_result:
                 return selection_result
        
        # 0. Handle Pending Clarification
        pending = self.memory.get_pending_clarification()
        if pending:
            return self._resolve_clarification(query, pending)

        # 0.5 Ambiguity Guard (v3.6 Fix + v4.0 Context)
        # Explicitly block unresolved pronouns before anything else
        # UNLESS we have a clear context (Active Window)
        has_context = bool(system_context.get("active_window"))
        
        if any(p in q.split() for p in ["it", "this", "that", "them", "those"]):
            if not self.memory.has_recent_entity() and not has_context:
                self.memory.set_pending_clarification({
                    "original_query": query,
                    "reason": "unresolved_pronoun"
                })
                # User asked for: "What do you want me to open?" specifically for "Can you open it?"
                # But generic "it" might apply to "close it". 
                # I'll use a generic safe response or strict user request?
                # User said: "The exact bug... The minimal, correct fix... return 'What do you want me to open?'"
                # But that's specific to 'open'. 
                # I will output "What do you want me to do with 'it'?" or similar?
                # Actually, later user example: "User: Can you open it? Jarvis: What do you want me to open?"
                # I should probably detect the verb if I want to be that smart, but user said "minimal".
                # Let's stick to the user's specific block for now, or make it slightly dynamic if easy.
                # "Do you want me to open it?" -> "What do you want me to open?"
                # "Do you want me to close it?" -> "What do you want me to close?"
                # Minimal fix:
                # return "What do you want me to open?" (If I strictly follow the "open it" example logic)
                # But wait, "close it" shouldn't say "what do you want me to OPEN".
                # I will try to be slightly smart or generic.
                # User suggested code: return "What do you want me to open?" implies they are thinking of the "open" case.
                # I'll use the user's snippet but maybe make it generic? 
                # "What do you want me to open" is what they Asked for.
                # I will check if "open" is in query?
                if "open" in q:
                     return "What do you want me to open?"
                return "I'm not sure what 'it' refers to. Could you clarify?"
        
        # Handle memory queries (To be moved to Memory Layer in v3.4)
        if any(kw in q for kw in ["remember", "recall", "what did", "what i asked", "what i told", "what was"]):
            return self._handle_memory_query(query)
        
        # Extract name if user introduces themselves
        if "my name is" in q or "i am" in q or "i'm" in q:
            name = self._extract_name(query)
            if name:
                self.memory.set_context("user_name", name)
                response = f"Nice to meet you, {name}! How can I help you today?"
                self.memory.add(query, response)
                return response
        
        response = None
        
        # Use AI Decision Maker if available
        if self.use_ai_decision and self.decision_maker:
            try:
                # v4.0: Pass system context to AI
                decision = self.decision_maker.categorize(query, memory=self.memory, context=system_context)
                
                category = decision.get("category", "general")
                args = decision.get("args", query)
                confidence = decision.get("confidence", 0.0)
                alternatives = decision.get("alternatives", [])
                plan = decision.get("plan", [])
                
                # Confidence Check
                # Apply to ALL categories (including general) for safety
                if confidence < 0.75:
                    # Low confidence on an action -> Clarify
                    self.memory.set_pending_clarification({
                        "original_query": query,
                        "candidate_decision": decision
                    })
                    return "I'm not entirely sure. Could you clarify?"
                
                # Execute Plan or Single Decision
                # Use unified executor entry point for validation/tracing support
                result = self.executor.execute(decision)
                
                # Check for Ambiguous General Block -> Fallback to Keywords
                if not result.success and result.error == "AMBIGUOUS_GENERAL":
                    print("[!] Ambiguous General: Falling back to keywords")
                    response = None # Trigger fallback below
                else:
                    response = result
                
            except Exception as e:
                print(f"[!] AI routing failed: {e}, falling back to keyword matching")
        
        # Fallback to keyword matching if AI failed or didn't return a response
        if not response:
            response = self.executor.execute_fallback(query)
            
        # Contextual Fallback
        if not response:
            response = self._contextual_response(query)
        
        # Format response for output
        output_text = response
        tag = "conversation"
        
        if isinstance(response, ExecutionResult):
            output_text = response.message
            tag = "action"
            
        # Save to memory
        self.memory.add(query, output_text, tag=tag)
        
        return output_text
    
    def _handle_memory_query(self, query: str) -> str:
        """Handle queries about past conversation."""
        q = query.lower()
        
        # User asking what they said/asked
        if any(kw in q for kw in ["what did i", "what was", "what i asked", "what i told"]):
            recent = self.memory.get_recent(1)
            if recent:
                return f"You asked: '{recent[0]['user']}'"
            return "I don't recall our conversation yet."
        
        # Summary
        if "remember" in q:
            if "what" in q or "do you" in q: # "Do you remember..." or "What do you remember..."
                 # Trigger semantic search
                 # Extract the core topic? Or just search the whole query?
                 # Search whole query is simplest.
                 semantic_fact = self.memory.recall_semantic(query)
                 if semantic_fact:
                     return f"I seem to recall you mentioning: '{semantic_fact}'. Is that correct?"
                 return self.memory.get_summary()
            
            # Simple "remember" command might be summary request still?
            return self.memory.get_summary()

        # General recall query (e.g. "What is my favorite color?")
        # If it didn't match specific "what did I say", try semantic
        semantic_fact = self.memory.recall_semantic(query)
        if semantic_fact:
            return f"I seem to recall you mentioning: '{semantic_fact}'. Is that correct?"
        
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
                    if name not in ["here", "back", "ready", "fine", "good", "ok", "jarvis", "greeting", "not", "asking", "telling", "talking", "speaking"]:
                        return parts[0].capitalize()
        except (IndexError, AttributeError):
            pass
        return None
    
    def _resolve_clarification(self, query: str, pending: dict) -> str:
        """Handle user response to a clarification question."""
        q = query.lower()
        candidate = pending.get("candidate_decision", {})
        category = candidate.get("category")
        args = candidate.get("args")
        alternatives = candidate.get("alternatives", [])
        
        selected_action = None
        
        # 1. Option Selection ("first one", "option 2")
        if "first" in q or "option 1" in q:
             # Default candidate is technically option 1, but if alternatives listed, maybe option 1 is the candidate?
             # Let's assume candidate is option 1, alternatives start at 2.
             selected_action = (category, args)
        elif "second" in q or "option 2" in q:
             if len(alternatives) >= 1:
                 # Alternatives might be just strings "open spotify" or full objects? 
                 # Our decisionMaker output alternatives as strings ["search youtube", "play ..."]
                 # We need to parse them back or just treat them as new queries.
                 # Treating as new query is safest.
                 return self.process(alternatives[0])
        elif "third" in q or "option 3" in q:
             if len(alternatives) >= 2:
                 return self.process(alternatives[1])

        # 2. Confirmation
        if not selected_action and any(kw in q for kw in ["yes", "yeah", "yep", "sure", "ok", "do it"]):
             selected_action = (category, args)
             
        if selected_action:
            self.memory.clear_pending_clarification()
            
            # Execute
            if pending.get("candidate_decision", {}).get("plan"):
                 # if valid plan was the candidate
                 response = self.executor.execute_plan(pending["candidate_decision"]["plan"])
            else:
                cat, arg_val = selected_action
                response = self.executor.execute_decision(cat, arg_val, pending.get("original_query", ""))
            
            # Format and Save
            output_text = response
            tag = "conversation"
            if isinstance(response, ExecutionResult):
                output_text = response.message
                tag = "action"
            self.memory.add(query, output_text, tag=tag)
            return output_text

        # 2. Correction (User provided a specific app/value)
        # If user says "No, Spotify" or just "Spotify"
        # Ideally we'd re-process this logic smarter, but for now:
        # If it's a correction, we treat it as a new command contextually linked?
        # Simplest v3 approach: Treat as new command, clear pending. 
        # The new command will likely hit the rule match or AI again.
        
        self.memory.clear_pending_clarification()
        return self.process(query)

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

    def _handle_file_selection(self, query: str) -> str:
        """Handle file selection confirmation (e.g. "first one", "option 2")."""
        q = query.lower()
        import re
        
        # Extract number
        selection = None
        
        if "first" in q or "option 1" in q or q == "1":
            selection = 1
        elif "second" in q or "option 2" in q or q == "2":
            selection = 2
        elif "third" in q or "option 3" in q or q == "3":
            selection = 3
        elif "fourth" in q or "option 4" in q or q == "4":
            selection = 4
        elif "fifth" in q or "option 5" in q or q == "5":
            selection = 5
            
        # Also simple numbers "open 1"
        match = re.search(r"(\d+)", q)
        if match and not selection:
             # Be careful not to match random numbers if query is "open mp3"
             # Only if query is short or explicit?
             # For now trust the context lock.
             try:
                 val = int(match.group(1))
                 if 1 <= val <= 5:
                     selection = val
             except: pass

        if "yes" in q or "open it" in q:
             # If only 1 candidate, selection defaults to 1 (handled by FileManager logic usually?)
             # But FileManager.open_confirmed takes an index.
             # If we have candidates, and user says "yes", imply 1 ONLY if count == 1
             candidates = self.memory.get_context("file_candidates")
             if candidates and len(candidates) == 1:
                 selection = 1
        
        if selection:
             # Access FileManager via Executor
             if hasattr(self.executor, "file_manager"):
                 result = self.executor.file_manager.open_confirmed(selection)
                 # Clear context on success
                 if result.success:
                     self.memory.set_context("file_candidates", None)
                     
                 # Retrieve message
                 output_text = result.message
                 self.memory.add(query, output_text, tag="action")
                 return output_text
                 
        return None

    def _generate_status_report(self, health: Dict, caps: Dict) -> str:
        """Generate a natural language status report."""
        report = ["System Status Report:"]
        
        # Internet
        net = health.get("internet", {})
        state = net.get("state")
        if state == "HEALTHY":
            report.append("✓ Internet: Online")
        else:
            report.append(f"❌ Internet: Offline ({net.get('error', 'Unknown')})")
            
        # LLM
        llm = health.get("llm", {})
        if llm.get("state") == "HEALTHY":
            report.append("✓ Intelligence: Online (Groq)")
        else:
            report.append(f"⚠️ Intelligence: Limited ({llm.get('error', 'Unknown')})")
            
        # Vision
        vis = health.get("vision", {})
        if vis.get("state") == "HEALTHY":
            report.append("✓ Vision: Online")
        else:
            report.append("⚠️ Vision: Unavailable")
            
        # Summary
        if caps["llm_reasoning"] == "DISABLED":
            report.append("\nNote: I am running in Offline Mode. I can only perform basic automation commands.")
            
        return "\n".join(report)
