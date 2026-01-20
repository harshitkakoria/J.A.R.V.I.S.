"""App control - open, close apps."""
import subprocess
import os
import glob
import webbrowser
import psutil
from urllib.parse import quote


# App paths
APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "chrome": ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
               "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"],
    "settings": "ms-settings:",
    "vscode": "C:\\Users\\{}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
}

# App websites (fallback)
WEBSITES = {
    "chatgpt": "https://chat.openai.com/",
    "gemini": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "spotify": "https://open.spotify.com/",
    "netflix": "https://www.netflix.com/",
    "github": "https://github.com/",
    "gmail": "https://mail.google.com/",
    "youtube": "https://youtube.com/",
}


def handle(query: str) -> str:
    """Handle app commands."""
    q = query.lower()
    
    # Close first
    if any(kw in q for kw in ["close", "shut", "exit", "kill"]):
        return close_app(q)
    
    # Open
    if any(kw in q for kw in ["open", "launch", "start"]):
        return open_app(q)
    
    return None


def open_app(query: str) -> str:
    """Open app or website."""
    q = query.lower()
    
    # Remove open keywords
    for kw in ["open", "launch", "start"]:
        q = q.replace(kw, "").strip()
    
    # Function to open without logs
    def run_detached(path):
        try:
            # CREATE_NO_WINDOW = 0x08000000
            # DETACHED_PROCESS = 0x00000008
            subprocess.Popen(
                [path], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
                shell=True  # Needed for shortcuts (.lnk) unfortunately, or use 'start' command
            )
            # Actually, simpler way for shortcuts that supports detachment:
            # usage of 'start "" "path"' via shell
            return True
        except:
            return False

    # Check installed apps
    for name, path in APPS.items():
        if name in q:
            if isinstance(path, list):
                for p in path:
                    p = p.format(os.getenv("USERNAME", ""))
                    if os.path.exists(p):
                        try:
                            # Use 'start' command to detach completely
                            subprocess.Popen(f'start "" "{p}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            return f"Opening {name}"
                        except Exception as e:
                            print(f"Error opening {name}: {e}")
            elif path.startswith("ms-"):
                subprocess.Popen(f'start {path}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {name}"
            elif os.path.exists(path):
                try:
                    subprocess.Popen(f'start "" "{path}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {name}"
                except Exception as e:
                    print(f"Error opening {name}: {e}")
    
    # Check Start Menu (Chrome apps)
    username = os.getenv("USERNAME")
    paths = [
        f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk",
        f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk",
    ]
    
    for search_path in paths:
        for shortcut in glob.glob(search_path, recursive=True):
            name = os.path.splitext(os.path.basename(shortcut))[0].lower()
            if q in name or name in q:
                try:
                    # 'start' command handles .lnk files and detaches them
                    subprocess.Popen(f'start "" "{shortcut}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opening {name}"
                except Exception:
                    pass
    
    # Check websites
    for name, url in WEBSITES.items():
        if name in q:
            webbrowser.open(url)
            return f"Opening {name} website"
    
    # Try generic website
    if " " not in q:  # Single word
        url = f"https://{q}.com"
        webbrowser.open(url)
        return f"Opening {url}"
    
    # Search Google
    webbrowser.open(f"https://google.com/search?q={quote(q + ' download')}")
    return f"Searching for {q}"


def close_app(query: str) -> str:
    """Close running app."""
    q = query.lower()
    
    # Remove close keywords
    for kw in ["close", "shut", "exit", "kill"]:
        q = q.replace(kw, "").strip()

    # Dynamic process closing
    killed_count = 0
    target = None
    
    # Common mappings
    mappings = {
        "calculator": "calc",
        "settings": "systemsettings",
        "paint": "mspaint",
        "vscode": "code.exe"
    }
    
    # Use mapping or original query
    search_term = mappings.get(q, q)
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            p_name = proc.info['name'].lower()
            
            # Skip system processes and self
            if p_name in ["python.exe", "cmd.exe", "powershell.exe", "svchost.exe", "explorer.exe"]:
                continue

            # Skip Chrome STT
            if "chrome" in p_name:
                cmdline = " ".join(proc.info.get('cmdline') or []).lower()
                if "speech_recognition.html" in cmdline:
                    continue

            # Match
            if search_term in p_name:
                proc.kill()
                killed_count += 1
                target = p_name
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if killed_count > 0:
        return f"Closed {target} ({killed_count} processes)"
    
    return f"Could not find running app: {q}"
