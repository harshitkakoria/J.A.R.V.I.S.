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
        # Check if it's a common program (including Chrome and VLC)
        if any(app in query_lower for app in ["notepad", "calculator", "paint", "cmd", "powershell", "explorer", "task manager", "chrome", "google chrome", "vlc"]):
            return open_program(query)
        # Try to open from desktop if not a common program
        else:
            return open_desktop_app(query)
    
    # Close tab (keyboard shortcut)
    # Match "close" + "tab" even if separated by words like "all the"
    if ("close" in query_lower and "tab" in query_lower) or any(kw in query_lower for kw in ["close tab", "close this tab", "close current tab"]):
        return close_tab()
    
    # Close window
    if ("close" in query_lower and "window" in query_lower) or any(kw in query_lower for kw in ["close window", "close this window"]):
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


def open_desktop_app(query: str) -> str:
    """
    Open an app from Desktop by searching for shortcuts and executables.
    
    Args:
        query: User command (e.g., "open vlc", "launch photoshop")
        
    Returns:
        Result message
    """
    try:
        import os
        import glob
        
        # Get username and construct desktop path
        username = os.getenv('USERNAME')
        desktop_path = f"C:\\Users\\{username}\\Desktop"
        
        if not os.path.exists(desktop_path):
            return "Desktop folder not found"
        
        # Extract app name from query
        query_lower = query.lower()
        for kw in ["open", "launch", "start", "run"]:
            query_lower = query_lower.replace(kw, "").strip()
        app_name = query_lower.strip()
        
        if not app_name:
            return "Please specify an app name to open"
        
        # Search for shortcuts (.lnk) first, then executables (.exe)
        shortcuts = glob.glob(f"{desktop_path}/*.lnk")
        executables = glob.glob(f"{desktop_path}/*.exe")
        all_items = shortcuts + executables
        
        # Find matching app (case-insensitive)
        for item_path in all_items:
            item_name = os.path.splitext(os.path.basename(item_path))[0].lower()
            if app_name in item_name or item_name in app_name:
                # Found a match
                subprocess.Popen(item_path, shell=True)
                logger.info(f"Opened desktop app: {item_path}")
                return f"Opening {item_name}"
        
        # No match found, list available apps
        available_apps = [os.path.splitext(os.path.basename(item))[0] for item in all_items]
        if available_apps:
            apps_list = ", ".join(available_apps[:5])  # Show first 5
            return f"App '{app_name}' not found on desktop. Available: {apps_list}"
        else:
            return f"No apps found on desktop"
        
    except Exception as e:
        logger.error(f"Open desktop app error: {e}")
        return f"Failed to open app: {str(e)}"





def open_program(query: str) -> str:
    """Open a program."""
    try:
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
        
        # Special handling for Chrome (search in common locations)
        if "chrome" in query_lower or "google chrome" in query_lower:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\Harshit\AppData\Local\Google\Chrome\Application\chrome.exe",
            ]
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen(chrome_path, shell=True)
                    logger.info(f"Opened Chrome: {chrome_path}")
                    return "Opening Chrome"
            logger.warning("Chrome not found in common locations")
            return "Chrome is not installed or not found"
        
        # Special handling for VLC (search in common locations)
        if "vlc" in query_lower:
            vlc_paths = [
                r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                r"C:\Users\Harshit\AppData\Local\VideoLAN\VLC\vlc.exe",
            ]
            for vlc_path in vlc_paths:
                if os.path.exists(vlc_path):
                    subprocess.Popen(vlc_path, shell=True)
                    logger.info(f"Opened VLC: {vlc_path}")
                    return "Opening VLC"
            logger.warning("VLC not found in common locations")
            return "VLC is not installed or not found"
        
        # Find which program to open (standard Windows programs)
        for name, executable in programs.items():
            if name in query_lower:
                subprocess.Popen(executable, shell=True)
                logger.info(f"Opened program: {executable}")
                return f"Opening {name.title()}"
        
        return "Program not recognized"
        
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
