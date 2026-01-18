"""
Speech-to-Text (STT) and Text-to-Speech (TTS) functionality.
STT: Selenium + Chrome Web Speech API
TTS: Edge TTS
"""
import threading
import platform
from typing import Optional, Callable
from jarvis.utils.logger import setup_logger
from dotenv import dotenv_values

logger = setup_logger(__name__)


class SpeechEngine:
    """Handles both STT and TTS operations."""
    
    def __init__(self, rate: int = 150, volume: float = 0.9, voice_id: int = 0, use_selenium_stt: bool = True):
        """
        Initialize speech engine.
        
        Args:
            rate: Speech rate (words per minute) - unused, for compatibility
            volume: Volume level (0.0 to 1.0) - unused, for compatibility
            voice_id: Voice index - unused, for compatibility
            use_selenium_stt: Always True (only STT method)
        """
        self.selenium_stt = None
        
        # Initialize Edge TTS
        try:
            from jarvis.core.TextToSpeech import TextToSpeech
            self.tts_engine = TextToSpeech()
            logger.info("Edge TTS initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Edge TTS: {e}")
            self.tts_engine = None
        
        # Initialize Selenium STT
        try:
            from jarvis.core.SeleniumSTT import SeleniumSTT
            env_config = dotenv_values()
            stt_language = env_config.get("STT_INPUT_LANGUAGE", "en")
            self.selenium_stt = SeleniumSTT(headless=True, language=stt_language, timeout=10)
            logger.info(f"Selenium STT initialized (Web Speech API, headless) - Language: {stt_language}")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium STT: {e}")
            self.selenium_stt = None
    
    def speak(self, text: str, threaded: bool = False) -> Optional[threading.Thread]:
        """
        Convert text to speech using Edge TTS with male voice.
        
        Args:
            text: Text to speak
            threaded: If True, speak in background thread (non-blocking)
            
        Returns:
            Thread object if threaded=True, None otherwise
        """
        if not self.tts_engine:
            print(f"JARVIS: {text}")
            return None
        
        try:
            return self.tts_engine.speak(text, threaded=threaded)
        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            print(f"JARVIS: {text}")
            return None
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """
        Listen for speech and convert to text using Selenium Web Speech API.
        
        Args:
            timeout: Seconds to wait for speech
            phrase_time_limit: Maximum seconds for phrase
            
        Returns:
            Recognized text or None
        """
        # Audible cue: start listening (Windows only)
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(800, 150)  # frequency, duration(ms)
        except Exception:
            pass

        # Use Selenium STT
        if not self.selenium_stt:
            logger.error("Selenium STT not initialized")
            return None
        
        result = self.selenium_stt.listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
        
        # Audible cue: stop listening (Windows only)
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.Beep(600, 120)
        except Exception:
            pass
        
        return result
