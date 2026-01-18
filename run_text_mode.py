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
        from jarvis.skills import basic, weather, system, scrape, web, youtube, file_manager, app_control, system_commands
        
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
            "youtube",
            youtube.handle,
            keywords=["youtube", "play", "play video", "play music", "play song", "watch", "search", "search youtube", "find", "look for", "youtube channel", "trending", "subscriptions"]
        )
        
        brain.register_skill(
            "web",
            web.handle,
            keywords=["google search", "search", "browse", "visit", "website", "github", "stackoverflow"]
        )
        
        brain.register_skill(
            "file_manager",
            file_manager.handle,
            keywords=["create file", "delete file", "rename file", "create folder", "delete folder", "list files"]
        )
        
        brain.register_skill(
            "app_control",
            app_control.handle,
            keywords=["chrome", "google chrome", "vlc", "close tab", "close this tab", "close the tab", "close these tabs", "close all tabs", "close window", "close this window", "close the window", "switch window", "minimize", "maximize", "notepad", "calculator", "paint", "explorer", "task manager"]
        )
        
        brain.register_skill(
            "system_commands",
            system_commands.handle,
            keywords=["execute", "run command", "system command"]
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
