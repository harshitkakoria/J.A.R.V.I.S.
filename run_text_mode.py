#!/usr/bin/env python3
"""
JARVIS in TEXT MODE (no microphone needed)
Type commands instead of speaking
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from jarvis.core.speech import SpeechEngine
from jarvis.core.brain import Brain
from jarvis.core.response import ResponseHandler
from jarvis.settings import UserSettings
from jarvis.skills import basic
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main entry point - TEXT MODE."""
    try:
        # Load settings
        settings = UserSettings.load()
        
        # Initialize components
        speech_engine = SpeechEngine(
            rate=settings.voice_rate,
            volume=settings.voice_volume,
            voice_id=settings.voice_id
        )
        brain = Brain()
        response_handler = ResponseHandler(speech_engine)
        
        # Register skills
        from jarvis.skills import basic, weather, system, scrape, web
        
        brain.register_skill(
            "basic",
            basic.handle,
            keywords=["time", "date", "joke", "wikipedia", "who are you", "exit", "bye", "what is", "who is"]
        )
        
        brain.register_skill(
            "weather",
            weather.handle,
            keywords=["weather", "temperature", "forecast", "rain", "hot", "cold", "climate"]
        )
        
        brain.register_skill(
            "system",
            system.handle,
            keywords=["screenshot", "shutdown", "restart", "reboot", "volume", "mute", "quiet", "loud"]
        )
        
        brain.register_skill(
            "scrape",
            scrape.handle,
            keywords=["news", "headline", "gold", "stock", "market", "price"]
        )
        
        brain.register_skill(
            "web",
            web.handle,
            keywords=["google", "youtube", "search", "play", "open", "visit", "website", "github", "stackoverflow"]
        )
        
        # Greeting
        greeting = f"Hello {settings.name}, I am JARVIS (TEXT MODE). Type 'exit' to quit."
        print(f"\nJARVIS: {greeting}\n")
        response_handler.respond(greeting)
        
        # Main loop
        while True:
            # Get text input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Process command
            response = brain.process(user_input)
            
            # Handle exit
            if response and any(kw in response.lower() for kw in ["goodbye", "bye"]):
                print(f"\nJARVIS: {response}\n")
                response_handler.respond(response)
                break
            
            # Respond
            if response:
                print(f"\nJARVIS: {response}\n")
                response_handler.respond(response)
            else:
                fallback = "I didn't catch that. Could you rephrase?"
                print(f"\nJARVIS: {fallback}\n")
                response_handler.respond(fallback)
                
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
