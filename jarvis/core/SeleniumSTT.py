"""
Selenium-based Speech-to-Text using Chrome's Web Speech API.
Updated to follow the provided stable pattern: headless Chrome with fake media,
local STT.html, polling loop, and optional translation.
"""
from selenium import webdriver
from time import sleep, time as now
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from mtranslate import translate as mt_translate
from pathlib import Path
from typing import Optional
from urllib.parse import quote
import os

from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def _to_bcp47(lang: str) -> str:
    if not lang:
        return "en-US"
    if "-" in lang:
        return lang
    mapping = {
        "en": "en-US",
        "hi": "hi-IN",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
    }
    return mapping.get(lang.lower(), f"{lang}-US")


class SeleniumSTT:
    """Speech-to-Text using Selenium + Chrome Web Speech API."""

    def __init__(self, headless: bool = True, language: str = "en", timeout: int = 10, translate: bool = False) -> None:
        self.timeout = timeout
        self.language = _to_bcp47(language)
        self.translate = translate
        self.driver: Optional[webdriver.Chrome] = None
        self._setup_driver(headless=headless)

    def _setup_driver(self, headless: bool) -> None:
        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/89.0.142.86 Safari/537.36"
        )
        opts = Options()
        opts.add_argument(f"user-agent={ua}")
        opts.add_argument("--use-fake-ui-for-media-stream")
        opts.add_argument("--use-fake-device-for-media-stream")
        if headless:
            opts.add_argument("--headless=new")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=opts)
        logger.info("Chrome WebDriver initialized (SeleniumSTT)")

    def _stt_page_url(self) -> str:
        html_path = Path(__file__).resolve().parent / "STT.html"
        lang = quote(self.language)
        return f"file:///{str(html_path).replace(os.sep, '/')}?lang={lang}"

    def listen(self, timeout: Optional[int] = None, phrase_time_limit: int = 5, translate_to: Optional[str] = None) -> Optional[str]:
        timeout = timeout or self.timeout
        if not self.driver:
            self._setup_driver(headless=True)

        try:
            url = self._stt_page_url()
            self.driver.get(url)
            logger.info("Loaded STT page")

            # Start recognition
            self.driver.find_element(By.ID, "start").click()
            logger.info("Listening...")

            end_at = now() + max(timeout, phrase_time_limit + 1)
            last_text = ""
            while now() < end_at:
                try:
                    txt = self.driver.find_element(By.ID, "output").text
                    if txt and txt != last_text:
                        last_text = txt
                        # If we got some text and phrase time has likely passed, stop
                        if len(txt) > 0:
                            self.driver.find_element(By.ID, "end").click()
                            out = txt.strip()
                            if not out:
                                break
                            # Optional translation step
                            if self.translate or translate_to:
                                target = (translate_to or "en-us").lower()
                                try:
                                    out = mt_translate(out, target)
                                except Exception as e:
                                    logger.warning(f"Translation failed: {e}; returning original text")
                            logger.info(f"✓ Recognized: {out}")
                            return out
                    sleep(0.333)
                except Exception:
                    sleep(0.333)

            logger.warning("No speech recognized before timeout")
            return None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
        finally:
            try:
                self.driver.find_element(By.ID, "end").click()
            except Exception:
                pass

    def close(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
            finally:
                self.driver = None
                logger.info("Chrome WebDriver closed")

    def __del__(self):
        self.close()

