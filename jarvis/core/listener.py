"""Listener - Captures voice input via Selenium STT."""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class Listener:
    """Simple STT via Selenium."""
    
    def __init__(self):
        self.driver = None
        self.html_path = None
        self.is_speaking = False
    
    def start(self, html_path: str):
        """Start Chrome with STT HTML."""
        try:
            print("🔧 Starting Chrome...")
            
            options = Options()
            options.add_argument("--use-fake-ui-for-media-stream")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Install and use ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            print("🌐 Loading speech recognition page...")
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get(f"file:///{html_path.replace('\\', '/')}")
            
            print("⏳ Waiting for page to load...")
            time.sleep(2)
            
            # Start recognition
            start_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "start"))
            )
            start_btn.click()
            
            print("✅ Speech recognition ready!\n")
            
        except Exception as e:
            print(f"❌ Error starting listener: {e}")
            print("💡 Try: pip install selenium webdriver-manager")
            raise
    
    def listen(self) -> str:
        """Listen for voice input with quick retries."""
        if not self.driver:
            return ""
        if self.is_speaking:
            return ""
        
        try:
            # Quick retries (total ~2s) to avoid long blocking waits
            # Sleep 0.1s * 20 = 2 seconds
            for _ in range(20):
                try:
                    # v5.0 Optimization: Atomic Read-And-Clear via JS
                    # Avoids find_element overhead and 2 round-trips
                    text = self.driver.execute_script("""
                        var out = document.getElementById('output');
                        if (out) {
                            var txt = out.innerText.trim();
                            if (txt.length > 0) {
                                out.innerHTML = '';
                                return txt;
                            }
                        }
                        return '';
                    """)
                    
                    if text:
                        return text
                        
                except Exception:
                    pass
                    
                time.sleep(0.1)  # Checking 10x per second
            return ""
        except Exception as e:
            print(f"⚠️ Listen error: {e}")
            return ""

    def start_speaking(self):
        """Mark speaking to ignore self audio."""
        self.is_speaking = True
        # Clear any pending text
        try:
            if self.driver:
                self.driver.execute_script("document.getElementById('output').innerHTML = ''")
        except Exception:
            pass

    def stop_speaking(self):
        """Resume listening after speaking."""
        self.is_speaking = False
    
    def stop(self):
        """Stop listener."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def pause(self):
        """Pause listening (clear the input)."""
        if self.driver:
            try:
                self.driver.execute_script("document.getElementById('output').innerHTML = ''")
            except:
                pass
    
    def resume(self):
        """Resume listening."""
        if self.driver:
            try:
                self.driver.execute_script("document.getElementById('output').innerHTML = ''")
            except:
                pass
