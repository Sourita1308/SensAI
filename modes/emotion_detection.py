"""
modes/emotion_detection.py
Mode 3 — Facial Emotion → Spoken Feedback (for autism / therapy support)
Pipeline: Webcam Frame → DeepFace → Emotion Label → Contextual Message → TTS
"""

import cv2
import numpy as np
from deepface import DeepFace
from core.base_mode import BaseMode
from core.tts_engine import TTSEngine


# Contextual messages per emotion — more human than just saying "You look angry"
EMOTION_MESSAGES = {
    "happy":     "You look happy! That's wonderful.",
    "sad":       "You seem to be feeling sad.",
    "angry":     "You might be feeling frustrated.",
    "fear":      "You appear anxious or fearful.",
    "surprise":  "You look surprised!",
    "disgust":   "You seem uncomfortable.",
    "neutral":   "Your expression looks calm."
}

EMOTION_COLORS = {
    "happy":   (0, 220, 110),
    "sad":     (200, 100, 50),
    "angry":   (0, 50, 220),
    "fear":    (200, 50, 200),
    "surprise":(0, 200, 220),
    "disgust": (50, 180, 50),
    "neutral": (180, 180, 180)
}


class EmotionDetectionMode(BaseMode):
    FRAME_SKIP   = 5     # run DeepFace every N frames (it's slow)
    CONF_THRESH  = 0.55  # minimum dominant emotion confidence

    def __init__(self, tts: TTSEngine):
        super().__init__(tts)
        self.frame_count     = 0
        self.last_result     = {}
        self.speak_cooldown  = 7.0   # 7-second cooldown between emotion announcements — calm & unhurried

    def get_mode_name(self) -> str:
        return "Facial Emotion → Speech"

    def process_frame(self, frame: np.ndarray) -> dict:
        self.frame_count += 1
        annotated = frame.copy()

        # Only run inference every N frames for performance
        if self.frame_count % self.FRAME_SKIP == 0:
            self.last_result = self._analyse(frame)

        if self.last_result:
            annotated = self._draw(annotated, self.last_result)
            dominant  = self.last_result.get("dominant_emotion", "")
            if dominant:
                message = EMOTION_MESSAGES.get(dominant, f"You seem {dominant}.")
                self.maybe_speak(message)

        return {
            "text":            self.last_result.get("dominant_emotion", ""),
            "emotion_data":    self.last_result,
            "speak":           bool(self.last_result),
            "annotated_frame": annotated
        }

    # ── DeepFace Analysis ────────────────────────────────────────────────────

    def _analyse(self, frame: np.ndarray) -> dict:
        try:
            results = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False,
                silent=True
            )
            if not results:
                return {}
            r = results[0]
            emotions = r.get("emotion", {})
            dominant = r.get("dominant_emotion", "")
            region   = r.get("region", {})
            conf     = emotions.get(dominant, 0) / 100
            if conf < self.CONF_THRESH:
                return {}
            return {
                "dominant_emotion": dominant,
                "emotions":         emotions,
                "region":           region,
                "confidence":       conf
            }
        except Exception as e:
            print(f"[Emotion error] {e}")
            return {}

    # ── Annotation ───────────────────────────────────────────────────────────

    def _draw(self, frame: np.ndarray, result: dict) -> np.ndarray:
        region   = result.get("region", {})
        dominant = result.get("dominant_emotion", "")
        emotions = result.get("emotions", {})
        color    = EMOTION_COLORS.get(dominant, (200, 200, 200))

        # Face bounding box
        if region:
            x, y, w, h = region.get("x", 0), region.get("y", 0), \
                         region.get("w", 0), region.get("h", 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, dominant.upper(),
                        (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Emotion bar chart (top right)
        bar_x, bar_y = frame.shape[1] - 200, 20
        for i, (emo, score) in enumerate(sorted(emotions.items(), key=lambda e: -e[1])):
            bar_len = int(score * 1.6)   # scale 0-100 to 0-160px
            c       = EMOTION_COLORS.get(emo, (200, 200, 200))
            y_pos   = bar_y + i * 22
            cv2.rectangle(frame, (bar_x, y_pos), (bar_x + bar_len, y_pos + 14), c, -1)
            cv2.putText(frame, f"{emo[:5]} {score:.0f}%",
                        (bar_x - 80, y_pos + 11),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1)

        return frame
