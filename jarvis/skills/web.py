"""
Web browsing skill: Open websites, play videos, search.
"""
import webbrowser
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle web browsing commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # GitHub (check before generic open)
    if "github" in query_lower:
        return open_github()
    
    # Stack Overflow (check before generic open)
    if any(kw in query_lower for kw in ["stackoverflow", "stack overflow"]):
        return open_stackoverflow()
    
    # Open Google (check before generic open)
    if any(kw in query_lower for kw in ["google", "search google"]):
        return open_google(query)
    
    # Open YouTube (check before generic open)
    if any(kw in query_lower for kw in ["youtube", "play", "video", "music"]):
        return open_youtube(query)
    
    # Open website (generic, check last)
    if any(kw in query_lower for kw in ["open", "visit", "go to", "website"]):
        return open_website(query)
    
    return None


def open_google(query: str) -> str:
    """Open Google and search."""
    try:
        query_lower = query.lower()
        
        # Extract search term - remove keywords
        keywords_to_remove = ["google", "search", "on google", "in google", "open"]
        search_term = query_lower
        for keyword in keywords_to_remove:
            search_term = search_term.replace(keyword, "").strip()
        
        if search_term and search_term.strip():
            url = f"https://www.google.com/search?q={search_term.strip()}"
            webbrowser.open(url)
            return f"Opening Google search for '{search_term.strip()}'"
        else:
            webbrowser.open("https://www.google.com")
            return "Opening Google"
            
    except Exception as e:
        logger.error(f"Google open error: {e}")
        return f"Failed to open Google: {str(e)}"


def open_youtube(query: str) -> str:
    """Open YouTube and search."""
    try:
        query_lower = query.lower()
        
        # Extract search term - remove keywords
        keywords_to_remove = ["youtube", "play", "video", "music", "on youtube", "in youtube", "open"]
        search_term = query_lower
        for keyword in keywords_to_remove:
            search_term = search_term.replace(keyword, "").strip()
        
        if search_term and search_term.strip():
            url = f"https://www.youtube.com/results?search_query={search_term.strip()}"
            webbrowser.open(url)
            return f"Opening YouTube search for '{search_term.strip()}'"
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube"
            
    except Exception as e:
        logger.error(f"YouTube open error: {e}")
        return f"Failed to open YouTube: {str(e)}"
        return f"Failed to open YouTube: {str(e)}"


def open_website(query: str) -> str:
    """Open a website."""
    try:
        # Extract website name
        website = query.lower().replace("open", "").replace("visit", "").replace("go to", "").replace("website", "").strip()
        
        if website:
            # Add https:// if not present
            if not website.startswith("http"):
                url = f"https://{website}.com"
            else:
                url = website
            
            webbrowser.open(url)
            return f"Opening {website}"
        else:
            return "Please specify a website to open."
            
    except Exception as e:
        logger.error(f"Website open error: {e}")
        return f"Failed to open website: {str(e)}"


def open_github() -> str:
    """Open GitHub."""
    try:
        webbrowser.open("https://www.github.com")
        return "Opening GitHub"
    except Exception as e:
        logger.error(f"GitHub open error: {e}")
        return f"Failed to open GitHub: {str(e)}"


def open_stackoverflow() -> str:
    """Open Stack Overflow."""
    try:
        webbrowser.open("https://www.stackoverflow.com")
        return "Opening Stack Overflow"
    except Exception as e:
        logger.error(f"Stack Overflow open error: {e}")
        return f"Failed to open Stack Overflow: {str(e)}"
