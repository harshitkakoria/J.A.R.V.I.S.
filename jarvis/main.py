"""Main entry point for JARVIS."""
from pathlib import Path
from jarvis.core.brain import Brain
from jarvis.core.listener import Listener
from jarvis.core.speech import Speaker
from jarvis.utils.helpers import clean_text
from jarvis.skills import basic, web, youtube, apps, system, weather, files, scrape


def main():
    """Run JARVIS voice mode."""
    print("=" * 60)
    print("J.A.R.V.I.S v2.0 - Simple & Fast")
    print("=" * 60)
    
    try:
        # Initialize
        brain = Brain(use_ai_decision=True)
        listener = Listener()
        speaker = Speaker()
        
        # Register all skills
        brain.register("basic", basic.handle, ["time", "date", "joke", "who are you", "exit", "quit", "bye"])
        brain.register("web", web.handle, ["search", "google"])
        brain.register("youtube", youtube.handle, ["play", "youtube", "watch"])
        brain.register("apps", apps.handle, ["open", "close", "launch", "start", "notepad", "calculator", "chrome", "chatgpt", "gemini"])
        brain.register("system", system.handle, ["screenshot", "volume", "mute", "capture"])
        brain.register("weather", weather.handle, ["weather", "temperature", "forecast", "rain", "hot", "cold"])
        brain.register("files", files.handle, ["create file", "create document", "delete file", "list files", "find", "search", "locate", "where is"])
        brain.register("scrape", scrape.handle, ["news", "headline", "gold", "stock", "market"])
        
        # Start listener
        html_path = Path("data/selenium_stt/speech_recognition.html").absolute()
        if not html_path.exists():
            print(f"❌ Error: HTML file not found at {html_path}")
            print("Please ensure data/selenium_stt/speech_recognition.html exists")
            return
        
        listener.start(str(html_path))
        
        print("\n✓ JARVIS is ready! Speak now...")
        print("Say 'exit' to quit\n")
        print("💡 Tips:")
        print("   - Say 'my name is [name]' to introduce yourself")
        print("   - Ask 'what did I say' to recall conversation")
        print("   - I'll remember our last 10 exchanges\n")
        
        # Startup greeting
        greeting = "Hello! I'm JARVIS, your personal assistant. How can I help you today?"
        print(f"🤖 JARVIS: {greeting}")
        speaker.speak(greeting)
        
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Run: pip install selenium webdriver-manager")
        print("   2. Make sure Chrome browser is installed")
        print("   3. Check data/selenium_stt/speech_recognition.html exists")
        return
    
    try:
        waiting_for_input = True
        command_count = 0
        while True:
            try:
                if waiting_for_input:
                    print("\n🎙️  Ready...")
                    waiting_for_input = False
                
                # Listen
                raw_text = listener.listen()
                if not raw_text:
                    continue
                
                waiting_for_input = True
                command_count += 1
                
                # Clean
                query = clean_text(raw_text)
                print(f"\n🎤 You: {query}")
                
                # Pause listener before speaking
                try:
                    listener.start_speaking()
                except:
                    pass
                
                # Process (brain handles memory automatically)
                response = brain.process(query)
                print(f"🤖 JARVIS: {response}")
                
                # Speak (always talk back) with timeout
                try:
                    speaker.speak(response)
                except:
                    print("[TTS skipped]")
                
                # Resume listener after speaking
                try:
                    listener.stop_speaking()
                except:
                    pass
                
                # Exit?
                if any(w in query.lower() for w in ["exit", "quit", "bye"]):
                    # Pause listener before final farewell
                    try:
                        listener.start_speaking()
                    except:
                        pass
                    # Farewell with name if known
                    name = brain.memory.get_context("user_name")
                    farewell = f"Goodbye {name}!" if name else "Goodbye!"
                    print(f"🤖 JARVIS: {farewell}")
                    try:
                        speaker.speak(farewell)
                    except:
                        pass
                    try:
                        listener.stop_speaking()
                    except:
                        pass
                    break
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[Error in loop: {e}]")
                continue
    
    except KeyboardInterrupt:
        print("\n\n🤖 JARVIS: Shutting down. Goodbye!")
        try:
            speaker.speak("Shutting down. Goodbye!")
        except:
            pass
    finally:
        listener.stop()
        print("✓ JARVIS stopped")


if __name__ == "__main__":
    main()
