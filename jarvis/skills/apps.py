import webbrowser
import difflib
import psutil
from urllib.parse import quote
from AppOpener import open as app_open, close as app_close, give_appnames
from jarvis.core.models import ExecutionResult

# App websites (fallback)
# Used only if AppOpener fails or for specific website requests
WEBSITES = {
    "google": "https://google.com/",
    "youtube": "https://youtube.com/",
    "facebook": "https://facebook.com/",
    "twitter": "https://twitter.com/",
    "instagram": "https://instagram.com/",
    "chatgpt": "https://chat.openai.com/",
    "gemini": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "netflix": "https://www.netflix.com/",
    "github": "https://github.com/",
    "gmail": "https://mail.google.com/",
    "maps": "https://maps.google.com/",
    "lms": "https://lms.vit.ac.in/login/index.php",
    "vitop":"https://vtopcc.vit.ac.in/vtop/open/page",
    "vitcolab": "https://vitcolab945.examly.io/"
}

def handle(query: str) -> ExecutionResult:
    """Handle app commands."""
    q = query.lower()
    
    # Close first
    if any(kw in q for kw in ["close", "shut", "exit", "kill"]):
        return close_app(q)
    
    # Open
    if any(kw in q for kw in ["open", "launch", "start"]):
        return open_app(q)
    
    return None


# Cache for app names to avoid re-fetching (slows down voice mode)
APP_NAMES_CACHE = None

def open_app(query: str) -> ExecutionResult:
    """Open app or website."""
    global APP_NAMES_CACHE
    q = query.lower()
    
    # Remove open keywords
    for kw in ["open", "launch", "start", "the"]:
        q = q.replace(kw, "").strip()
    
    # 1. Try AppOpener (Handles UWP, Shortcuts, Fuzzy Matching)
    try:
        # Lazy load app names
        if APP_NAMES_CACHE is None:
            # give_appnames() returns dict_keys, convert to list for efficient reuse
            APP_NAMES_CACHE = list(give_appnames())
        
        # 1.1 Aliases (Manual Overrides for common issues)
        aliases = {
            "chrome": "google chrome",
            "code": "visual studio code",
            "vscode": "visual studio code",
            "edge": "microsoft edge",
            "brave": "brave browser",
            "word": "word",
            "excel": "excel",
            "powerpoint": "powerpoint",
            "ppt": "powerpoint",
            "store": "microsoft store",
            "notepad": "notepad",
            "calc": "calculator",
            "explorer": "file explorer",
            "terminal": "windows terminal"
        }
        target_name = aliases.get(q, q)
        
        # Find closest match manually to get the cleaner name
        matches = difflib.get_close_matches(target_name, APP_NAMES_CACHE, n=1, cutoff=0.6)
        
        if matches:
            target_name = matches[0]
            # print(f"Matched '{q}' to '{target_name}'") # Debug only
            
            print(f"AppOpener: Attempting to open '{target_name}'")
            app_open(target_name, match_closest=True, output=False)
            return ExecutionResult(True, f"Opening {target_name}", data={"app": target_name})
        
        # If no match found in installed apps, do NOT try to open blindly.
        # Fall through to websites/search.
        print(f"AppOpener: No matching app found for '{q}'")

    except Exception as e:
        print(f"AppOpener failed: {e}")
    
    # 2. Fallback: Check websites
    for name, url in WEBSITES.items():
        if name in q:
            webbrowser.open(url)
            return ExecutionResult(True, f"Opening {name} website", data={"url": url})
    
    # 3. Try generic website (Stricter: Must look like a domain)
    if "." in q and " " not in q:  # e.g. "example.com" but not "windows terminal"
        if not q.startswith("http"):
             url = f"https://{q}"
        else:
             url = q
        webbrowser.open(url)
        return ExecutionResult(True, f"Opening {url}", data={"url": url})
    
    # 4. Search Google
    webbrowser.open(f"https://google.com/search?q={quote(q + ' download')}")
    return ExecutionResult(True, f"Searching for {q}", data={"query": q})


def close_app(query: str) -> ExecutionResult:
    """Close running app safely using psutil."""
    q = query.lower()
    
    # Remove close keywords
    for kw in ["close", "shut", "exit", "kill"]:
        q = q.replace(kw, "").strip()

    # Dynamic process closing using psutil (Safer than AppOpener)
    killed_count = 0
    target = None
    
    # Common mappings for process names
    mappings = {
        "calculator": "calc",
        "settings": "systemsettings",
        "paint": "mspaint",
        "vscode": "code",
        "github": "github", # Matches GitHubDesktop.exe or similar
        "spotify": "spotify",
    }
    
    search_term = mappings.get(q, q)
    print(f"Attempting to close process matching: '{search_term}'")
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                p_name = proc.info['name'].lower()
                
                # Critical Safety: Skip system processes
                if p_name in ["python.exe", "cmd.exe", "powershell.exe", "svchost.exe", "explorer.exe", "csrss.exe", "winlogon.exe"]:
                    continue

                # Smart matching
                match = False
                
                # Check name
                if search_term in p_name:
                    match = True
                
                # Check command line (helpful for python scripts or java apps)
                if not match and proc.info['cmdline']:
                    cmd = " ".join(proc.info['cmdline']).lower()
                    if search_term in cmd:
                        match = True
                
                if match:
                    print(f"Killing process: {p_name} ({proc.info['pid']})")
                    proc.kill()
                    killed_count += 1
                    target = p_name
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        if killed_count > 0:
            return ExecutionResult(True, f"Closed {target} ({killed_count} processes)", data={"count": killed_count})
        
    except Exception as e:
        print(f"Error in close_app: {e}")
        return ExecutionResult(False, f"Error closing app: {e}", error=str(e))
        
    return ExecutionResult(False, f"Could not find running app: {q}")
