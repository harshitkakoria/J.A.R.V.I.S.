"""Helpers - text cleaning."""
import re


def clean_text(text: str) -> str:
    """Clean text from STT."""
    if not text:
        return ""
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix common mishearings
    replacements = {
        "broke": "grok",
        "brock": "grok",
        "grog": "grok",
        "groq": "grok",
    }
    
    words = text.split()
    cleaned = []
    for word in words:
        word_lower = word.lower()
        if word_lower in replacements:
            cleaned.append(replacements[word_lower])
        else:
            cleaned.append(word)
    
    return " ".join(cleaned)
