"""
System control skill: Screenshot, shutdown, volume control.
"""
import os
import platform
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle system control commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Screenshot
    if any(kw in query_lower for kw in ["screenshot", "take a screenshot", "capture screen", "print screen"]):
        return take_screenshot()
    
    # Shutdown - RE-ENABLED with confirmation requirement
    if any(kw in query_lower for kw in ["shutdown", "power off", "turn off", "reboot", "restart"]):
        return shutdown_system(query_lower)
    
    # Volume control
    if any(kw in query_lower for kw in ["volume", "loud", "quiet", "mute"]):
        return control_volume(query_lower)
    
    return None


def take_screenshot() -> str:
    """Take a screenshot and save it."""
    try:
        import pyautogui
        from datetime import datetime
        
        # Create screenshots directory
        screenshot_dir = "screenshots"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
        
        # Take screenshot
        pyautogui.screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
        
        return f"Screenshot taken and saved to {filename}"
        
    except ImportError:
        logger.error("pyautogui library not available")
        return "Screenshot library not installed."
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        return f"Failed to take screenshot: {str(e)}"


def shutdown_system(query: str) -> str:
    """
    Shutdown or restart the system.
    REQUIRES 'confirm' or 'yes' keyword for safety.
    """
    try:
        # SAFETY: Require explicit confirmation
        if "confirm" not in query and "yes" not in query:
            if "restart" in query or "reboot" in query:
                return "Restart requires confirmation. Say 'restart confirm' or 'restart yes'"
            else:
                return "Shutdown requires confirmation. Say 'shutdown confirm' or 'shutdown yes'"
        
        system = platform.system()
        
        if "restart" in query or "reboot" in query:
            logger.critical(f"SYSTEM RESTART INITIATED by user command: {query}")
            if system == "Windows":
                os.system("shutdown /r /t 10")
                return "System will restart in 10 seconds. Cancel with: shutdown /a"
            else:
                os.system("shutdown -r -t 10")
                return "System will restart in 10 seconds."
        else:
            logger.critical(f"SYSTEM SHUTDOWN INITIATED by user command: {query}")
            if system == "Windows":
                os.system("shutdown /s /t 10")
                return "System will shutdown in 10 seconds. Cancel with: shutdown /a"
            else:
                os.system("shutdown -h -t 10")
                return "System will shutdown in 10 seconds."
                
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
        return f"Failed to shutdown system: {str(e)}"


def control_volume(query: str) -> str:
    """Control system volume."""
    try:
        system = platform.system()
        
        if "mute" in query:
            if system == "Windows":
                os.system("nircmd.exe muteappvolume 0 toggle")
                return "Volume muted."
            return "Mute command not available on this system."
        
        elif "increase" in query or "louder" in query or "up" in query:
            if system == "Windows":
                # Increase volume using keyboard
                import pyautogui
                for _ in range(5):
                    pyautogui.press("volumeup")
                return "Volume increased."
            return "Volume control not available on this system."
        
        elif "decrease" in query or "quiet" in query or "down" in query:
            if system == "Windows":
                import pyautogui
                for _ in range(5):
                    pyautogui.press("volumedown")
                return "Volume decreased."
            return "Volume control not available on this system."
        
        return "Volume control command not recognized."
        
    except ImportError:
        logger.error("pyautogui library not available")
        return "Volume control library not installed."
    except Exception as e:
        logger.error(f"Volume control error: {e}")
        return f"Failed to control volume: {str(e)}"
