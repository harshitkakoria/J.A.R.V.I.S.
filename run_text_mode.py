"""Text mode for JARVIS (no voice)."""
from jarvis.core.brain import Brain
from jarvis.skills import basic, web, youtube, apps, system, weather, files, scrape


def main():
    """Run JARVIS text mode."""
    print("=" * 60)
    print("J.A.R.V.I.S v2.0 - Text Mode")
    print("=" * 60)
    
    # Initialize
    brain = Brain()
    
    # Register all skills
    brain.register("basic", basic.handle, ["time", "date", "joke", "who are you", "exit", "quit"])
    brain.register("web", web.handle, ["search", "google", "open"])
    brain.register("youtube", youtube.handle, ["play", "youtube", "watch"])
    brain.register("apps", apps.handle, ["open", "close", "launch", "start"])
    brain.register("system", system.handle, ["screenshot", "volume", "mute"])
    brain.register("weather", weather.handle, ["weather", "temperature", "forecast"])
    brain.register("files", files.handle, ["create", "delete", "list files"])
    brain.register("scrape", scrape.handle, ["news", "headline", "gold", "stock"])
    
    print("\n✓ JARVIS ready! Type your commands.")
    print("Type 'exit' to quit\n")
    print("💡 Memory enabled:")
    print("   - Say 'my name is [name]' to introduce yourself")
    print("   - Ask 'what did I say' to recall")
    print("   - Type 'remember' to see conversation history\n")
    
    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
            
            # Brain handles memory automatically
            response = brain.process(query)
            print(f"JARVIS: {response}\n")
            
            if any(w in query.lower() for w in ["exit", "quit", "bye"]):
                # Farewell with name
                name = brain.memory.get_context("user_name")
                if name:
                    print(f"JARVIS: Goodbye {name}!\n")
                break
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()
