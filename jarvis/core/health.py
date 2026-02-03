# core/health.py
import time
import os
import subprocess
import requests
from typing import Dict

class HealthManager:
    """
    Real-time system health checks.
    Detects if components (Internet, LLM, Vision, etc.) are usable.
    """
    
    def __init__(self):
        self.last_check = 0
        self.cache_ttl = 60  # Cache health check for 60 seconds
        self.status = {}
        # Initial check on startup
        self.check_all()

    def check_all(self) -> Dict[str, dict]:
        """Public entry point to get full system health."""
        now = time.time()
        # Return cached status if within TTL
        if self.status and (now - self.last_check < self.cache_ttl):
            return self.status

        print("[-] Running System Health Check...")
        self.status = {
            "internet": self._check_internet(),
            "llm": self._check_llm(),
            "speech": self._check_speech(),
            "vision": self._check_vision(),
            "automation": self._check_automation()
        }

        self.last_check = now
        return self.status

    def _check_internet(self):
        """Ping a reliable host (Google DNS) to verify connectivity."""
        try:
            # Using requests is simpler than parsing ping output across OS
            requests.get("https://8.8.8.8", timeout=2)
            return {"state": "HEALTHY"}
        except:
            return {"state": "UNAVAILABLE", "error": "No internet connection"}

    def _check_llm(self):
        """Check if Groq API Key is present and Internet is reachable."""
        # 1. Check Key
        key = os.getenv("GROQ_API_KEY")
        if not key:
            return {"state": "UNAVAILABLE", "error": "Missing GROQ_API_KEY"}
            
        # 2. Check Internet (Dependency)
        # Verify internet check result (optimistic here or re-check? re-check safer)
        if self._check_internet()["state"] != "HEALTHY":
             return {"state": "UNAVAILABLE", "error": "No Internet for API"}
             
        # 3. Import check
        try:
            import groq
            return {"state": "HEALTHY"}
        except ImportError:
            return {"state": "UNAVAILABLE", "error": "Groq module missing"}

    def _check_speech(self):
        """Check STT/TTS modules."""
        status = "HEALTHY"
        errs = []
        try:
            from jarvis.core.listener import Listener
        except:
            status = "DEGRADED"
            errs.append("Listener missing")
            
        try:
            from jarvis.core.speech import Speaker
        except:
             status = "DEGRADED" if status == "HEALTHY" else "UNAVAILABLE"
             errs.append("Speaker missing")
             
        if errs:
            return {"state": status, "error": ", ".join(errs)}
        return {"state": "HEALTHY"}

    def _check_vision(self):
        """Check Vision capabilities."""
        try:
            from jarvis.core.vision import VisionManager
            # We assume VisionManager works if imported, or we could check dependencies
            return {"state": "HEALTHY"}
        except ImportError:
            return {"state": "UNAVAILABLE", "error": "Vision module missing"}
        except Exception as e:
            return {"state": "UNAVAILABLE", "error": str(e)}

    def _check_automation(self):
        """Check OS Automation capabilities."""
        if os.name in ["nt", "posix"]:
            return {"state": "HEALTHY"}
        return {"state": "DEGRADED", "error": "Unsupported OS"}
