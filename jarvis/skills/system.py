"""System commands - screenshot, volume, shutdown."""
import subprocess
from pathlib import Path
from datetime import datetime
import re


def handle(query: str) -> str:
    """Handle system commands."""
    q = query.lower()
    
    # Screenshot
    if "screenshot" in q or "capture" in q:
        return take_screenshot()
    
    # Volume
    if any(kw in q for kw in ["volume", "mute", "unmute", "sound", "audio"]):
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
        import math
        
        # Correctly get the volume interface
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        
        # Mute/Unmute
        if "unmute" in query:
            volume.SetMute(0, None)
            return "Unmuted"
        elif "mute" in query:
            volume.SetMute(1, None)
            return "Muted"
            
        # Specific volume level (e.g. "volume 50", "set volume to 80%")
        # Find number in string
        numbers = re.findall(r'\d+', query)
        if numbers:
            level = int(numbers[0])
            if 0 <= level <= 100:
                scalar = level / 100.0
                volume.SetMasterVolumeLevelScalar(scalar, None)
                return f"Volume set to {level}%"
        
        # Incremental
        current = volume.GetMasterVolumeLevelScalar()
        if "up" in query or "louder" in query or "increase" in query:
            new_vol = min(1.0, current + 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return "Volume increased"
        elif "down" in query or "quieter" in query or "decrease" in query:
            new_vol = max(0.0, current - 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return "Volume decreased"
            
    except Exception as e:
        print(f"Volume error: {e}")
    
    return "Volume control unavailable"
