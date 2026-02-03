# core/recovery.py
from jarvis.core.models import ExecutionResult

class RecoveryManager:
    """
    Handles execution failures by suggesting retries or alternatives.
    """
    
    def attempt_recovery(self, failure: ExecutionResult, context: dict) -> ExecutionResult:
        """
        Analyze failure and decide next step.
        context: {
            "category": str,
            "args": str,
            "query": str,
            "executor": Executor,
            "alternatives": list
        }
        """
        error = str(failure.error or "").lower()
        msg = failure.message.lower()
        
        # 1. Permission / Security
        if "permission" in error or "access denied" in error or "admin" in error:
            return ExecutionResult(
                False,
                "I don't have permission to do that. You might need to run me as Administrator.",
                error="PERMISSION"
            )

        # 2. Not Installed / Not Found -> Suggest Alternative
        if "not installed" in error or "not found" in error or "unrecognized" in error:
            return self._suggest_alternative(context)

        # 3. Timeout / Not Responding -> Retry ONCE
        if "timeout" in error or "not responding" in error or "busy" in error:
            return self._retry(context)

        # 4. Unknown / Fatal
        return ExecutionResult(
            False,
            f"I couldn't complete that. Error: {failure.message}",
            error="FATAL"
        )

    def _retry(self, context) -> ExecutionResult:
        """Retry the action once."""
        if context.get("retried"):
            return ExecutionResult(False, "Retry failed. The app is not responding.", error="RETRY_LIMIT")

        print(f"[Recovery] Retrying action: {context['category']} {context['args']}")
        context["retried"] = True
        
        # Re-execute via executor
        # We need to call back into executor.execute_decision
        # Ensure we don't infinitely loop if it keeps failing.
        # The executor helper calling this must handle the retry limit or pass a flag?
        # Ideally, we return a special result asking Executor to retry?
        # Or we call it here.
        executor = context.get("executor")
        if executor:
            # We must pass a flag to prevent infinite recursion if it fails again and comes back here?
            # context is passed by reference, so setting retried=True helps if the caller persists context.
            # But here we are calling execute_decision which creates a NEW context usually?
            # We need to be careful.
            # Actually, standard Executor.execute_decision doesn't take context.
            # It just runs. If it fails, Executor calls RecoveryManager again.
            # We need a way to tell Executor "This is a retry".
            
            # Simple approach: Return a result that SAYS "Retrying..." and let the *caller* (Executor) handle the loop?
            # OR execute it here and return the result.
            # If we execute here, and it fails, Executor sees a failure result.
            # Does Executor call RecoveryManager recursively?
            # Yes, if we use the same `execute_step` method.
            # We should call the lower level `execute_decision` which does NOT have recovery logic wrapper?
            # Yes, `execute_step` has the wrapper. `execute_decision` is the raw handler.
            # So calling `execute_decision` here is safe from infinite recursion loop logic, 
            # BUT if it fails, we return the failure, and the *original* execute_step sees a failure.
            # The original execute_step already called us. It will return our result.
            
            result = executor.execute_decision(
                context["category"],
                context["args"],
                context["query"]
            )
            
            # Standardize
            if not isinstance(result, ExecutionResult):
                result = ExecutionResult(True, str(result))
                
            if result.success:
                result.message = f"Retry successful: {result.message}"
            else:
                result.message = f"Retry failed: {result.message}"
                
            return result
            
        return ExecutionResult(False, "Retry unavailable (Internal Error)", error="INTERNAL")

    def _suggest_alternative(self, context) -> ExecutionResult:
        """Suggest an alternative app from the list."""
        alternatives = context.get("alternatives", [])
        original_app = context.get("args")
        
        if alternatives:
            # Pick first available alternative
            alt = alternatives[0] 
            # If alternative is just a string "open youtube", we need to describe it.
            # AI outputs alternatives as list of strings usually?
            # DecisionMaker: "alternatives": ["open youtube", "search google"]
            
            return ExecutionResult(
                False,
                f"'{original_app}' doesn't seem to be installed. Should I try '{alt}' instead?",
                error="ALTERNATIVE_AVAILABLE",
                data={"suggested_alternative": alt}
            )

        return ExecutionResult(False, f"'{original_app}' is not installed and I have no alternatives.", error="NO_ALTERNATIVE")
