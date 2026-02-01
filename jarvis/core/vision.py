"""Vision Manager - See the world."""
import os
import base64
from pathlib import Path
from PIL import ImageGrab
import groq
from dotenv import load_dotenv

load_dotenv()

class VisionManager:
    """Handles screen capture and visual analysis using Groq."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = groq.Groq(api_key=self.api_key)
                print("[+] Vision Manager initialized (Llama 3.2 Vision)")
            except Exception as e:
                print(f"[!] Vision Init Error: {e}")
        else:
            print("[!] GROQ_API_KEY missing. Vision disabled.")
            
        self.temp_dir = Path("data/vision_cache")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def capture(self) -> str:
        """Capture screen and save to temp file."""
        try:
            timestamp = int(os.path.getmtime(__file__)) # just a seed, actually time.time is better
            import time
            timestamp = int(time.time() * 1000)
            
            # Capture
            screenshot = ImageGrab.grab()
            
            # Save
            path = self.temp_dir / f"screen_{timestamp}.png"
            screenshot.save(path, format="PNG")
            
            return str(path)
        except Exception as e:
            print(f"[Capture Error]: {e}")
            return None

    def encode_image(self, image_path: str) -> str:
        """Encode image file to base64."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"[Encode Error]: {e}")
            return None

    def analyze(self, query: str) -> str:
        """Analyze current screen context."""
        if not self.client:
            return "Vision capabilities are not available (Check API Key)."
            
        # 1. Capture
        print("📸 Capturing screen...")
        image_path = self.capture()
        if not image_path:
            return "Failed to capture screen."
            
        # 2. Encode
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return "Failed to process image."
            
        # 3. Ask AI
        try:
            print("🧠 Analyzing image...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query or "Describe what is on my screen."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                # wrappers for different models might change
                # Currently: llama-3.2-90b-vision-preview (Decommissioned? Check Groq docs)
                model="llama-3.2-90b-vision-preview", 
                temperature=0.1,
                max_tokens=250,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"[Vision API Error]: {e}")
            if "model_decommissioned" in str(e):
                return "The Vision Model is currently unavailable (Decommissioned). Please update the Model ID in jarvis/core/vision.py."
            return f"I couldn't analyze the screen: {e}"
