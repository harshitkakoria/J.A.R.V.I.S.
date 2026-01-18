import os
import asyncio
import random
import threading
from typing import List, Optional

import pygame
import edge_tts
from dotenv import dotenv_values
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class TextToSpeech:
    """Edge TTS-based voice for JARVIS with pygame playback.

    Uses Microsoft Edge Text-to-Speech (edge_tts) to synthesize high-quality speech
    and pygame.mixer to play the generated audio. Uses male voices only.
    Configuration can be provided via .env using keys:

    - TTS_VOICE: single voice (e.g., "en-US-GuyNeural")
    - TTS_RATE: rate string like "+0%", "+10%", "-10%"
    - TTS_VOLUME: volume string like "+0%", "+50%"
    - TTS_PITCH: pitch string like "+0Hz", "+2Hz", "-2Hz"
    - TTS_RANDOMIZE: "true" to slightly vary rate/pitch per utterance
    - TTS_TMP_DIR: output cache folder (default: data/tts_cache)
    """

    # Male voices only
    MALE_VOICES = [
        "en-US-GuyNeural",        # Clear male voice (primary)
        "en-GB-RyanNeural",       # British male
        "en-CA-LaimNeural",       # Canadian male
    ]

    DEFAULT_VOICES = MALE_VOICES

    def __init__(
        self,
        voice: Optional[str] = None,
        voices: Optional[List[str]] = None,
        rate: Optional[str] = None,
        volume: Optional[str] = None,
        pitch: Optional[str] = None,
        tmp_dir: Optional[str] = None,
    ) -> None:
        cfg = dotenv_values() or {}

        # Voice selection - male voices only
        env_voices = self._parse_voice_list(cfg.get("TTS_VOICES"))
        self.voices: List[str] = voices or env_voices or self.MALE_VOICES
        self.voice: Optional[str] = voice or cfg.get("TTS_VOICE")

        # Synthesis params
        self.rate = rate or cfg.get("TTS_RATE") or "+0%"
        self.volume = volume or cfg.get("TTS_VOLUME") or "+0%"
        self.pitch = pitch or cfg.get("TTS_PITCH") or "+0Hz"
        self.randomize = str(cfg.get("TTS_RANDOMIZE", "false")).lower() in {"1", "true", "yes"}

        # Temp/cache directory for audio files
        self.tmp_dir = tmp_dir or cfg.get("TTS_TMP_DIR") or os.path.join("data", "tts_cache")
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Init pygame mixer lazily to avoid device conflicts at import time
        self._mixer_initialized = False
        self._play_lock = threading.Lock()

        logger.info("TextToSpeech initialized (male voice)")

    def _parse_voice_list(self, value: Optional[str]) -> List[str]:
        if not value:
            return []
        parts = [v.strip() for v in value.split(",")]
        return [p for p in parts if p]

    def _choose_voice(self) -> str:
        """Choose voice, preferring configured voice or primary male voice."""
        if self.voice and self.voice.strip():
            return self.voice.strip()
        # Always prefer the primary voice (en-US-GuyNeural) instead of random selection
        return self.voices[0] if self.voices else self.DEFAULT_VOICES[0]

    def _maybe_randomize_params(self) -> tuple[str, str, str]:
        if not self.randomize:
            return self.rate, self.volume, self.pitch
        # Small natural variation
        rate_delta = random.randint(-5, 5)
        pitch_delta = random.randint(-2, 2)
        return f"{rate_delta:+d}%", self.volume, f"{pitch_delta:+d}Hz"

    def _ensure_mixer(self) -> None:
        if self._mixer_initialized:
            return
        try:
            pygame.mixer.init()
            self._mixer_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}")
            raise

    async def _synthesize_to_file(self, text: str, out_path: str, voice: str, rate: str, volume: str, pitch: str) -> None:
        import asyncio
        max_retries = 3
        retry_count = 0
        primary_voice = "en-US-GuyNeural"  # Primary reliable voice
        
        while retry_count < max_retries:
            try:
                comm = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume, pitch=pitch)
                await asyncio.wait_for(comm.save(out_path), timeout=30.0)
                
                # Verify file was created and has content
                if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
                    raise Exception(f"Audio file not created or empty: {out_path}")
                
                logger.debug(f"TTS synthesis successful: {len(text)} chars")
                return
                    
            except asyncio.TimeoutError:
                logger.warning(f"TTS synthesis timeout (attempt {retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count < max_retries:
                    # Switch to primary voice immediately on timeout
                    if voice != primary_voice:
                        logger.info(f"Switching to primary voice: {primary_voice}")
                        voice = primary_voice
                        rate, volume, pitch = "+0%", "+0%", "+0Hz"
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                raise Exception("TTS synthesis timed out after retries")
                
            except Exception as e:
                logger.warning(f"TTS synthesis failed with {voice} (attempt {retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                
                # Switch to primary voice immediately on any failure
                if voice != primary_voice and retry_count < max_retries:
                    logger.info(f"Switching to primary voice: {primary_voice}")
                    voice = primary_voice
                    rate, volume, pitch = "+0%", "+0%", "+0Hz"
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                
                if retry_count >= max_retries:
                    raise Exception(f"TTS synthesis failed after {max_retries} attempts: {str(e)}")
                raise

    def _run_async(self, coro) -> None:
        try:
            asyncio.run(coro)
        except RuntimeError:
            # If an event loop is already running (e.g., in certain environments),
            # run the coroutine in a dedicated thread with its own loop.
            def _runner():
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(coro)
                finally:
                    loop.close()

            t = threading.Thread(target=_runner, daemon=True)
            t.start()
            t.join()

    def _play_file_blocking(self, path: str) -> None:
        self._ensure_mixer()
        with self._play_lock:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.delay(50)
                pygame.mixer.music.unload()
            finally:
                try:
                    os.remove(path)
                except Exception:
                    pass

    def speak(self, text: str, threaded: bool = False) -> Optional[threading.Thread]:
        """Synthesize and play speech.

        Args:
            text: Text content to speak
            threaded: If True, run playback non-blocking in a background thread

        Returns:
            Thread object if threaded=True, else None
        """
        if not text:
            return None

        try:
            voice = self._choose_voice()
            rate, volume, pitch = self._maybe_randomize_params()
            out_file = os.path.join(self.tmp_dir, f"tts_{abs(hash((text, voice, rate, volume, pitch)))}.mp3")

            logger.info(f"Synthesizing with {voice}")
            self._run_async(self._synthesize_to_file(text, out_file, voice, rate, volume, pitch))

            if threaded:
                th = threading.Thread(target=self._play_file_blocking, args=(out_file,), daemon=True)
                th.start()
                return th
            else:
                self._play_file_blocking(out_file)
                return None
                
        except Exception as e:
            logger.error(f"TTS speak error: {e}")
            # Fallback to console output
            print(f"JARVIS: {text}")
            return None

    def stop(self) -> None:
        """Stop current playback, if any."""
        if not self._mixer_initialized:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
