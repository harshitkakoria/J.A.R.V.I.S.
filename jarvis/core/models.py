"""Core data models."""
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class ExecutionResult:
    """Standardized result from skill execution."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    
    def __str__(self):
        return self.message
