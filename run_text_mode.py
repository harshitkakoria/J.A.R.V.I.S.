"""Text mode for JARVIS (no voice)."""
from jarvis.core.brain import Brain
from importlib import import_module


def _optional_import(module_path: str):
    """Import a skill module if its dependencies are installed."""
    try:
        return import_module(module_path)
    except Exception as e:
        print(f"[!] Skill disabled: {module_path} ({e})")
        return None


def main():
    """Run JARVIS text mode."""
    print("=" * 60)
    print("J.A.R.V.I.S v2.0 - Text Mode")
    print("=" * 60)
    
    # Initialize
    brain = Brain(use_ai_decision=True)
    
    # Register all skills
    basic = _optional_import("jarvis.skills.basic")
    web = _optional_import("jarvis.skills.web")
    youtube = _optional_import("jarvis.skills.youtube")
    apps = _optional_import("jarvis.skills.apps")
    system = _optional_import("jarvis.skills.system")
    weather = _optional_import("jarvis.skills.weather")

    if basic:
        brain.register("basic", basic.handle, ["time", "date", "joke", "who are you", "exit", "quit"])
    if web:
        brain.register("web", web.handle, ["search", "google", "open"])
    if youtube:
        brain.register("youtube", youtube.handle, ["play", "youtube", "watch"])
    if apps:
        brain.register("apps", apps.handle, ["open", "close", "launch", "start"])
    if system:
        brain.register("system", system.handle, ["screenshot", "volume", "mute"])
    if weather:
        brain.register("weather", weather.handle, ["weather", "temperature", "forecast"])
    
    print("\n[OK] JARVIS ready! Type your commands.")
    print("Type 'exit' to quit\n")
    print("[Tip] Memory enabled:")
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
