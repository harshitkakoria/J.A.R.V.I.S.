"""YouTube commands - play, search."""
import pywhatkit
import webbrowser
from urllib.parse import quote


def handle(query: str) -> str:
    """Handle YouTube commands."""
    q = query.lower()
    
    # Play video
    if "play" in q:
        # Extract video name
        for kw in ["play", "watch"]:
            if kw in q:
                video = q.split(kw, 1)[1].strip()
                if video:
                    pywhatkit.playonyt(video)
                    return f"Playing {video}"
        return "What should I play?"
    
    # Search YouTube
    if "search" in q and "youtube" in q:
        term = q.replace("search", "").replace("youtube", "").strip()
        if term:
            webbrowser.open(f"https://youtube.com/results?search_query={quote(term)}")
            return f"Searching YouTube for {term}"
    
    # Open YouTube
    if "youtube" in q:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"
    
    return None
