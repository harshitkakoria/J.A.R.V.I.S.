import ctypes
from ctypes import wintypes
import psutil
from typing import Optional, Dict

class ContextManager:
    """
    Manages system context awareness (Active Window, Process, etc.)
    using Windows API (ctypes) and psutil.
    """
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

    def get_context(self) -> Dict[str, Optional[str]]:
        """
        Snapshot the current system context.
        Returns:
            dict: {
                "active_window": str (Title),
                "process_name": str (exe name),
                "app_name": str (Simplified name for AI)
            }
        """
        title = self._get_active_window_title()
        process = self._get_active_process_name()
        
        return {
            "active_window": title,
            "process_name": process,
            "app_name": self._simplify_app_name(process)
        }

    def _get_active_window_title(self) -> Optional[str]:
        """Get the title of the foreground window."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            length = self.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return None
                
            buff = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        except Exception as e:
            print(f"[!] Error getting window title: {e}")
            return None

    def _get_active_process_name(self) -> Optional[str]:
        """Get the executable name of the foreground window."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            if pid.value == 0:
                return None
                
            process = psutil.Process(pid.value)
            return process.name()
        except Exception as e:
            print(f"[!] Error getting process name: {e}")
            return None

    def _simplify_app_name(self, process_name: Optional[str]) -> Optional[str]:
        """Convert 'chrome.exe' -> 'Google Chrome' for better AI context."""
        if not process_name:
            return None
            
        name = process_name.lower().replace(".exe", "")
        mapping = {
            "chrome": "Google Chrome",
            "firefox": "Firefox",
            "msedge": "Microsoft Edge",
            "notepad": "Notepad",
            "explorer": "File Explorer",
            "spotify": "Spotify",
            "code": "VS Code",
            "cmd": "Command Prompt",
            "powershell": "PowerShell",
            "discord": "Discord",
            "vlc": "VLC Media Player"
        }
        return mapping.get(name, name.capitalize())

if __name__ == "__main__":
    # Quick Test
    cm = ContextManager()
    import time
    print("Switch windows now... checking in 3 seconds.")
    time.sleep(3)
    print(f"Context: {cm.get_context()}")
