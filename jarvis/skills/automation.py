"""
Automation skills: Google search, content generation, YouTube search/play, app control.
Provides web automation, content creation, and system app management.
Supports both sync and async operations for concurrent execution.
"""
import asyncio
import webbrowser
import subprocess
import os
import json
import psutil
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import quote
import time
from jarvis.utils.logger import setup_logger
from jarvis.config import DATA_DIR
from jarvis.skills import app_control

logger = setup_logger(__name__)

# Common app paths on Windows
APP_PATHS = {
    "chrome": [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ],
    "firefox": [
        "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
    ],
    "notepad": [
        "C:\\Windows\\System32\\notepad.exe",
    ],
    "notepad++": [
        "C:\\Program Files\\Notepad++\\notepad++.exe",
        "C:\\Program Files (x86)\\Notepad++\\notepad++.exe",
    ],
    "settings": ["ms-settings:"],
    "vscode": [
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    ],
    "vlc": [
        "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
        "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe",
    ],
    "excel": [
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
        "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
    ],
    "word": [
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    ],
    "powerpoint": [
        "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
        "C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
    ],
    "calculator": [
        "C:\\Windows\\System32\\calc.exe",
    ],
    "paint": [
        "C:\\Windows\\System32\\mspaint.exe",
    ],
    "task manager": [
        "C:\\Windows\\System32\\taskmgr.exe",
    ],
    "settings": [
        "ms-settings:",
    ],
    "figma": [
        "C:\\Users\\{}\\AppData\\Local\\Figma\\Figma.exe",
        "C:\\Program Files\\Figma\\Figma.exe",
        "C:\\Program Files (x86)\\Figma\\Figma.exe",
    ],
}

# App website URLs (fallback if not installed)
APP_WEBSITES = {
    "chrome": "https://www.google.com/chrome/",
    "firefox": "https://www.mozilla.org/firefox/",
    "notepad++": "https://notepad-plus-plus.org/",
    "vscode": "https://code.visualstudio.com/",
    "vlc": "https://www.videolan.org/vlc/",
    "excel": "https://www.microsoft.com/microsoft-365/excel",
    "word": "https://www.microsoft.com/microsoft-365/word",
    "powerpoint": "https://www.microsoft.com/microsoft-365/powerpoint",
    "gimp": "https://www.gimp.org/",
    "blender": "https://www.blender.org/",
    "figma": "https://www.figma.com/",
    "chatgpt": "https://chat.openai.com/",
    "chat gpt": "https://chat.openai.com/",
    "gemini": "https://gemini.google.com/",
    "claude": "https://claude.ai/",
    "spotify": "https://open.spotify.com/",
    "netflix": "https://www.netflix.com/",
    "youtube": "https://www.youtube.com/",
    "gmail": "https://mail.google.com/",
    "outlook": "https://outlook.office.com/",
    "discord": "https://discord.com/app",
    "slack": "https://slack.com/",
    "notion": "https://www.notion.so/",
    "trello": "https://trello.com/",
    "whatsapp": "https://web.whatsapp.com/",
}


def handle(query: str, brain=None) -> Optional[str]:
    """
    Handle automation commands.
    
    Args:
        query: User query
        brain: Brain instance for context
        
    Returns:
        Response text or None
    """
    query_lower = query.lower()
    close_keywords = ["close", "shut", "exit", "kill", "stop"]
    open_keywords = ["open", "launch", "start", "run"]
    
    # Google search (automation workflow - different from web.py interactive search)
    if any(kw in query_lower for kw in ["google search", "search google", "google", "search for"]):
        return google_search(query)
    
    # Document generation (renamed to avoid conflict with file_manager.py)
    if any(kw in query_lower for kw in ["write content", "generate content", "create content", "write article", "write blog"]):
        return generate_document_content(query, brain)
    
    # Note: YouTube commands removed - handled by dedicated youtube.py skill
    # This prevents duplicate routing and maintains separation of concerns

    # Close app before open to avoid misrouting (e.g., "close settings" should not open Settings)
    if any(kw in query_lower for kw in close_keywords):
        return close_app(query)

    # Open app (explicit open verbs or known app names)
    if any(kw in query_lower for kw in open_keywords) or any(app in query_lower for app in APP_PATHS.keys()):
        return open_app(query)
    
    return None


def google_search(query: str) -> str:
    """
    Automated Google search for automation workflows.
    
    Note: Different from web.py::open_google() which is for interactive browsing.
    This function is optimized for automation tasks and batch operations.
    
    Args:
        query: Search query
        
    Returns:
        Confirmation message
    """
    try:
        # Extract search term
        search_keywords = ["google search", "search google", "google", "search for"]
        search_term = query
        
        for kw in search_keywords:
            if kw in query.lower():
                search_term = query.lower().replace(kw, "").strip()
                break
        
        if not search_term or len(search_term) < 2:
            return "Please specify what you want to search for."
        
        # Create Google search URL
        search_url = f"https://www.google.com/search?q={quote(search_term)}"
        
        logger.info(f"Opening Google search for: {search_term}")
        webbrowser.open(search_url)
        
        return f"Searching Google for '{search_term}'. Opening in your browser."
    
    except Exception as e:
        logger.error(f"Google search error: {e}")
        return "Sorry, I couldn't perform the Google search."


def generate_document_content(query: str, brain=None) -> str:
    """
    Generate content on a topic using LLM and save to file.
    
    Note: Renamed from generate_content() to avoid conflict with file_manager.py
    
    Args:
        query: Content topic
        brain: Brain instance for LLM access
        
    Returns:
        Confirmation message
    """
    try:
        # Extract topic
        content_keywords = ["write content", "generate content", "create content", "write article", "write blog"]
        topic = query
        
        for kw in content_keywords:
            if kw in query.lower():
                topic = query.lower().replace(kw, "").strip()
                break
        
        if not topic or len(topic) < 3:
            return "Please specify what content topic you want me to write about."
        
        # Sanitize filename
        filename = topic.replace(" ", "_")[:30] + ".txt"
        filepath = DATA_DIR / filename
        
        logger.info(f"Generating content for: {topic}")
        
        # Generate content using LLM
        content_prompt = f"""Write a well-structured article about: {topic}

Include:
- Introduction
- Main points
- Conclusion

Make it informative and engaging."""
        
        # Use brain's LLM if available
        if brain and hasattr(brain, 'intent_parser'):
            try:
                content = brain.intent_parser.extract_intent(content_prompt)
                if isinstance(content, dict) and 'response' in content:
                    generated_text = content['response']
                else:
                    generated_text = str(content)
            except:
                generated_text = f"Content about {topic}\n\nThis is a placeholder content.\n" + content_prompt
        else:
            # Fallback: use simple template
            generated_text = f"""Article: {topic}

Introduction:
This article discusses {topic} in detail.

Main Points:
1. Overview of {topic}
2. Key aspects and features
3. Applications and benefits
4. Recent developments

Conclusion:
{topic} continues to be an important topic of interest.

For more detailed information, please research further."""
        
        # Save to file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Topic: {topic}\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            f.write(generated_text)
        
        logger.info(f"Content saved to: {filepath}")
        
        # Open in notepad
        try:
            subprocess.Popen(["notepad.exe", str(filepath)])
            return f"Content on '{topic}' generated and opened in Notepad."
        except:
            return f"Content saved to {filepath}, but couldn't open in Notepad."
    
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        return "Sorry, I couldn't generate the content."


# YouTube functions removed - use dedicated youtube.py skill instead
# This prevents duplicate functionality and maintains clean separation
# For YouTube operations, the brain will route to youtube.py skill


def open_app(query: str) -> str:
    """
    Open an application if installed, otherwise open its website.
    
    Args:
        query: App name
        
    Returns:
        Confirmation message
    """
    try:
        # Extract app name
        open_keywords = ["open", "launch", "start", "run"]
        app_name = query.lower()

        for kw in open_keywords:
            app_name = app_name.replace(kw, "").strip()

        if not app_name or len(app_name) < 2:
            return "Please specify which app you want to open."

        app_name = app_name.strip()

        # Special case: Windows Settings
        if "settings" in app_name:
            try:
                subprocess.Popen(["start", "ms-settings:"], shell=True)
                logger.info("Opening Windows Settings via ms-settings:")
                return "Opening Windows Settings."
            except Exception as e:
                logger.error(f"Settings open error: {e}")
                # fall through to generic handling

        # Try known app paths
        matched_app = None
        for app_key in APP_PATHS.keys():
            if app_key in app_name:
                matched_app = app_key
                break

        if matched_app:
            app_exe = None
            for path in APP_PATHS.get(matched_app, []):
                if "{}" in path:
                    path = path.format(os.getenv("USERNAME"))
                if path.startswith("ms-settings:"):
                    try:
                        subprocess.Popen(["start", path], shell=True)
                        logger.info(f"Opening app via protocol: {matched_app} -> {path}")
                        return f"Opening {matched_app}."
                    except Exception as e:
                        logger.error(f"Protocol open error for {matched_app}: {e}")
                        continue
                if os.path.exists(path):
                    app_exe = path
                    break

            if app_exe:
                logger.info(f"Opening app: {matched_app} from {app_exe}")
                subprocess.Popen(app_exe)
                return f"Opening {matched_app}."

            # Known app but not installed: open official site if available
            if matched_app in APP_WEBSITES:
                website = APP_WEBSITES[matched_app]
                logger.info(f"App not found, opening website: {website}")
                webbrowser.open(website)
                return f"{matched_app.title()} is not installed. Opening the website instead."

        # Try Chrome web apps / PWAs in Start Menu
        start_menu_result = _search_start_menu_app(app_name)
        if start_menu_result:
            return start_menu_result

        # Try desktop and common program search using app_control helper
        desktop_result = app_control.open_desktop_app(query)
        if desktop_result and "not found" not in desktop_result.lower() and "failed" not in desktop_result.lower():
            return desktop_result

        program_result = app_control.open_program(query)
        if program_result and not any(term in program_result.lower() for term in ["not found", "failed", "not recognized", "cannot find"]):
            return program_result

        # Check if we have a website URL for this app
        website_url = _find_app_website(app_name)
        if website_url:
            logger.info(f"App not installed, opening website in Chrome: {website_url}")
            # Try to open in Chrome specifically
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
            ]
            chrome_opened = False
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, website_url])
                    chrome_opened = True
                    break
            
            if not chrome_opened:
                # Chrome not found, use default browser
                webbrowser.open(website_url)
            
            return f"{app_name.title()} is not installed. Opening the website in browser."

        # As a last resort, open Google search for the app
        search_url = f"https://www.google.com/search?q={quote(app_name + ' download')}"
        webbrowser.open(search_url)
        logger.info(f"App not recognized; opened Google search for {app_name}")
        return f"I couldn't find {app_name} installed. Opened Google search instead."

    except Exception as e:
        logger.error(f"App opening error: {e}")
        return "Sorry, I couldn't open the app."


def close_app(query: str) -> str:
    """
    Close a running application by name.
    
    Args:
        query: App name
        
    Returns:
        Confirmation message
    """
    try:
        # Extract app name
        close_keywords = ["close", "shut", "exit", "kill", "stop"]
        app_name = query.lower()
        
        for kw in close_keywords:
            if kw in app_name:
                app_name = app_name.replace(kw, "").strip()
                break
        
        if not app_name or len(app_name) < 2:
            return "Please specify which app you want to close."
        
        app_name = app_name.strip()
        
        # Map app names to process names
        app_to_process = {
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "notepad": "notepad.exe",
            "notepad++": "notepad++.exe",
            "settings": "SystemSettings.exe",
            "vscode": "Code.exe",
            "vlc": "vlc.exe",
            "excel": "EXCEL.EXE",
            "word": "WINWORD.EXE",
            "powerpoint": "POWERPNT.EXE",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "task manager": "taskmgr.exe",
        }
        
        # Find matching app
        matched_process = None
        for app_key, process_name in app_to_process.items():
            if app_key in app_name:
                matched_process = process_name
                break
        
        if not matched_process:
            return f"I don't recognize the app '{app_name}'."
        
        # Kill process
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == matched_process.lower():
                    proc.kill()
                    killed = True
                    logger.info(f"Closed process: {matched_process}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            return f"Closed {app_name}."
        else:
            return f"{app_name} is not currently running."
    
    except Exception as e:
        logger.error(f"App closing error: {e}")
        return "Sorry, I couldn't close the app."


def _search_start_menu_app(app_name: str) -> Optional[str]:
    """Search for app in Start Menu (including Chrome PWAs).
    
    Args:
        app_name: Name of app to search for
        
    Returns:
        Success message if found and opened, None otherwise
    """
    try:
        import glob
        username = os.getenv('USERNAME')
        
        # Search locations for Start Menu shortcuts
        search_paths = [
            f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk",
            f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk",
            f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Chrome Apps\\*.lnk",
        ]
        
        for search_path in search_paths:
            shortcuts = glob.glob(search_path, recursive=True)
            for shortcut in shortcuts:
                shortcut_name = os.path.splitext(os.path.basename(shortcut))[0].lower()
                # Match if app_name is in shortcut name or vice versa
                if app_name.lower() in shortcut_name or shortcut_name in app_name.lower():
                    subprocess.Popen(shortcut, shell=True)
                    logger.info(f"Opened Start Menu app: {shortcut}")
                    return f"Opening {shortcut_name.title()}"
        
        return None
    except Exception as e:
        logger.error(f"Start Menu search error: {e}")
        return None


def _find_app_website(app_name: str) -> Optional[str]:
    """Find website URL for an app.
    
    Args:
        app_name: Name of app
        
    Returns:
        Website URL if found, None otherwise
    """
    # Direct match in APP_WEBSITES
    if app_name.lower() in APP_WEBSITES:
        return APP_WEBSITES[app_name.lower()]
    
    # Partial match
    for key, url in APP_WEBSITES.items():
        if key in app_name.lower() or app_name.lower() in key:
            return url
    
    # Try common patterns: app.com or www.app.com
    app_clean = app_name.lower().replace(" ", "")
    potential_urls = [
        f"https://{app_clean}.com",
        f"https://www.{app_clean}.com",
        f"https://app.{app_clean}.com",
    ]
    
    # Return first potential URL (could add validation with requests later)
    return potential_urls[0]


def get_app_list() -> str:
    """Get list of supported apps."""
    return "I can open: " + ", ".join(sorted(APP_PATHS.keys()))


# ============================================================================
# ASYNC VERSIONS FOR CONCURRENT EXECUTION
# ============================================================================

async def async_google_search(query: str) -> str:
    """Async version of google search.
    
    Args:
        query: Search query
        
    Returns:
        Confirmation message
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, google_search, query)


# Async YouTube functions removed - use youtube.py skill for YouTube operations
# The youtube skill can be wrapped with asyncio if needed for concurrent operations


async def async_open_app(query: str) -> str:
    """Async version of open app.
    
    Args:
        query: App name
        
    Returns:
        Confirmation message
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, open_app, query)


async def async_close_app(query: str) -> str:
    """Async version of close app.
    
    Args:
        query: App name
        
    Returns:
        Confirmation message
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, close_app, query)


async def async_generate_document_content(query: str, brain=None) -> str:
    """Async version of document content generation.
    
    Note: Renamed to match generate_document_content()
    
    Args:
        query: Content topic
        brain: Brain instance
        
    Returns:
        Confirmation message
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_document_content, query, brain)


async def execute_multiple_automations(tasks: List[tuple]) -> Dict[str, str]:
    """Execute multiple automation tasks concurrently.
    
    Note: YouTube operations should use youtube.py skill.
    This is for automation tasks: google_search, app control, document generation.
    
    Args:
        tasks: List of (task_name, task_func, query) tuples
               e.g., [("search", async_google_search, "python"),
                      ("open", async_open_app, "chrome")]
    
    Returns:
        Dict of task results
    """
    coroutines = [func(query) for name, func, query in tasks]
    results_list = await asyncio.gather(*coroutines, return_exceptions=True)
    
    results = {}
    for (name, _, _), result in zip(tasks, results_list):
        results[name] = result if not isinstance(result, Exception) else None
    
    return results
