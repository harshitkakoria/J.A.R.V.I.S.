"""
Response formatting and speaking replies.
"""
from jarvis.core.speech import SpeechEngine
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseHandler:
    """Handles response formatting and speaking."""
    
    def __init__(self, speech_engine: SpeechEngine):
        """
        Initialize response handler.
        
        Args:
            speech_engine: SpeechEngine instance
        """
        self.speech_engine = speech_engine
    
    def respond(self, text: str) -> None:
        """
        Format and speak response.
        
        Args:
            text: Response text to speak
        """
        if not text:
            return
        
        # Clean and format response
        text = text.strip()
        
        # Speak the response
        self.speech_engine.speak(text)
    
    def acknowledge(self) -> None:
        """Quick acknowledgment sound/text."""
        self.speech_engine.speak("Yes, sir")
