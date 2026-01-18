"""Web commands - search, open websites."""
import webbrowser
from urllib.parse import quote


def handle(query: str) -> str:
    """Handle web commands."""
    q = query.lower()
    
    # Google search
    if "search" in q or "google" in q:
        # Extract search term
        for kw in ["search for", "google", "search"]:
            if kw in q:
                term = q.split(kw, 1)[1].strip()
                if term:
                    webbrowser.open(f"https://google.com/search?q={quote(term)}")
                    return f"Searching for {term}"
        return "What should I search for?"
    
    # Open website
    if "open" in q:
        sites = {
            "youtube": "https://youtube.com",
            "facebook": "https://facebook.com",
            "github": "https://github.com",
            "twitter": "https://twitter.com",
            "instagram": "https://instagram.com",
        }
        for name, url in sites.items():
            if name in q:
                webbrowser.open(url)
                return f"Opening {name}"
        return "Which website?"
    
    return None
