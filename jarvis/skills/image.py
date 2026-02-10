"""Image Generation Skill using Pollinations.ai (Free, No API Key)."""
import os
import time
import requests
from pathlib import Path
from datetime import datetime

def generate_image(prompt: str) -> str:
    """
    Generate an image from text using Pollinations.ai.
    Saves to Downloads/JARVIS/Generated/ and opens it.
    """
    try:
        # 1. Prepare Path
        downloads = Path.home() / "Downloads" / "JARVIS" / "Generated"
        downloads.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(c for c in prompt[:20] if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
        filename = f"img_{timestamp}_{safe_prompt}.jpg"
        filepath = downloads / filename
        
        # 2. Construct URL (Pollinations.ai is prompt-based)
        # URL encoding is handled by requests usually, but direct URL construction needs care.
        # Format: https://image.pollinations.ai/prompt/{prompt}
        # We can pass specific params like width/height if needed, but default is fine.
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        
        print(f"🎨 Generating image for: '{prompt}'...")
        
        # 3. Fetch Image
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 4. Save
        with open(filepath, "wb") as f:
            f.write(response.content)
            
        print(f"💾 Saved to: {filepath}")
        
        # 5. Open Image
        if os.name == 'nt': # Windows
            os.startfile(filepath)
        elif os.name == 'posix': # Mac/Linux
            subprocess.run(['open', filepath]) # Mac
            # Linux usually xdg-open but skipping for now as user is Windows
            
        return f"I have generated the image and saved it to Downloads."
        
    except Exception as e:
        print(f"❌ Image Gen Error: {e}")
        return "Failed to generate image. Please checking internet connection."
