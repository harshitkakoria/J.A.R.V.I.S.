import subprocess
from pathlib import Path
from datetime import datetime
import re
import psutil
import pyperclip
import pyautogui

def handle(query: str) -> str:
    """Handle system commands."""
    q = query.lower()
    
    # Media Control
    if any(kw in q for kw in ["play", "pause", "stop", "next", "previous", "skip", "track", "media"]):
        return control_media(q)

    # System Status
    if any(kw in q for kw in ["cpu", "ram", "memory", "battery", "system status", "pc health"]):
        return get_system_status(q)
        
    # Clipboard
    if any(kw in q for kw in ["clipboard", "copy", "paste"]):
        return clipboard_manager(q)
    
    # Screenshot
    if "screenshot" in q or "capture" in q:
        return take_screenshot()
    
    # Volume
    if any(kw in q for kw in ["volume", "mute", "unmute", "sound", "audio"]):
        return control_volume(q)
    
    # Wi-Fi
    if any(kw in q for kw in ["wifi", "internet"]):
        return control_wifi(q)
        
    # Brightness
    if any(kw in q for kw in ["brightness", "dim", "bright", "screen"]):
        return set_brightness(q)

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


def set_brightness(query: str) -> str:
    """Control screen brightness using PowerShell."""
    try:
        # 1. Get current brightness first (for relative changes)
        cmd_get = "(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightness).CurrentBrightness"
        result = subprocess.check_output(["powershell", "-Command", cmd_get], shell=True).decode().strip()
        current_level = int(result) if result.isdigit() else 50
        print(f"[DEBUG] Current Brightness: {current_level}, Query: '{query}'")
        
        target_level = current_level
        
        # 2. Parse Target
        numbers = re.findall(r'\d+', query)
        if numbers:
            target_level = int(numbers[0])
            print(f"[DEBUG] Matched Number: {target_level}")
        elif any(kw in query for kw in ["increase", "up", "raise", "more", "brighten"]):
            target_level = min(100, current_level + 20)
            print(f"[DEBUG] Matched Increase. Target: {target_level}")
        elif any(kw in query for kw in ["decrease", "down", "lower", "less", "dim"]):
            target_level = max(0, current_level - 20)
            print(f"[DEBUG] Matched Decrease. Target: {target_level}")
        elif "max" in query or "full" in query:
            target_level = 100
        elif "min" in query or "lowest" in query:
            target_level = 0
            
        print(f"[DEBUG] Final Target: {target_level}")
        
        # 3. Set Brightness
        cmd_set = f"(Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {target_level})"
        subprocess.run(["powershell", "-Command", cmd_set], shell=True)
        
        return f"Brightness set to {target_level}%"
        
    except Exception as e:
        print(f"Brightness Error: {e}")
        return "Failed to set brightness (WMI error)"


def control_wifi(query: str) -> str:
    """Control Wi-Fi using netsh."""
    try:
        if "off" in query or "disconnect" in query or "disable" in query:
            # Disconnect
            subprocess.run("netsh wlan disconnect", shell=True)
            return "Wi-Fi disconnected"
            
        elif "on" in query or "connect" in query or "enable" in query:
            # Try to connect (requires interface to be on and auto-connect profile)
            # Just 'netsh wlan connect' usually tries the default or fails if specific profile needed?
            # 'netsh wlan connect name="ProfileName"'
            # We'll try to scan/connect or just generic connect
            # Simplest generic re-connect usually works if profile exists
            subprocess.run("netsh wlan connect name=Home", shell=True) # TODO: Make dynamic later?
            # Actually, standard 'connect' without name might error. 
            # But we can try just re-enabling if we disabled the interface.
            # But we strictly used 'disconnect' earlier, not disable interface.
            return "Attempting to connect Wi-Fi..."
            
    except:
        pass
    return "Check Wi-Fi settings"


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


def control_media(query: str) -> str:
    """Control media playback using pyautogui."""
    try:
        q = query.lower()
        
        if "play" in q or "pause" in q:
            pyautogui.press("playpause")
            return "Toggled media playback"
            
        elif "next" in q or "skip" in q:
            pyautogui.press("nexttrack")
            return "Skipped to next track"
            
        elif "previous" in q or "back" in q:
            pyautogui.press("prevtrack")
            return "Went back to previous track"
            
        elif "stop" in q:
            pyautogui.press("stopmedia")
            return "Stopped media"
            
    except Exception as e:
        print(f"Media Error: {e}")
        
    return "Media control failed"


def get_system_status(query: str) -> str:
    """Get CPU, RAM, and Battery status."""
    try:
        status = []
        q = query.lower()
        
        # CPU
        if "cpu" in q or "system" in q or "health" in q:
            cpu = psutil.cpu_percent(interval=0.1)
            status.append(f"CPU: {cpu}%")
            
        # RAM
        if "ram" in q or "memory" in q or "system" in q or "health" in q:
            mem = psutil.virtual_memory()
            # Convert to GB
            used_gb = round(mem.used / (1024**3), 1)
            total_gb = round(mem.total / (1024**3), 1)
            percent = mem.percent
            status.append(f"RAM: {used_gb}/{total_gb} GB ({percent}%)")
            
        # Battery
        if "battery" in q or "power" in q or "system" in q or "health" in q:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "Plugged in" if battery.power_plugged else "On battery"
                status.append(f"Battery: {battery.percent}% ({plugged})")
            else:
                status.append("Battery: No battery detected")
                
        if not status:
            return "Please specify CPU, RAM, or Battery."
            
        return " | ".join(status)
        
    except Exception as e:
        return f"Error getting system status: {e}"


def clipboard_manager(query: str) -> str:
    """Manage system clipboard."""
    try:
        q = query.lower()
        
        if "read" in q or "what is on" in q or "tell me" in q:
            content = pyperclip.paste()
            if not content:
                return "Clipboard is empty."
            # Truncate if too long for voice, but keep for chat
            preview = content[:200] + "..." if len(content) > 200 else content
            return f"Clipboard contains: {preview}"
            
        # Write to clipboard (usually from an args passing perspective, 
        # but for voice, it might be 'copy [text]'). 
        # Ideally, this function is called with a specific string to copy.
        # But for now, we'll support "clear"
        
        if "clear" in q or "empty" in q:
            pyperclip.copy("")
            return "Clipboard cleared."
            
        # If the user says "copy X", we'd need to extract X.
        # Simple extraction:
        if "copy " in q:
            text_to_copy = query.split("copy ", 1)[1].strip()
            pyperclip.copy(text_to_copy)
            return "Copied to clipboard."
            
        return "Clipboard command not recognized (Read/Clear/Copy)"
        
    except Exception as e:
        return f"Clipboard error: {e}"


def control_media(query: str) -> str:
    """Control media playback using pyautogui."""
    try:
        q = query.lower()
        
        if "play" in q or "pause" in q:
            pyautogui.press("playpause")
            return "Toggled media playback"
            
        elif "next" in q or "skip" in q:
            pyautogui.press("nexttrack")
            return "Skipped to next track"
            
        elif "previous" in q or "back" in q:
            pyautogui.press("prevtrack")
            return "Went back to previous track"
            
        elif "stop" in q:
            pyautogui.press("stopmedia")
            return "Stopped media"
            
    except Exception as e:
        print(f"Media Error: {e}")
        
    return "Media control failed"


def get_system_status(query: str) -> str:
    """Get CPU, RAM, and Battery status."""
    try:
        status = []
        q = query.lower()
        
        # CPU
        if "cpu" in q or "system" in q or "health" in q:
            cpu = psutil.cpu_percent(interval=0.1)
            status.append(f"CPU: {cpu}%")
            
        # RAM
        if "ram" in q or "memory" in q or "system" in q or "health" in q:
            mem = psutil.virtual_memory()
            # Convert to GB
            used_gb = round(mem.used / (1024**3), 1)
            total_gb = round(mem.total / (1024**3), 1)
            percent = mem.percent
            status.append(f"RAM: {used_gb}/{total_gb} GB ({percent}%)")
            
        # Battery
        if "battery" in q or "power" in q or "system" in q or "health" in q:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "Plugged in" if battery.power_plugged else "On battery"
                status.append(f"Battery: {battery.percent}% ({plugged})")
            else:
                status.append("Battery: No battery detected")
                
        if not status:
            return "Please specify CPU, RAM, or Battery."
            
        return " | ".join(status)
        
    except Exception as e:
        return f"Error getting system status: {e}"


def clipboard_manager(query: str) -> str:
    """Manage system clipboard."""
    try:
        q = query.lower()
        
        if "read" in q or "what is on" in q or "tell me" in q:
            content = pyperclip.paste()
            if not content:
                return "Clipboard is empty."
            # Truncate if too long for voice, but keep for chat
            preview = content[:200] + "..." if len(content) > 200 else content
            return f"Clipboard contains: {preview}"
            
        # Write to clipboard (usually from an args passing perspective, 
        # but for voice, it might be 'copy [text]'). 
        # Ideally, this function is called with a specific string to copy.
        # But for now, we'll support "clear"
        
        if "clear" in q or "empty" in q:
            pyperclip.copy("")
            return "Clipboard cleared."
            
        # If the user says "copy X", we'd need to extract X.
        # Simple extraction:
        if "copy " in q:
            text_to_copy = query.split("copy ", 1)[1].strip()
            pyperclip.copy(text_to_copy)
            return "Copied to clipboard."
            
        return "Clipboard command not recognized (Read/Clear/Copy)"
        
    except Exception as e:
        return f"Clipboard error: {e}"
