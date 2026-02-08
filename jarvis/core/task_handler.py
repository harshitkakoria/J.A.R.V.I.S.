"""Task Handlers - RealTimeSearch, ChatBot, Automation."""
import os
import requests
from bs4 import BeautifulSoup
import groq
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()

console = Console()

USERNAME = os.getenv("USERNAME", "User")
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "JARVIS")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class RealTimeSearch:
    """Search real-time data from Google and refine with AI."""
    
    def __init__(self):
        self.groq_client = groq.Groq(api_key=GROQ_API_KEY)
    
    def search(self, query: str) -> str:
        """Search Google and refine results with AI."""
        try:
            # Search Google
            search_results = self._google_search(query)
            
            if not search_results:
                return f"No results found for {query}"
            
            # Refine with AI
            refined = self._refine_with_ai(query, search_results)
            return refined
        
        except Exception as e:
            console.print(f"[red]RealTimeSearch Error: {e}[/red]")
            return f"Unable to search for {query} right now."
    
    def _google_search(self, query: str, num_results: int = 3) -> str:
        """Search Google for information."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            search_url = f"https://www.google.com/search?q={query}"
            
            # Note: This is a simplified approach. For production, use Google API or SerpAPI
            response = requests.get(search_url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract snippets
            for g in soup.find_all('div', class_='g'):
                text = g.get_text()
                if text and len(results) < num_results:
                    results.append(text[:200])
            
            return "\n".join(results) if results else f"Search results for: {query}"
        
        except Exception as e:
            console.print(f"[yellow]Search fallback: {e}[/yellow]")
            return f"Searching for {query}..."
    
    def _refine_with_ai(self, query: str, search_data: str) -> str:
        """Refine search results using Groq AI."""
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
*** Personality: Be conversational, natural, and helpful. Speak in full sentences as an assistant ***
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
            
            return response
        
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
            "weather": "weather"
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
