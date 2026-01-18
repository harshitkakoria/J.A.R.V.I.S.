"""
AI-powered intent parser: Converts natural language to structured commands.
Uses OpenRouter Llama 3 8B to understand user intent.
"""
import json
import requests
from typing import Dict, Optional, List
from jarvis.utils.logger import setup_logger
from jarvis.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

logger = setup_logger(__name__)


class IntentParser:
    """Parse natural language commands using AI (Llama 3 8B)"""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        if not self.api_key:
            logger.warning("⚠️ OPENROUTER_API_KEY not configured - AI intent parsing disabled")
    
    def parse_command(self, user_input: str) -> Dict:
        """
        Convert natural language to structured command.
        
        Args:
            user_input: What user said (e.g., "open chrome and search for python")
            
        Returns:
            Dict with structure:
            {
                'intent': 'command_type',
                'action': 'what_to_do',
                'target': 'object_of_action',
                'params': {},
                'confidence': 0.0-1.0,
                'commands': [list of sequential commands if multi-command]
            }
        """
        if not user_input or not user_input.strip():
            return {"intent": "unknown", "confidence": 0.0}
        
        # Skip AI parsing if API key not configured
        if not self.api_key:
            logger.debug("API key not configured, skipping AI intent parsing")
            return {"intent": "unknown", "confidence": 0.0}
        
        # Local heuristic: detect simple greetings to avoid false positives
        greeting_response = self._detect_greeting(user_input)
        if greeting_response:
            return greeting_response
        
        prompt = self._build_prompt(user_input)
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500,
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract JSON from response
                try:
                    command = json.loads(text)
                    logger.info(f"AI parsed intent: {command.get('intent')} | confidence: {command.get('confidence')}")
                    return command
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse AI response as JSON: {text[:100]}")
                    return {"intent": "unknown", "confidence": 0.0}
            else:
                logger.error(f"AI API error: {response.status_code} - {response.text[:200]}")
                return {"intent": "error", "confidence": 0.0}
                
        except Exception as e:
            logger.error(f"Intent parsing error: {e}")
            return {"intent": "error", "confidence": 0.0}
    
    def _detect_greeting(self, user_input: str) -> Optional[Dict]:
        """
        Local heuristic: detect simple greetings without API call.
        Returns greeting response or None if not a greeting.
        """
        greetings = {
            "hi": "Hello! How can I help?",
            "hello": "Hello! What do you need?",
            "hey": "Hey there! What's up?",
            "sup": "What's up! How can I assist?",
            "hya": "Hi! How can I help?",
            "hlo": "Hello! What do you need?",  # typo
            "hellow": "Hello! What can I do for you?",  # typo
        }
        cleaned = user_input.lower().strip()
        if cleaned in greetings:
            return {
                "intent": "greeting",
                "action": "respond",
                "target": cleaned,
                "response": greetings[cleaned],
                "confidence": 1.0,
                "reasoning": "Local greeting detection"
            }
        return None
    
    def _build_prompt(self, user_input: str) -> str:
        """Build the AI prompt for command interpretation."""
        return f"""You are a command interpreter for a personal AI assistant. Convert the user's natural language request into structured commands.

USER REQUEST: "{user_input}"

Respond with ONLY valid JSON (no markdown, no explanations, no extra text):

{{
    "intent": "one of: [open_app, close_app, close_window, close_all_tabs, take_screenshot, get_weather, search_web, open_website, delete_file, create_file, list_files, rename_file, get_info, tell_joke, get_time, shutdown, restart, volume_control, youtube_play, youtube_search, youtube_channel, youtube_trending]",
    "action": "specific action to perform",
    "target": "object/app/file name (what to act on)",
    "params": {{"confirm_needed": false, "multi_command": false}},
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of interpretation",
    "commands": []
}}

INTERPRETATION RULES:
- "open my files" / "show desktop" → intent: open_app, target: explorer
- "close the tab" / "shut this tab" → intent: close_app, target: current_tab
- "take a pic" / "capture screen" → intent: take_screenshot
- "what's the weather" / "is it hot" → intent: get_weather
- "search for X" / "google X" → intent: search_web, target: X
- "delete that file" → intent: delete_file, target: that file (set confirm_needed: true)
- "create a new note" → intent: create_file, target: note
- "tell me a joke" → intent: tell_joke
- "what time is it" → intent: get_time
- "shut down" / "turn off pc" → intent: shutdown (set confirm_needed: true)
- "play python tutorial on youtube" → intent: youtube_play, target: python tutorial
- "search for funny cats on youtube" → intent: youtube_search, target: funny cats
- "watch avengers trailer" → intent: youtube_play, target: avengers trailer
- "open MrBeast channel" → intent: youtube_channel, target: MrBeast
- "show me trending videos" → intent: youtube_trending
- "open chrome and search for python then take screenshot" → multi_command: true, commands: [open_app, search_web, take_screenshot]
- Speech accent/typos: "opne" → "open", "calculater" → "calculator", "shdown" → "shutdown"

IMPORTANT:
1. Be smart about context (typos, accents, slang)
2. Detect dangerous operations (shutdown, delete) and set confirm_needed: true
3. For unclear requests, ask clarification or set confidence low
4. Support multi-commands (multiple actions in one sentence)
5. Extract exact app/file names when possible
"""


class CommandExecutor:
    """Execute parsed commands by routing to appropriate skills"""
    
    def __init__(self, brain=None):
        self.brain = brain
    
    def execute(self, command: Dict) -> str:
        """
        Execute a parsed command.
        
        Args:
            command: Parsed command dict from IntentParser
            
        Returns:
            Result message from skill execution
        """
        intent = command.get("intent", "unknown")
        target = command.get("target", "")
        params = command.get("params", {})
        
        # Safety check for dangerous operations
        if params.get("confirm_needed") and not params.get("confirmed"):
            return f"This action requires confirmation. Please say 'confirm' or 'yes' to proceed."
        
        try:
            # Route to appropriate skill based on intent
            if intent == "open_app":
                from jarvis.skills.app_control import open_program, open_desktop_app
                # Try built-in programs first
                result = open_program(f"open {target}")
                if result and "not recognized" in result.lower():
                    result = open_desktop_app(f"open {target}")
                return result if result else f"Attempting to open {target}"
            
            elif intent == "close_app" or intent == "close_window":
                from jarvis.skills.app_control import close_window, close_tab
                if target and "tab" in target.lower():
                    return close_tab()
                else:
                    return close_window()
            
            elif intent == "close_all_tabs":
                from jarvis.skills.app_control import close_tab
                return close_tab()
            
            elif intent == "take_screenshot":
                from jarvis.skills.system import take_screenshot
                return take_screenshot()
            
            elif intent == "get_weather":
                from jarvis.skills.weather import handle as weather_handle
                return weather_handle("weather")
            
            elif intent == "search_web":
                from jarvis.skills.web import handle as web_handle
                return web_handle(f"search {target}")
            
            elif intent == "open_website":
                from jarvis.skills.web import handle as web_handle
                return web_handle(f"open {target}")
            
            elif intent == "delete_file":
                from jarvis.skills.file_manager import handle as fm_handle
                confirm_word = "confirm" if params.get("confirmed") else ""
                return fm_handle(f"delete file {target} {confirm_word}")
            
            elif intent == "create_file":
                from jarvis.skills.file_manager import handle as fm_handle
                return fm_handle(f"create file {target}")
            
            elif intent == "list_files":
                from jarvis.skills.file_manager import handle as fm_handle
                return fm_handle("list files")
            
            elif intent == "rename_file":
                from jarvis.skills.file_manager import handle as fm_handle
                new_name = params.get("new_name", "")
                return fm_handle(f"rename file {target} to {new_name}")
            
            elif intent == "tell_joke":
                from jarvis.skills.basic import handle as basic_handle
                return basic_handle("tell me a joke")
            
            elif intent == "get_time":
                from jarvis.skills.basic import handle as basic_handle
                return basic_handle("what time is it")
            
            elif intent == "shutdown":
                from jarvis.skills.system import handle as system_handle
                confirm_word = "confirm" if params.get("confirmed") else ""
                return system_handle(f"shutdown {confirm_word}")
            
            elif intent == "restart":
                from jarvis.skills.system import handle as system_handle
                confirm_word = "confirm" if params.get("confirmed") else ""
                return system_handle(f"restart {confirm_word}")
            
            elif intent == "volume_control":
                from jarvis.skills.system import handle as system_handle
                action = target if target else "mute"
                return system_handle(f"{action} volume")
            
            elif intent == "youtube_play":
                from jarvis.skills.youtube import play_video
                return play_video(f"play {target}")
            
            elif intent == "youtube_search":
                from jarvis.skills.youtube import search_youtube
                return search_youtube(f"search {target}")
            
            elif intent == "youtube_channel":
                from jarvis.skills.youtube import open_channel
                return open_channel(f"open {target} channel")
            
            elif intent == "youtube_trending":
                from jarvis.skills.youtube import open_trending
                return open_trending()
            
            elif intent == "get_info":
                # Use AI for general information
                return self._get_info(target or command.get("action", ""))
            
            else:
                return "I didn't understand that command. Could you rephrase it?"
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
    
    def _get_info(self, query: str) -> str:
        """Get general information using AI."""
        try:
            if not self.brain:
                return "AI information service not available"
            
            # Use brain's LLM response function
            if hasattr(self.brain, '_llm_response'):
                return self.brain._llm_response(query)
            else:
                return "Could not retrieve information"
        except Exception as e:
            logger.error(f"Error getting info: {e}")
            return f"Error: {str(e)}"
