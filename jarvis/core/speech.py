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
            # Add small delay to ensure clean audio output
            import time
            time.sleep(0.2)
        except Exception as e:
            logger.error(f"Error in TTS: {e}")
            print(f"JARVIS: {text}")  # Fallback to print
            # Try to reinitialize TTS engine
            try:
                self.tts_engine.stop()
            except:
                pass
            try:
                self.tts_engine = pyttsx3.init()
                self.set_voice_properties(150, 0.9, 0)
                logger.info("TTS engine reinitialized")
            except Exception as reinit_error:
                logger.error(f"Failed to reinitialize TTS: {reinit_error}")
                self.tts_engine = None
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 5) -> Optional[str]:
        """
        Listen for speech and convert to text using Google Speech Recognition.
        Optimized with better noise handling and retries.
        
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
                # Optimize recognizer settings for better accuracy
                self.recognizer.energy_threshold = 3000  # More lenient with quiet speech
                self.recognizer.dynamic_energy_threshold = True  # Auto-adjust to environment
                self.recognizer.phrase_threshold = 0.1  # Lower threshold (default 0.3)
                self.recognizer.pause_threshold = 1.0  # Wait 1 second of silence before stopping (default 0.8)
                self.recognizer.non_speaking_duration = 0.5  # Minimum silence duration (default 0.5)
                
                logger.debug("Adjusting for ambient noise...")
                # Longer noise adjustment for better calibration
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.debug("Listening for speech...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            logger.debug("Processing audio with Google Speech Recognition...")
            
            # Try with retry logic for robustness
            try:
                text = self.recognizer.recognize_google(audio)
                logger.info(f"✓ Recognized: {text}")
                return text.lower()
            except sr.UnknownValueError as e:
                # Audio detected but not recognized - could be too quiet or unclear
                logger.warning(f"❓ Could not understand audio clearly")
                logger.debug(f"   Audio captured but recognition failed: {e}")
                logger.info("   Suggestions:")
                logger.info("   • Speak louder or closer to microphone")
                logger.info("   • Reduce background noise")
                logger.info("   • Speak at normal pace")
                return None
            
        except sr.WaitTimeoutError:
            logger.debug("⏱ Timeout - no speech detected (silent for too long)")
            return None
        except sr.RequestError as e:
            if "Failed to connect" in str(e) or "HTTPSConnectionPool" in str(e):
                logger.error(f"🌐 No internet connection - cannot use Google Speech Recognition")
                logger.info("   Solutions:")
                logger.info("   1. Check your internet connection")
                logger.info("   2. Use text mode: run_text_mode.bat")
            else:
                logger.error(f"Speech Recognition API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during speech recognition: {e}")
            return None
