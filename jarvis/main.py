"""
Main entry point for JARVIS.
Starts the listening loop and handles the greeting.
"""
import sys
from jarvis.core.speech import SpeechEngine
from jarvis.core.listener import Listener
from jarvis.core.brain import Brain
from jarvis.core.response import ResponseHandler
from jarvis.settings import UserSettings
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def greet(settings: UserSettings, response_handler: ResponseHandler):
    """Greet the user on startup."""
    greeting = f"Hello {settings.name}, I am JARVIS. How can I assist you today?"
    logger.info("Starting JARVIS")
    response_handler.respond(greeting)


def register_skills(brain: Brain):
    """Register all available skills with the brain."""
    from jarvis.skills import basic
    
    # Register basic skills
    brain.register_skill(
        "basic",
        basic.handle,
        keywords=["time", "date", "joke", "wikipedia", "who are you", "exit", "bye", "what is", "who is"]
    )
    
    logger.info("Skills registered")


def main():
    """Main entry point."""
    try:
        # Load settings
        settings = UserSettings.load()
        
        # Initialize speech engine
        speech_engine = SpeechEngine(
            rate=settings.voice_rate,
            volume=settings.voice_volume,
            voice_id=settings.voice_id
        )
        
        # Initialize components
        listener = Listener(
            speech_engine=speech_engine,
            wake_word=settings.wake_word,
            use_wake_word=settings.use_wake_word
        )
        brain = Brain()
        response_handler = ResponseHandler(speech_engine)
        
        # Register skills
        register_skills(brain)
        
        # Greet user
        greet(settings, response_handler)
        
        # Main loop
        logger.info("Entering main loop")
        while True:
            try:
                # Wait for wake word (if enabled)
                if settings.use_wake_word:
                    if not listener.wait_for_wake_word():
                        continue
                
                # Acknowledge wake word
                response_handler.acknowledge()
                
                # Capture command
                command = listener.capture_command(timeout=5)
                
                if not command:
                    logger.debug("No command captured")
                    continue
                
                # Process command
                response = brain.process(command)
                
                # Handle exit
                if response and any(kw in response.lower() for kw in ["goodbye", "bye"]):
                    response_handler.respond(response)
                    logger.info("Shutting down")
                    break
                
                # Respond
                if response:
                    response_handler.respond(response)
                else:
                    response_handler.respond("I didn't catch that. Could you repeat?")
                    
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                response_handler.respond("Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                response_handler.respond("Sorry, I encountered an error. Please try again.")
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
