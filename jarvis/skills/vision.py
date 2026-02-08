"""Vision Skill - Screen and Camera Analysis."""
import cv2
import pyautogui
from PIL import Image
import time
import os
from jarvis.core.llm import LLM

class VisionSkill:
    """Handles visual input (Screen/Webcam) for Gemini."""
    
    def __init__(self):
        self.llm = LLM()
        self.screenshots_dir = "data/screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def handle(self, query: str) -> str:
        """Route vision commands."""
        query = query.lower()
        
        if "screen" in query or "screenshot" in query:
            return self.analyze_screen(query)
        elif "camera" in query or "see" in query or "look at me" in query:
            return self.analyze_webcam(query)
        else:
            return "I'm not sure what you want me to look at (Screen or Camera?)."

    def analyze_screen(self, query: str) -> str:
        """Capture and analyze the screen."""
        try:
            # Capture
            path = os.path.join(self.screenshots_dir, "latest_screen.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            
            # Analyze
            # We pass the PIL Image object directly to Gemini
            response = self.llm.chat_with_image(
                prompt=f"User Query: {query}\nAnalyze this screenshot:",
                image=screenshot
            )
            return response
        except Exception as e:
            return f"Screen analysis failed: {e}"

    def analyze_webcam(self, query: str) -> str:
        """Capture and analyze webcam image."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "I cannot access the webcam."
            
            # Warmup
            time.sleep(1) 
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return "Failed to capture image from camera."
            
            # Convert CV2 (BGR) to PIL (RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Save for debug (optional)
            pil_image.save(os.path.join(self.screenshots_dir, "latest_cam.png"))
            
            # Analyze
            response = self.llm.chat_with_image(
                prompt=f"User Query: {query}\nDescribe what you see in this camera feed:",
                image=pil_image
            )
            return response
            
        except Exception as e:
            return f"Camera analysis failed: {e}"
