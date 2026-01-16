"""
System commands skill: Run arbitrary system commands.
WARNING: This is DANGEROUS - only use with trusted voice input!
"""
import subprocess
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle system command execution.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Execute system command
    if any(kw in query_lower for kw in ["execute", "run command", "system command"]):
        return execute_command(query)
    
    return None


def execute_command(query: str) -> str:
    """
    Execute a system command.
    REQUIRES 'confirm' keyword for safety.
    """
    try:
        query_lower = query.lower()
        
        # SAFETY: Require confirmation
        if "confirm" not in query_lower:
            return "System commands require confirmation. Add 'confirm' to your command. Example: 'run command dir confirm'"
        
        # Extract command (everything after "command" and before "confirm")
        if "command" in query_lower:
            parts = query_lower.split("command")
            if len(parts) > 1:
                cmd_part = parts[1].split("confirm")[0].strip()
            else:
                return "Could not parse command"
        else:
            return "Please specify 'command' keyword"
        
        if not cmd_part:
            return "No command specified"
        
        # SAFETY: Blacklist dangerous commands
        dangerous_keywords = [
            "format", "del /f", "rm -rf", "rmdir /s", "shutdown /s",
            "reg delete", "diskpart", "fdisk", "mkfs", "dd if=",
            "cipher /w", ":(){:|:&};:", "fork bomb"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in cmd_part:
                logger.error(f"BLOCKED dangerous command: {cmd_part}")
                return f"Command blocked for safety: contains dangerous keyword '{keyword}'"
        
        # Execute command
        logger.warning(f"EXECUTING SYSTEM COMMAND: {cmd_part}")
        result = subprocess.run(
            cmd_part,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout if result.stdout else result.stderr
        
        if output:
            # Truncate long output
            if len(output) > 500:
                output = output[:500] + "... (output truncated)"
            return f"Command executed. Output: {output}"
        else:
            return "Command executed successfully"
            
    except subprocess.TimeoutExpired:
        return "Command timed out (10 seconds limit)"
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return f"Failed to execute command: {str(e)}"
