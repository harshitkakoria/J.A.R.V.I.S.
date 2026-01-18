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
    
    # Check installed apps
    for name, path in APPS.items():
        if name in q:
            if isinstance(path, list):
                for p in path:
                    p = p.format(os.getenv("USERNAME", ""))
                    if os.path.exists(p):
                        # Non-blocking, no shell
                        subprocess.Popen([p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return f"Opening {name}"
            elif path.startswith("ms-"):
                subprocess.Popen(["start", path], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {name}"
            elif os.path.exists(path):
                # Non-blocking, no shell
                subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {name}"
    
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
                subprocess.Popen([shortcut], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Opening {name}"
    
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
    
    procs = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "settings": "SystemSettings.exe",
        "vscode": "Code.exe",
    }
    
    for name, proc_name in procs.items():
        if name in q:
            if name == "chrome":
                return "Chrome is running speech recognition, so I won't close it."
            killed = False
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    if proc.info['name'].lower() == proc_name.lower():
                        # Skip the speech recognition Chrome tab
                        cmdline = " ".join(proc.info.get('cmdline') or []).lower()
                        if "speech_recognition.html" in cmdline:
                            continue
                        proc.kill()
                        killed = True
                except Exception:
                    pass
            if not killed and proc_name.lower() == "chrome.exe":
                return "Chrome STT tab is protected and left running."
            return f"Closed {name}" if killed else f"{name} not running"
    
    return "App not found"
