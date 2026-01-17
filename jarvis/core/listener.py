"""
Wake-word detection and command recording.
"""
from typing import Optional
from jarvis.core.speech import SpeechEngine
from jarvis.utils.logger import setup_logger
from jarvis.utils.helpers import clean_text

logger = setup_logger(__name__)


class Listener:
    """Handles wake word detection and command capture."""
    
    def __init__(self, speech_engine: SpeechEngine, wake_word: str = "jarvis", use_wake_word: bool = True):
        """
        Initialize listener.
        
        Args:
            speech_engine: SpeechEngine instance
            wake_word: Wake word to listen for
            use_wake_word: Whether to use wake word detection
        """
        self.speech_engine = speech_engine
        self.wake_word = wake_word.lower()
        self.use_wake_word = use_wake_word
        logger.info(f"Listener initialized with wake word: '{self.wake_word}'")
    
    def wait_for_wake_word(self, timeout: int = 30) -> bool:
        """
        Wait for wake word to be detected.
        
        Args:
            timeout: Seconds to wait before giving up (0 = infinite)
            
        Returns:
            True if wake word detected, False if timeout
        """
        if not self.use_wake_word:
            return True
        
        logger.debug(f"Waiting for wake word '{self.wake_word}'...")
        attempts = 0
        max_attempts = timeout if timeout > 0 else 999999  # Large number for "infinite"
        
        while attempts < max_attempts:
            text = self.speech_engine.listen(timeout=3, phrase_time_limit=5)
            if text and self.wake_word in clean_text(text):
                logger.info(f"✓ Wake word '{self.wake_word}' detected!")
                return True
            
            attempts += 1
            if timeout > 0 and attempts % 5 == 0:
                logger.debug(f"Still waiting for wake word... ({attempts}s)")
        
        logger.warning(f"Timeout waiting for wake word after {timeout} seconds")
        return False
    
    def capture_command(self, timeout: int = 5) -> Optional[str]:
        """
        Capture user command after wake word.
        
        Args:
            timeout: Seconds to wait for command
            
        Returns:
            Captured command text or None
        """
        logger.debug("Listening for command...")
        # Increased phrase_time_limit from 5 to 8 seconds for longer sentences
        command = self.speech_engine.listen(timeout=timeout, phrase_time_limit=8)
        
        if command:
            # Remove wake word from command if present
            command = clean_text(command)
            if self.wake_word in command:
                command = command.replace(self.wake_word, "").strip()
            
            if command:  # Make sure there's still text after removing wake word
                return command
        
        return None
