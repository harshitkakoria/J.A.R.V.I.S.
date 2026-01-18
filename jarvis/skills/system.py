"""System commands - screenshot, volume, shutdown."""
import subprocess
from pathlib import Path
from datetime import datetime


def handle(query: str) -> str:
    """Handle system commands."""
    q = query.lower()
    
    # Screenshot
    if "screenshot" in q or "capture" in q:
        return take_screenshot()
    
    # Volume
    if any(kw in q for kw in ["volume", "mute", "louder", "quieter"]):
        return control_volume(q)
    
    # Shutdown
    if "shutdown" in q:
        return "Shutdown disabled for safety"
    
    return None


def take_screenshot() -> str:
    """Take a screenshot."""
    try:
        import pyautogui
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = Path.home() / "Downloads" / filename
        pyautogui.screenshot(str(path))
        return f"Screenshot saved to Downloads"
    except:
        return "Screenshot failed"


def control_volume(query: str) -> str:
    """Control system volume."""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        if "mute" in query:
            volume.SetMute(1, None)
            return "Muted"
        elif "unmute" in query:
            volume.SetMute(0, None)
            return "Unmuted"
        elif "up" in query or "louder" in query:
            current = volume.GetMasterVolumeLevel()
            volume.SetMasterVolumeLevel(current + 3, None)
            return "Volume up"
        elif "down" in query or "quieter" in query:
            current = volume.GetMasterVolumeLevel()
            volume.SetMasterVolumeLevel(current - 3, None)
            return "Volume down"
    except:
        pass
    
    return "Volume control not available"
