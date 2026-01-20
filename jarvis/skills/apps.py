import webbrowser
import difflib
from urllib.parse import quote
from AppOpener import open as app_open, close as app_close, give_appnames

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


# Cache for app names to avoid re-fetching (slows down voice mode)
APP_NAMES_CACHE = None

def open_app(query: str) -> str:
    """Open app or website."""
    global APP_NAMES_CACHE
    q = query.lower()
    
    # Remove open keywords
    for kw in ["open", "launch", "start"]:
        q = q.replace(kw, "").strip()
    
    # 1. Try AppOpener (Handles UWP, Shortcuts, Fuzzy Matching)
    try:
        # Lazy load app names
        if APP_NAMES_CACHE is None:
            # give_appnames() returns dict_keys, convert to list for efficient reuse
            APP_NAMES_CACHE = list(give_appnames())
        
        # Find closest match manually to get the cleaner name
        matches = difflib.get_close_matches(q, APP_NAMES_CACHE, n=1, cutoff=0.6)
        
        target_name = q # Default to query
        if matches:
            target_name = matches[0]
            # print(f"Matched '{q}' to '{target_name}'") # Debug only
            
            print(f"AppOpener: Attempting to open '{target_name}'")
            app_open(target_name, match_closest=True, output=False)
            return f"Opening {target_name}"
        
        # If no match found in installed apps, do NOT try to open blindly.
        # Fall through to websites/search.
        print(f"AppOpener: No matching app found for '{q}'")

    except Exception as e:
        print(f"AppOpener failed: {e}")
    
    # 2. Fallback: Check websites
    for name, url in WEBSITES.items():
        if name in q:
            webbrowser.open(url)
            return f"Opening {name} website"
    
    # 3. Try generic website
    if " " not in q:  # Single word
        url = f"https://{q}.com"
        webbrowser.open(url)
        return f"Opening {url}"
    
    # 4. Search Google
    webbrowser.open(f"https://google.com/search?q={quote(q + ' download')}")
    return f"Searching for {q}"


def close_app(query: str) -> str:
    """Close running app."""
    q = query.lower()
    
    # Remove close keywords
    for kw in ["close", "shut", "exit", "kill"]:
        q = q.replace(kw, "").strip()

    # Try AppOpener for close
    try:
        print(f"AppOpener: Closing '{q}'")
        app_close(q, match_closest=True, output=False)
        return f"Closed {q} (if running)"
    except Exception as e:
        return f"Error closing {q}: {e}"
