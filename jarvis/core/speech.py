"""Speech - Text to Speech."""
import pygame
import random
import asyncio
import edge_tts
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Speaker:
    """Smart TTS using edge-tts and pygame."""
    
    def __init__(self):
        self.voice = os.getenv("ASSISTANT_VOICE", "en-CA-LiamNeural")
        self.cache_dir = Path("data/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        self.responses = [
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
    
    def speak(self, text: str):
        """Speak text using edge-tts with smart truncation."""
        if not text:
            return
        
        try:
            # Check if text is too long
            lines = text.split('\n')
            words = text.split()
            
            if len(lines) > 2 or len(words) > 250:
                # Speak first 2 lines
                speak_text = '\n'.join(lines[:2])
                # Add random response
                speak_text += " " + random.choice(self.responses)
            else:
                speak_text = text
            
            asyncio.run(self._speak_async(speak_text))
        except Exception as e:
            print(f"[TTS Error: {e}]")
    
    async def _speak_async(self, text: str):
        """Async TTS generation and playback."""
        import time
        output = self.cache_dir / f"temp_{int(time.time() * 1000)}.mp3"
        
        # Generate audio
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(str(output))
        
        # Play audio using pygame
        pygame.mixer.music.load(str(output))
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
