"""
Speech-to-Text (STT) and Text-to-Speech (TTS) functionality.
"""
import pyttsx3
import speech_recognition as sr
from typing import Optional
from jarvis.utils.logger import setup_logger
from jarvis.config import USE_WHISPER, WHISPER_MODEL

logger = setup_logger(__name__)


class SpeechEngine:
    """Handles both STT and TTS operations."""
    
    def __init__(self, rate: int = 150, volume: float = 0.9, voice_id: int = 0):
        """
        Initialize speech engine.
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice index
        """
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.set_voice_properties(rate, volume, voice_id)
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.tts_engine = None
        
        # Initialize STT
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Microphone initialized successfully")
        except Exception as e:
            logger.warning(f"Microphone initialization failed: {e}")
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: int = None):
        """Set TTS voice properties."""
        if not self.tts_engine:
            return
        
        if rate is not None:
            self.tts_engine.setProperty('rate', rate)
        if volume is not None:
            self.tts_engine.setProperty('volume', volume)
        if voice_id is not None:
            voices = self.tts_engine.getProperty('voices')
            if voices and voice_id < len(voices):
                self.tts_engine.setProperty('voice', voices[voice_id].id)
    
    def speak(self, text: str) -> None:
        """
        Convert text to speech and speak it.
        
        Args:
            text: Text to speak
        """
        if not self.tts_engine:
            print(f"JARVIS: {text}")  # Fallback to print
            return
        
        try:
            logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            print(f"JARVIS: {text}")  # Fallback
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Seconds to wait for speech
            phrase_time_limit: Maximum seconds for phrase
            
        Returns:
            Recognized text or None
        """
        if not self.microphone:
            logger.error("Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                logger.debug("Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try faster-whisper first if enabled, else fallback to Google
            if USE_WHISPER:
                try:
                    # Note: faster-whisper integration would go here
                    # For now, fallback to Google
                    text = self.recognizer.recognize_google(audio)
                except:
                    text = self.recognizer.recognize_google(audio)
            else:
                text = self.recognizer.recognize_google(audio)
            
            logger.info(f"Recognized: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            logger.debug("No speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"STT service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in listen: {e}")
            return None
