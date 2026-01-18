"""
Wake-word detection and command recording.
"""
import threading
from typing import Optional, Callable
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
    
    def wait_for_wake_word(self, timeout: int = 30, threaded: bool = False, callback: Optional[Callable[[bool], None]] = None) -> Optional[threading.Thread]:
        """
        Wait for wake word to be detected.
        Can run in background thread with callback.
        
        Args:
            timeout: Seconds to wait before giving up (0 = infinite)
            threaded: If True, run in background thread
            callback: Function to call with result (True/False) when done
            
        Returns:
            Thread object if threaded=True, None otherwise
        """
        if threaded:
            thread = threading.Thread(
                target=self._wait_for_wake_word_impl,
                args=(timeout, callback),
                daemon=True
            )
            thread.start()
            logger.debug(f"Started wake word detection in background thread")
            return thread
        else:
            return self._wait_for_wake_word_impl(timeout, callback)
    
    def _wait_for_wake_word_impl(self, timeout: int = 30, callback: Optional[Callable[[bool], None]] = None) -> Optional[bool]:
        """Internal implementation of wake word detection."""
        if not self.use_wake_word:
            if callback:
                callback(True)
            return True
        
        logger.debug(f"Waiting for wake word '{self.wake_word}'...")
        attempts = 0
        max_attempts = timeout if timeout > 0 else 999999  # Large number for "infinite"
        
        while attempts < max_attempts:
            text = self.speech_engine.listen(timeout=3, phrase_time_limit=5)
            if text and self.wake_word in clean_text(text):
                logger.info(f"✓ Wake word '{self.wake_word}' detected!")
                if callback:
                    callback(True)
                return True
            
            attempts += 1
            if timeout > 0 and attempts % 5 == 0:
                logger.debug(f"Still waiting for wake word... ({attempts}s)")
        
        logger.warning(f"Timeout waiting for wake word after {timeout} seconds")
        if callback:
            callback(False)
        return False
    
    def capture_command(self, timeout: int = 2) -> Optional[str]:
        """
        Capture user command after wake word.
        
        Args:
            timeout: Seconds to wait for command
            
        Returns:
            Captured command text or None
        """
        import time
        logger.info("🎙️ Listening for command... (speak now)")
        
        # Reduced phrase_time_limit from 8 to 3 seconds - ends listening sooner after speech ends
        # This makes it more responsive to when you finish speaking
        command = self.speech_engine.listen(timeout=timeout, phrase_time_limit=3)
        
        if command:
            # Remove wake word from command if present
            command = clean_text(command)
            if self.wake_word in command:
                command = command.replace(self.wake_word, "").strip()
            
            if command:  # Make sure there's still text after removing wake word
                logger.info(f"✓ Command captured: '{command}'")
                return command
        
        return None
