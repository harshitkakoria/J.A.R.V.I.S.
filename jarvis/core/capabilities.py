# core/capabilities.py
from typing import Dict

def build_capability_manifest(health: Dict[str, dict]) -> Dict[str, str]:
    """
    Map Health Status to Permission Levels.
    Levels: ENABLED, LIMITED, DISABLED
    """
    
    # helper
    def is_healthy(component):
        return health.get(component, {}).get("state") == "HEALTHY"

    manifest = {
        "voice_input": "ENABLED" if is_healthy("speech") else "DISABLED",
        "voice_output": "ENABLED" if is_healthy("speech") else "DISABLED",
        
        # LLM Reasoning depends on LLM health (which checks internet + key)
        "llm_reasoning": "ENABLED" if is_healthy("llm") else "DISABLED",
        
        # Realtime Search strictly needs Internet
        "realtime_search": "ENABLED" if is_healthy("internet") else "DISABLED",
        
        # Vision depends on vision module
        "vision": "ENABLED" if is_healthy("vision") else "DISABLED",
        
        # Automation works as long as OS is supported
        "automation": "ENABLED" if is_healthy("automation") else "DISABLED",
        
        # File management is local, always enabled unless automation fails
        "file_management": "ENABLED" if is_healthy("automation") else "DISABLED", 
    }
    
    return manifest
