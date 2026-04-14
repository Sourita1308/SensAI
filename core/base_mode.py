"""
core/base_mode.py
Abstract base class for all 4 SensAI modes.
Each mode must implement: process_frame() and get_mode_name().
"""

from abc import ABC, abstractmethod
import numpy as np
from core.tts_engine import TTSEngine


class BaseMode(ABC):
    def __init__(self, tts: TTSEngine):
        self.tts = tts
        self.last_spoken = ""        # avoid repeating same phrase
        self.speak_cooldown = 2.0    # seconds between repeated speech
        self._last_speak_time = 0.0

    @abstractmethod
    def get_mode_name(self) -> str:
        """Human-readable name shown in UI."""
        pass

    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Process a single video frame or image.

        Returns a dict with at minimum:
            {
                "text":    str,          # text to display on screen
                "speak":   bool,         # whether to speak the text
                "annotated_frame": np.ndarray   # frame with visualisations drawn on it
            }
        """
        pass

    def maybe_speak(self, text: str) -> None:
        """Speak only if text changed or cooldown passed."""
        import time
        now = time.time()
        if text and (text != self.last_spoken or now - self._last_speak_time > self.speak_cooldown):
            self.last_spoken = text
            self._last_speak_time = now
            self.tts.speak(text)

    def cleanup(self) -> None:
        """Release resources. Override if needed."""
        pass
