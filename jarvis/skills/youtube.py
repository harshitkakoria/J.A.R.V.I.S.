"""
YouTube skill: Search, play videos, open channels, playlists.
"""
import webbrowser
import urllib.parse
from typing import Optional
from jarvis.utils.logger import setup_logger
import pywhatkit

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle YouTube commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Play video (highest priority)
    if any(kw in query_lower for kw in ["play", "watch", "show me"]):
        return play_video(query)
    
    # Search YouTube
    if any(kw in query_lower for kw in ["search", "find", "look for"]):
        return search_youtube(query)
    
    # Open channel
    if any(kw in query_lower for kw in ["channel", "subscribe"]):
        return open_channel(query)
    
    # Open trending
    if any(kw in query_lower for kw in ["trending", "popular", "hot videos"]):
        return open_trending()
    
    # Open subscriptions
    if any(kw in query_lower for kw in ["subscriptions", "my videos", "my channel"]):
        return open_subscriptions()
    
    # Open YouTube homepage (default)
    if any(kw in query_lower for kw in ["open youtube", "youtube", "go to youtube"]):
        return open_youtube_homepage()
    
    return None


def play_video(query: str) -> str:
    """
    Play a video on YouTube.
    
    Examples:
    - "play python tutorial"
    - "watch avengers trailer"
    - "show me cute cats"
    - "play karan aujla song on youtube"
    """
    try:
        query_lower = query.lower()
        
        # Extract video search term
        keywords_to_remove = [
            "play", "watch", "show me", "show", "on youtube", 
            "youtube", "video", "videos", "a video of", "song", 
            "songs", "music", "track", "album", "by"
        ]
        
        search_term = query_lower
        for keyword in keywords_to_remove:
            search_term = search_term.replace(keyword, "").strip()
        
        if search_term:
            # Use pywhatkit to play the most popular video automatically
            pywhatkit.playonyt(search_term)
            logger.info(f"Playing YouTube video: {search_term}")
            return f"Playing '{search_term}' on YouTube"
        else:
            return "Please specify what video you want to play"
            
    except Exception as e:
        logger.error(f"YouTube play error: {e}")
        return f"Failed to play video: {str(e)}"


def search_youtube(query: str) -> str:
    """
    Search YouTube for videos.
    
    Examples:
    - "search python programming"
    - "find cooking recipes"
    - "look for meditation music"
    - "search karan aujla songs"
    """
    try:
        query_lower = query.lower()
        
        # Extract search term
        keywords_to_remove = [
            "search", "find", "look for", "on youtube", 
            "youtube", "in youtube", "for", "song", "songs",
            "music", "video", "videos"
        ]
        
        search_term = query_lower
        for keyword in keywords_to_remove:
            search_term = search_term.replace(keyword, "").strip()
        
        if search_term:
            encoded_term = urllib.parse.quote(search_term)
            url = f"https://www.youtube.com/results?search_query={encoded_term}"
            webbrowser.open(url)
            logger.info(f"Searching YouTube: {search_term}")
            return f"Searching YouTube for '{search_term}'"
        else:
            return "Please specify what you want to search for"
            
    except Exception as e:
        logger.error(f"YouTube search error: {e}")
        return f"Failed to search: {str(e)}"


def open_channel(query: str) -> str:
    """
    Open a YouTube channel.
    
    Examples:
    - "open MrBeast channel"
    - "subscribe to PewDiePie"
    """
    try:
        query_lower = query.lower()
        
        # Extract channel name
        keywords_to_remove = [
            "open", "go to", "visit", "subscribe to", 
            "channel", "on youtube", "youtube"
        ]
        
        channel_name = query_lower
        for keyword in keywords_to_remove:
            channel_name = channel_name.replace(keyword, "").strip()
        
        if channel_name:
            # Search for channel (YouTube will show channel if it exists)
            encoded_name = urllib.parse.quote(f"{channel_name} channel")
            url = f"https://www.youtube.com/results?search_query={encoded_name}"
            webbrowser.open(url)
            logger.info(f"Opening YouTube channel: {channel_name}")
            return f"Opening {channel_name}'s channel"
        else:
            return "Please specify which channel to open"
            
    except Exception as e:
        logger.error(f"YouTube channel error: {e}")
        return f"Failed to open channel: {str(e)}"


def open_trending() -> str:
    """Open YouTube trending page."""
    try:
        url = "https://www.youtube.com/feed/trending"
        webbrowser.open(url)
        logger.info("Opening YouTube trending")
        return "Opening YouTube trending videos"
    except Exception as e:
        logger.error(f"YouTube trending error: {e}")
        return f"Failed to open trending: {str(e)}"


def open_subscriptions() -> str:
    """Open YouTube subscriptions page."""
    try:
        url = "https://www.youtube.com/feed/subscriptions"
        webbrowser.open(url)
        logger.info("Opening YouTube subscriptions")
        return "Opening your YouTube subscriptions"
    except Exception as e:
        logger.error(f"YouTube subscriptions error: {e}")
        return f"Failed to open subscriptions: {str(e)}"


def open_youtube_homepage() -> str:
    """Open YouTube homepage."""
    try:
        url = "https://www.youtube.com"
        webbrowser.open(url)
        logger.info("Opening YouTube homepage")
        return "Opening YouTube"
    except Exception as e:
        logger.error(f"YouTube homepage error: {e}")
        return f"Failed to open YouTube: {str(e)}"
