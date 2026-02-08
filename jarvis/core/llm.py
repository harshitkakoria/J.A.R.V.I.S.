"""Unified LLM Interface using Groq (Llama 3.1/3.2)."""
import os
import json
import base64
import io
from groq import Groq
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()

class LLM:
    """Wrapper for Groq API (Llama 3.1 for Text, Llama 3.2 for Vision)."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            console.print("[red]GROQ_API_KEY not found in .env[/red]")
            self.client = None
            return

        try:
            self.client = Groq(api_key=self.api_key)
            self.text_model = "llama-3.1-8b-instant"
            # Vision models are currently decommissioned/unavailable on Groq.
            self.vision_model = None 
            console.print(f"[green]Groq Initialized (Text: {self.text_model}, Vision: Disabled)[/green]")
        except Exception as e:
            console.print(f"[red]Failed to init Groq: {e}[/red]")
            self.client = None

    def chat(self, prompt: str, system_instruction: str = None, json_mode: bool = False, history: list = None) -> str:
        """
        Send a message to Groq (Llama 3.1).
        """
        if not self.client:
            return ""

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        # Add history if provided (not fully implemented in args yet, but structure is here)
        if history:
             messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=messages,
                temperature=0.1 if json_mode else 0.7,
                response_format={"type": "json_object"} if json_mode else None
            )
            
            return response.choices[0].message.content.strip()

        except Exception as e:
            console.print(f"[red]LLM Error: {e}[/red]")
            return ""

    def chat_with_image(self, prompt: str, image) -> str:
        """
        Send an image and prompt to Groq (Llama 3.2 Vision).
        args:
            prompt: Question about the image
            image: PIL Image object
        """
        if not self.client or not self.vision_model:
            return "Vision capabilities are currently unavailable on Groq (Models decommissioned/missing). Please switch to Gemini for Vision or wait for Groq updates."

        try:
            # Convert PIL Image to Base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_url = f"data:image/png;base64,{img_str}"

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": img_url
                            }
                        }
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            console.print(f"[red]Vision Error: {e}[/red]")
            return f"I couldn't analyze the image. Error: {e}"
