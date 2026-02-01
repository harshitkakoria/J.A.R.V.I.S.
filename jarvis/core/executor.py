"""Executor - Handles skill execution and routing."""
from typing import Dict, Callable, List, Optional, Any
from jarvis.utils.memory import Memory
from jarvis.core.task_handler import RealTimeSearch, ChatBot, Automation
from jarvis.core.models import ExecutionResult

class Executor:
    """Executes skills based on decisions or keywords."""
    
    def __init__(self, memory: Memory):
        self.memory = memory
        self.execution_trace = []
        
        # Initialize task handlers
        self.realtime_search = RealTimeSearch()
        self.chatbot = ChatBot()
        self.automation = None  # Will be set after skills registration
        self.skills: Dict[str, tuple] = {}

    def register(self, name: str, handler: Callable, keywords: List[str]):
        """Register a skill handler with keywords."""
        self.skills[name] = (handler, [kw.lower() for kw in keywords])
        if self.automation is None:
            self.automation = Automation(self.skills)
            
    def execute(self, decision: Dict) -> ExecutionResult:
        """
        Unified entry point.
        Accepts either a single-step decision or a multi-step plan.
        """
        self.execution_trace = [] # Reset trace
        
        if decision.get("plan"):
            return self._execute_plan(decision["plan"])
        else:
            # Convert single decision to step format
            return self._execute_step(decision)

    def _execute_plan(self, plan: List[Dict]) -> ExecutionResult:
        """Execute a list of steps sequentially."""
        results = []
        for i, step in enumerate(plan):
            result = self._execute_step(step)
            # Store trace of logic, result.data usually has more info?
            # User wants trace of results
            self.execution_trace.append(result)
            
            if not result.success:
                return ExecutionResult(
                    success=False,
                    message=f"Stopped at step {i+1}: {result.message}",
                    data=self.execution_trace,
                    error=result.error
                )
            results.append(result.message)
        
        return ExecutionResult(
            success=True,
            message="Sequentially executed: " + " then ".join(results),
            data=self.execution_trace
        )

    def _execute_step(self, step: Dict) -> ExecutionResult:
        """Execute a single step with validation."""
        category = step.get("category")
        args = step.get("args")  # This is usually the refined 'action' or the raw query depending on source
        query = step.get("query", args) # fallback
        confidence = step.get("confidence", 1.0)

        # 1. Safety Guard: Block execution on low confidence or missing category
        if category is None:
             return ExecutionResult(False, "I need more details before doing that.", error="NO_CATEGORY")
             
        if confidence < 0.75:
             # Safety net if Brain missed it
             return ExecutionResult(False, "Command unclear, awaiting clarification.", error="LOW_CONFIDENCE")

        # Map to existing execution logic
        # execute_decision returns ExecutionResult or str
        try:
            # We pass 'args' (the action) as the second argument which enters 'execute_decision' as 'action'
            result = self.execute_decision(category, args, query)
            
            # Standardize result
            if not isinstance(result, ExecutionResult):
                result = ExecutionResult(True, str(result))
            
            # Normalizing Trace: Always append result
            self.execution_trace.append(result)
            
            if not result.success:
                return result

            # Validation
            if not self._validate(step, result):
                return ExecutionResult(False, "Post-action validation failed", error="Validation Failed")
            
            return result
            
        except Exception as e:
            return ExecutionResult(False, "Execution failed", error=str(e))

    def _validate(self, step: Dict, result: ExecutionResult) -> bool:
        """
        Minimal validation logic.
        """
        category = step.get("category")
        args = step.get("args")
        
        # 4. Basic Validation
        if category == "open":
            # Ensure we actually have something to open
            return bool(args) and len(args.strip()) > 0
            
        return True

    def execute_plan(self, plan: List[dict]) -> str:
        """Legacy wrapper for backward compatibility if needed."""
        # Brain calls this and expects a string response usually
        res = self._execute_plan(plan)
        return res.message

    def execute_decision(self, category: str, action: str, query: str) -> Any:
        # Changed to Any because it returns str logic-wise but effectively Any
        # Actually in Acceptance tests we mock this, so it returns ExecutionResult.
        # But real implementation returns str or ExecutionResult?
        # Automation returns str usually. 
        # We need to wrap it if it returns str.
        
        """Execute a command based on AI category decision."""
        q = query.lower() if query else ""
        
        # Automation tasks (Apps, System, Web, Media, Files)
        if category in ["open", "close", "play", "system", "google search", "youtube search", "files"]:
            if self.automation:
                # 3. Precision: Reconstruct command string for handlers that rely on keywords
                # e.g. apps.handle("youtube") fails, but apps.handle("open youtube") works
                if action and category not in action.lower():
                     target = f"{category} {action}"
                else:
                     target = action if action else query
                return self.automation.route_automation(category, target)
        
        # Real-time search
        elif category == "realtime":
            return self.realtime_search.search(query)
        
        # General conversation
        elif category == "general":
            # 2. Safety: General must NEVER trigger side effects (action-like keywords)
            if self._looks_like_action(query):
                return ExecutionResult(
                    False, 
                    "What exactly do you want me to do?", 
                    error="AMBIGUOUS_GENERAL"
                )
            
            memory_context = self.memory.get_summary()
            return self.chatbot.chat(query, memory=memory_context)
        
        # Exit
        elif category == "exit":
            return ExecutionResult(True, "Goodbye!")
            
        return ExecutionResult(False, f"Unknown category: {category}")

    def _looks_like_action(self, query: str) -> bool:
        """Check if query contains action verbs that shouldn't be in 'general'."""
        q = query.lower()
        # List of verbs that imply control/action
        verbs = ["open ", "close ", "play ", "start ", "launch ", "run ", "kill ", "exit ", "find ", "search ", "locate "]
        return any(v in q for v in verbs)

    def execute_fallback(self, query: str) -> Optional[str]:
        """Fallback to keyword matching if AI fails or is disabled."""
        q = query.lower()
        
        for name, (handler, keywords) in self.skills.items():
            if any(kw in q for kw in keywords):
                try:
                    response = handler(query)
                    if not response:
                        return "Done."
                    return response
                except Exception as e:
                    return f"Error: {str(e)}"
        
        return None
