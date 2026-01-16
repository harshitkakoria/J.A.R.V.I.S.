"""
Helper functions: date formatting, string cleaning, etc.
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text input.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters if needed (keep basic punctuation)
    # text = re.sub(r'[^\w\s.,!?]', '', text)
    
    return text.lower()


def extract_keywords(query: str, keywords: List[str]) -> List[str]:
    """
    Extract matching keywords from query.
    Prioritizes longer/more specific keywords first.
    
    Args:
        query: User query
        keywords: List of keywords to search for
        
    Returns:
        List of matched keywords (sorted by length, descending)
    """
    query_lower = clean_text(query)
    matched = [kw for kw in keywords if kw.lower() in query_lower]
    # Sort by length (longest first) to prioritize specific keywords
    # e.g., "take a screenshot" should match "screenshot" before "hot"
    matched = sorted(matched, key=len, reverse=True)
    return matched


def format_time(hour: int, minute: int) -> str:
    """
    Format time in a natural way.
    
    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        
    Returns:
        Formatted time string
    """
    period = "AM" if hour < 12 else "PM"
    hour_12 = hour if hour <= 12 else hour - 12
    if hour_12 == 0:
        hour_12 = 12
    
    return f"{hour_12}:{minute:02d} {period}"


def extract_query_after_keyword(query: str, keyword: str) -> str:
    """
    Extract the part of query after a keyword.
    
    Args:
        query: Full query
        keyword: Keyword to search for
        
    Returns:
        Query part after keyword, or empty string
    """
    query_lower = clean_text(query)
    keyword_lower = keyword.lower()
    
    if keyword_lower in query_lower:
        idx = query_lower.find(keyword_lower)
        after = query[idx + len(keyword):].strip()
        return after
    
    return ""
