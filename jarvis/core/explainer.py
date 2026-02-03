# core/explainer.py
from typing import List, Dict

class Explainer:
    """
    Translates execution traces into natural language explanations.
    """

    def explain(self, trace: List[object], last_decision: Dict, health: Dict) -> str:
        """
        Generate explanation from execution trace.
        """
        if not trace:
            return "I haven't done anything yet to explain."

        explanations = []

        for step in trace:
            # step is ExecutionResult object
            success = step.success
            data = step.data or {}
            
            if success:
                explanations.append(self._explain_success(step, data))
            else:
                explanations.append(self._explain_failure(step, data))

        # Add health context if relevant
        degraded = [k for k, v in health.items() if v.get("state") != "HEALTHY"]
        if degraded:
            explanations.append(f"Note: Some features were limited ({', '.join(degraded)}).")

        return " ".join(explanations)

    def _explain_success(self, step, data: Dict) -> str:
        """Explain a successful action."""
        action = data.get("action")
        target = data.get("target", "it")
        reason = data.get("reason")
        
        # Base explanation
        if action == "open":
            msg = f"I opened '{target}'."
        elif action == "close":
            msg = f"I closed '{target}'."
        elif action == "play":
            msg = f"I played '{target}'."
        elif action == "system":
            msg = f"I adjusted system settings for '{target}'."
        elif action == "file_search":
             msg = f"I searched for files matching '{target}'."
        else:
            msg = step.message # Fallback to raw message if no data

        # Append reason if available
        if reason:
            if reason == "active_window":
                msg += " It was the active window."
            elif reason == "user_request":
                pass # Implicit
            else:
                msg += f" Reason: {reason}."
                
        return msg

    def _explain_failure(self, step, data: Dict) -> str:
        """Explain a failed action."""
        error = step.error or "unknown error"
        recovery = data.get("recovery") # Did we recover?
        
        msg = f"I couldn't complete the action because of {error}."
        
        if recovery:
             msg += f" However, I {recovery}."
             
        return msg
