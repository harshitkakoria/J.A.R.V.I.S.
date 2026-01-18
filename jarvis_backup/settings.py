"""
User preferences: wake word, language, voice speed, etc.
"""
from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path
from jarvis.config import DATA_DIR


@dataclass
class UserSettings:
    """User preferences and settings."""
    wake_word: str = "jarvis"
    voice_rate: int = 150  # Words per minute
    voice_volume: float = 0.9  # 0.0 to 1.0
    voice_id: int = 0  # Voice index
    language: str = "en"
    city: str = "Chennai"  # Default city for weather/location-based queries
    name: str = "Harshit"  # User's name
    use_wake_word: bool = False  # Disabled for easier voice interaction
    
    # User Profile - Personalization
    occupation: str = "Software Developer"  # User's occupation
    preferences: dict = field(default_factory=lambda: {
        "news_topics": ["technology", "AI", "business"],
        "interests": ["coding", "automation", "productivity"],
        "daily_routine": {
            "work_start": "09:00",
            "work_end": "18:00",
            "preferred_break_time": "15:00"
        }
    })
    timezone: str = "Asia/Kolkata"  # User's timezone
    relationship: str = "senior"  # User is senior, JARVIS should be formal but not overly so
    
    @classmethod
    def load(cls, settings_file: Optional[Path] = None) -> "UserSettings":
        """
        Load settings from JSON file or return defaults.
        
        Args:
            settings_file: Path to settings file
            
        Returns:
            UserSettings instance
        """
        if settings_file is None:
            settings_file = DATA_DIR / "settings.json"
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception as e:
                print(f"Error loading settings: {e}, using defaults")
        
        return cls()
    
    def save(self, settings_file: Optional[Path] = None) -> None:
        """
        Save settings to JSON file.
        
        Args:
            settings_file: Path to settings file
        """
        if settings_file is None:
            settings_file = DATA_DIR / "settings.json"
        
        settings_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.__dict__, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
