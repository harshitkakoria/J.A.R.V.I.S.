"""
Application control skill: Open programs, close tabs, switch windows.
"""
import subprocess
import os
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle application control commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Open programs
    if any(kw in query_lower for kw in ["open", "launch", "start", "run"]):
        # Check if it's a common program
        if any(app in query_lower for app in ["notepad", "calculator", "paint", "cmd", "powershell", "explorer", "task manager"]):
            return open_program(query)
    
    # Close tab (keyboard shortcut)
    if any(kw in query_lower for kw in ["close tab", "close this tab", "close current tab"]):
        return close_tab()
    
    # Close window
    if any(kw in query_lower for kw in ["close window", "close this window"]):
        return close_window()
    
    # Switch window (Alt+Tab)
    if any(kw in query_lower for kw in ["switch window", "next window", "change window"]):
        return switch_window()
    
    # Minimize window
    if any(kw in query_lower for kw in ["minimize", "minimize window"]):
        return minimize_window()
    
    # Maximize window
    if any(kw in query_lower for kw in ["maximize", "maximize window"]):
        return maximize_window()
    
    return None


def open_program(query: str) -> str:
    """Open a program."""
    try:
        import pyautogui
        query_lower = query.lower()
        
        # Program mappings
        programs = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
        }
        
        # Find which program to open
        for name, executable in programs.items():
            if name in query_lower:
                subprocess.Popen(executable, shell=True)
                logger.info(f"Opened program: {executable}")
                return f"Opening {name.title()}"
        
        return "Program not recognized. Try: notepad, calculator, paint, cmd, powershell, explorer, or task manager"
        
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Open program error: {e}")
        return f"Failed to open program: {str(e)}"


def close_tab() -> str:
    """Close current tab using Ctrl+W."""
    try:
        import pyautogui
        pyautogui.hotkey('ctrl', 'w')
        logger.info("Sent Ctrl+W (close tab)")
        return "Closing current tab"
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Close tab error: {e}")
        return f"Failed to close tab: {str(e)}"


def close_window() -> str:
    """Close current window using Alt+F4."""
    try:
        import pyautogui
        pyautogui.hotkey('alt', 'F4')
        logger.info("Sent Alt+F4 (close window)")
        return "Closing current window"
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Close window error: {e}")
        return f"Failed to close window: {str(e)}"


def switch_window() -> str:
    """Switch to next window using Alt+Tab."""
    try:
        import pyautogui
        pyautogui.hotkey('alt', 'tab')
        logger.info("Sent Alt+Tab (switch window)")
        return "Switching window"
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Switch window error: {e}")
        return f"Failed to switch window: {str(e)}"


def minimize_window() -> str:
    """Minimize current window."""
    try:
        import pyautogui
        pyautogui.hotkey('win', 'down')
        logger.info("Minimized window")
        return "Minimizing window"
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Minimize error: {e}")
        return f"Failed to minimize: {str(e)}"


def maximize_window() -> str:
    """Maximize current window."""
    try:
        import pyautogui
        pyautogui.hotkey('win', 'up')
        logger.info("Maximized window")
        return "Maximizing window"
    except ImportError:
        return "pyautogui not installed"
    except Exception as e:
        logger.error(f"Maximize error: {e}")
        return f"Failed to maximize: {str(e)}"
