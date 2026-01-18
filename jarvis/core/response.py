"""
Response formatting and speaking replies.
"""
import threading
import random
from typing import Optional
from jarvis.core.speech import SpeechEngine
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

# Responses for long text truncation
TRUNCATION_RESPONSES = [
    "The rest of the result has been printed to the chat screen, kindly check it out sir.",
    "The rest of the text is now on the chat screen, sir, please check it.",
    "You can see the rest of the text on the chat screen, sir.",
    "The remaining part of the text is now on the chat screen, sir.",
    "Sir, you'll find more text on the chat screen for you to see.",
    "The rest of the answer is now on the chat screen, sir.",
    "Sir, please look at the chat screen, the rest of the answer is there.",
    "You'll find the complete answer on the chat screen, sir.",
    "The next part of the text is on the chat screen, sir.",
    "Sir, please check the chat screen for more information.",
    "There's more text on the chat screen for you, sir.",
    "Sir, take a look at the chat screen for additional text.",
    "You'll find more to read on the chat screen, sir.",
    "Sir, check the chat screen for the rest of the text.",
    "The chat screen has the rest of the text, sir.",
    "There's more to see on the chat screen, sir, please look.",
    "Sir, the chat screen holds the continuation of the text.",
    "You'll find the complete answer on the chat screen, kindly check it out sir.",
    "Please review the chat screen for the rest of the text, sir.",
    "Sir, look at the chat screen for the complete answer."
]


class ResponseHandler:
    """Handles response formatting and speaking."""
    
    def __init__(self, speech_engine: SpeechEngine):
        """
        Initialize response handler.
        
        Args:
            speech_engine: SpeechEngine instance
        """
        self.speech_engine = speech_engine
    
    def _is_long_response(self, text: str) -> bool:
        """Check if response exceeds 2 lines or 250 words."""
        lines = text.strip().split('\n')
        words = text.split()
        return len(lines) > 2 or len(words) > 250
    
    def _extract_first_two_lines(self, text: str) -> str:
        """Extract first 2 lines from text."""
        lines = text.strip().split('\n')
        return '\n'.join(lines[:2])
    
    def respond(self, text: str, threaded: bool = False) -> Optional[threading.Thread]:
        """
        Format and speak response.
        If response is longer than 2 lines or 250 words, speak only first 2 lines
        and add a truncation message, then print full text to console.
        
        Args:
            text: Response text to speak
            threaded: If True, speak in background thread
            
        Returns:
            Thread object if threaded=True, None otherwise
        """
        if not text:
            return None
        
        text = text.strip()
        
        if self._is_long_response(text):
            first_two_lines = self._extract_first_two_lines(text)
            print("\n" + "="*60)
            print(text)
            print("="*60 + "\n")
            
            truncation_msg = random.choice(TRUNCATION_RESPONSES)
            spoken_text = f"{first_two_lines}\n\n{truncation_msg}"
            logger.info(f"Long response: {len(text)} chars")
            return self.speech_engine.speak(spoken_text, threaded=threaded)
        
        return self.speech_engine.speak(text, threaded=threaded)
