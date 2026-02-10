import os
try:
    # Provided by the `python-dotenv` package.
    # If your environment doesn't have it installed, we still want JARVIS to run.
    from dotenv import load_dotenv  # type: ignore[import-not-found]
except Exception:
    def load_dotenv(*args, **kwargs):  # type: ignore[no-redef]
        return False

try:
    # Groq Python SDK (https://pypi.org/project/groq/)
    from groq import Groq  # type: ignore[import-not-found]
except Exception:
    Groq = None
try:
    from tavily import TavilyClient  # type: ignore
except Exception:
    TavilyClient = None

try:
    from rich.console import Console  # type: ignore
    console = Console()
except Exception:
    class _ConsoleFallback:
        def print(self, *args, **kwargs):
            print(*args)
    console = _ConsoleFallback()

load_dotenv()

USERNAME = os.getenv("USERNAME", "User")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "JARVIS")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class RealTimeSearch:
    """Search real-time data using Tavily API and refine with AI."""
    
    def __init__(self):
        if Groq and GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY)
        else:
            if not Groq:
                console.print("[yellow]Groq SDK is not installed. AI refinement disabled.[/yellow]")
            elif not GROQ_API_KEY:
                console.print("[yellow]GROQ_API_KEY not found. AI refinement disabled.[/yellow]")
            self.groq_client = None
        if TAVILY_API_KEY and TavilyClient:
            self.tavily = TavilyClient(api_key=TAVILY_API_KEY)  # type: ignore[misc]
        else:
            if not TavilyClient:
                console.print("[yellow]Tavily is not installed. Real-time search disabled.[/yellow]")
            elif not TAVILY_API_KEY:
                console.print("[yellow]TAVILY_API_KEY not found. Real-time search disabled.[/yellow]")
            self.tavily = None
    
    def search(self, query: str) -> str:
        """Search Web and refine results with AI."""
        if not self.tavily:
            return "Search is unavailable (Missing API Key)."

        try:
            # Search Tavily
            console.print(f"[green]Searching Tavily for: {query}...[/green]")
            search_result = self.tavily.search(query, search_depth="basic", max_results=5)
            
            # Format results
            context = "\n".join([
                f"- [{res['title']}]({res['url']}): {res['content']}" 
                for res in search_result.get('results', [])
            ])
            
            if not context:
                return f"No results found for {query}"
            
            # Refine with AI
            refined = self._refine_with_ai(query, context)
            return refined
        
        except Exception as e:
            console.print(f"[red]RealTimeSearch Error: {e}[/red]")
            return f"Unable to search for {query} right now."
            
    def _refine_with_ai(self, query: str, search_data: str) -> str:
        """Refine search results using Groq AI."""
        if not self.groq_client:
            return search_data
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
            
            system_prompt = f"""Hello, I am {USERNAME}, You are a very accurate and advanced AI chatbot named {ASSISTANT_NAME} which has real-time up-to-date information from the internet.
*** Current Date and Time: {current_time} ***
*** Personality: Be concise, direct, and helpful. Do NOT start answers with 'Based on...', 'According to my data...', or 'I can tell you that...'. Just state the facts. ***
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""
            
            user_message = f"Based on this data: {search_data}\n\nAnswer this question: {query}"
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            console.print(f"[yellow]AI Refinement Error: {e}[/yellow]")
            return search_data


class ChatBot:
    """General conversation using Groq AI."""
    
    def __init__(self):
        from jarvis.core.llm import LLM
        self.llm = LLM()
    
    def chat(self, query: str, memory: str = "") -> str:
        """Chat with user using Groq AI."""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
            
            system_prompt = f"""Hello, I am {USERNAME}, You are a very accurate and advanced AI chatbot named {ASSISTANT_NAME} which also has real-time up-to-date information from the internet.
*** Current Date and Time: {current_time} ***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Personality: Be extremely concise, direct, and helpful. Avoid polite filler. Just answer the question. ***
*** Rule: If asked for the time, ONLY mention the time. If asked for the date, ONLY mention the date. Do not combine them unless asked. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. """
            
            # Context is appended to system prompt or user message
            # For Groq/Llama, we pass it as system_instruction
            if memory:
                system_prompt += f"\n\nPrevious context: {memory}"
            
            response = self.llm.chat(
                prompt=query,
                system_instruction=system_prompt,
                json_mode=False
            )
            if not response or not str(response).strip():
                # Most common cause: GROQ not configured or request failed.
                if not GROQ_API_KEY:
                    return "AI chat is unavailable: GROQ_API_KEY is not set. Add it to your .env and restart."
                return "I couldn't generate a response right now. Please try again."

            return response.strip()
        
        except Exception as e:
            console.print(f"[red]ChatBot Error: {e}[/red]")
            return "I'm having trouble responding right now."


class Automation:
    """Automate tasks through JARVIS functions."""
    
    def __init__(self, skills_registry: dict = None):
        """Initialize with registered skills."""
        self.skills = skills_registry or {}
    
    def route_automation(self, category: str, query: str) -> str:
        """Route automation tasks to appropriate skill."""
        category = category.lower().strip()
        
        # Map automation categories to skills
        automation_map = {
            "google search": "web",
            "youtube search": "youtube",
            "play": "youtube",
            "open": "apps",
            "close": "apps",
            "system": "system",
            "context": "basic",
            "weather": "weather",
            "files": "files"
        }
        
        skill_name = automation_map.get(category)
        
        if skill_name and skill_name in self.skills:
            try:
                handler, _ = self.skills[skill_name]
                result = handler(query)
                return result if result else f"Performing: {category}"
            except Exception as e:
                console.print(f"[yellow]Automation Error in {skill_name}: {e}[/yellow]")
                return f"Unable to perform {category}"
        
        return f"Automation for '{category}' not available"
    
    def google_search(self, query: str) -> str:
        """Perform Google search."""
        if "web" in self.skills:
            handler, _ = self.skills["web"]
            return handler(query)
        return "Web search unavailable"
    
    def youtube_search(self, query: str) -> str:
        """Search and play YouTube."""
        if "youtube" in self.skills:
            handler, _ = self.skills["youtube"]
            return handler(query)
        return "YouTube unavailable"
    
    def open_app(self, app_name: str) -> str:
        """Open application."""
        if "apps" in self.skills:
            handler, _ = self.skills["apps"]
            return handler(f"open {app_name}")
        return f"Cannot open {app_name}"
    
    def close_app(self, app_name: str) -> str:
        """Close application."""
        if "apps" in self.skills:
            handler, _ = self.skills["apps"]
            return handler(f"close {app_name}")
        return f"Cannot close {app_name}"
    
    def system_control(self, action: str) -> str:
        """System control (volume, screenshot, etc)."""
        if "system" in self.skills:
            handler, _ = self.skills["system"]
            return handler(action)
        return "System control unavailable"
