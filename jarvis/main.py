"""
Main entry point for JARVIS.
Starts the listening loop and handles the greeting.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Core imports
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
    # Import skills with error handling (lazy imports to avoid circular dependencies)
    skills_to_register = []
    
    # Basic skill (required)
    try:
        from jarvis.skills import basic
        skills_to_register.append(("basic", basic.handle, ["time", "date", "joke", "wikipedia", "who are you", "exit", "bye", "what is", "who is"]))
    except ImportError as e:
        logger.error(f"Could not import basic skill: {e}")
        return  # Cannot continue without basic skill
    
    # Optional skills
    optional_skills = [
        ("weather", ["weather", "temperature", "forecast", "rain", "hot", "cold", "climate"]),
        ("system", ["screenshot", "shutdown", "restart", "reboot", "volume", "mute", "quiet", "loud"]),
        ("scrape", ["news", "headline", "gold", "stock", "market", "price"]),
        ("web", ["google", "youtube", "search", "play", "open", "visit", "website", "github", "stackoverflow"]),
        ("file_manager", ["create file", "delete file", "rename file", "create folder", "delete folder", "list files", "show files"]),
        ("app_control", ["close tab", "close window", "switch window", "minimize", "maximize", "notepad", "calculator", "paint", "explorer", "task manager"]),
        ("system_commands", ["execute", "run command", "system command"]),
    ]
    
    for skill_name, keywords in optional_skills:
        try:
            skill_module = __import__(f"jarvis.skills.{skill_name}", fromlist=[skill_name])
            skills_to_register.append((skill_name, skill_module.handle, keywords))
        except (ImportError, AttributeError) as e:
            logger.debug(f"Skill '{skill_name}' not available: {e}")
    
    # Register all available skills
    for skill_name, handler, keywords in skills_to_register:
        brain.register_skill(skill_name, handler, keywords)
    
    logger.info(f"Registered {len(skills_to_register)} skill(s)")


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
        logger.info("Entering main loop - say 'goodbye' to exit")
        attempt_count = 0
        max_consecutive_failures = 3
        
        while True:
            try:
                # Wait for wake word (if enabled) with timeout
                if settings.use_wake_word:
                    logger.info("Listening for wake word 'jarvis'...")
                    if not listener.wait_for_wake_word(timeout=60):
                        logger.info("No wake word detected, restarting...")
                        continue
                    # Acknowledge wake word
                    response_handler.acknowledge()
                else:
                    logger.info("Ready for command...")
                
                # Capture command
                logger.debug("Listening for command...")
                command = listener.capture_command(timeout=5)
                
                if not command:
                    logger.debug("No command captured, try again")
                    attempt_count += 1
                    if attempt_count >= max_consecutive_failures:
                        response_handler.respond("I didn't catch that. Please try again.")
                        attempt_count = 0
                    continue
                
                # Reset failure counter on successful capture
                attempt_count = 0
                
                logger.info(f"Command received: {command}")
                # Process command
                response = brain.process(command)
                
                # Handle exit
                if response and any(kw in response.lower() for kw in ["goodbye", "bye", "see you"]):
                    response_handler.respond(response)
                    logger.info("Shutting down JARVIS")
                    break
                
                # Respond with TTS
                if response:
                    response_handler.respond(response)
                else:
                    response_handler.respond("I didn't understand that. Could you rephrase?")
                    
            except KeyboardInterrupt:
                logger.info("Interrupted by user (Ctrl+C)")
                response_handler.respond("Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                response_handler.respond("Sorry, I encountered an error. Please try again.")
                attempt_count += 1
                if attempt_count >= max_consecutive_failures:
                    logger.error("Too many errors, restarting...")
                    attempt_count = 0
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
