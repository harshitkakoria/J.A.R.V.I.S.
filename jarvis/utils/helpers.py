"""Helpers - text cleaning and normalization."""
import re

# 1. Filler Words (Removed completely)
# These contribute no semantic meaning to the command
FILLER_WORDS = [
    "hey", "jarvis", "hi", "hello",
    "please", "can you", "could you", "would you", "will you", "do you",
    "for me", "just", "now", "actually", "basically", "literally",
    "uh", "um", "ah", "er", "hmm", "uhh", "umm", "like"
]

# 2. Synonyms (Mapped to Canonical Commands)
# Format: "variation": "canonical"
# Only strictly relevant mappings for current capabilities
SYNONYMS = {
    # Apps
    "boot up": "open",
    "start up": "open",
    "run": "open",
    "launch": "open", # Canonical but good to enforce
    "shut down": "close",
    "terminate": "close",
    "kill": "close",
    "exit": "close",
    
    # Web
    "find": "search",
    "lookup": "search",
    "look up": "search",
    "browse": "open",
    
    # YouTube
    "listen to": "play",
    "put on": "play",
    
    # System
    "snap": "screenshot",
    "capture": "screenshot",
    "screen shot": "screenshot",
    "quiet": "mute",
    "silent": "mute",
    "silence": "mute",
    "louder": "volume up",
    "softer": "volume down",
    "lower volume": "volume down",
    "raise volume": "volume up",
    
    # Weather
    "forecast": "weather",
    "climate": "weather",
    "temperature": "weather", # Often asks for "what's the temp", maps to weather skill checks
}

# 3. Common Mishearings (ASR Error Correction)
MISHEARINGS = {
    "broke": "grok",
    "brock": "grok",
    "grog": "grok",
    "groq": "grok",
    "chat gpt": "chatgpt",
    "what's": "what is",
    "whats": "what is",
    "opn": "open"
}

def clean_text(text: str) -> str:
    """
    Normalize text input:
    1. Lowercase
    2. Remove filler words
    3. Fix mishearings
    4. Map synonyms to canonical commands
    """
    if not text:
        return ""
    
    # 1. Lowercase
    text = text.lower()
    
    # 2. Remove Filler Words
    # distinct words only to avoid matching inside words
    # Sort by length descending to match phrases like "can you" before "you"
    sorted_fillers = sorted(FILLER_WORDS, key=len, reverse=True)
    pattern = r'\b(' + '|'.join(map(re.escape, sorted_fillers)) + r')\b'
    text = re.sub(pattern, '', text)
    
    # Clean up multiple spaces left by removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 3. Fix Mishearings & Map Synonyms
    # We use a similar regex strategy for safe phrases replacement
    
    # Combine maps
    replacements = {**MISHEARINGS, **SYNONYMS}
    
    # Create pattern for replacements
    # Sort by length DESC to match "shut down" before "shut"
    sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
    
    # Compile regex for one-pass replacement
    # Using a callback function for replacement
    pattern = r'\b(' + '|'.join(map(re.escape, sorted_keys)) + r')\b'
    
    def replace_callback(match):
        return replacements[match.group(0)]
    
    text = re.sub(pattern, replace_callback, text)
    
    # Final cleanup
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def is_ambiguous(text: str, memory) -> bool:
    """Check if text contains unresolved pronouns."""
    PRONOUNS = {"it", "this", "that", "them", "those"}
    tokens = text.lower().split()
    
    if any(p in tokens for p in PRONOUNS):
        # If we have a pronoun, check if memory has a resolved entity
        return not memory.has_recent_entity()
        
    return False
