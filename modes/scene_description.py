"""
modes/scene_description.py
Mode 4 — Scene Description → Speech (for visually impaired users)
Pipeline: Image → BLIP-2 Caption → Natural Language → TTS
Uses Salesforce BLIP-2 via HuggingFace Transformers (runs locally).
Falls back to BLIP-base if GPU unavailable.
"""

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from core.base_mode import BaseMode
from core.tts_engine import TTSEngine


class SceneDescriptionMode(BaseMode):
    # Use lighter BLIP-base for CPU, BLIP-2 for GPU
    BLIP_MODEL_CPU = "Salesforce/blip-image-captioning-base"
    BLIP_MODEL_GPU = "Salesforce/blip-image-captioning-large"

    FRAME_SKIP = 30   # describe scene every 30 frames (~1s at 30fps)

    def __init__(self, tts: TTSEngine):
        super().__init__(tts)
        self.device      = "cuda" if torch.cuda.is_available() else "cpu"
        model_id         = self.BLIP_MODEL_GPU if self.device == "cuda" else self.BLIP_MODEL_CPU
        self.speak_cooldown = 6.0

        print(f"[SceneMode] Loading {model_id} on {self.device}...")
        self.processor = BlipProcessor.from_pretrained(model_id)
        self.model     = BlipForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)
        self.model.eval()

        self.frame_count   = 0
        self.last_caption  = ""

    def get_mode_name(self) -> str:
        return "Scene Description → Speech"

    def process_frame(self, frame: np.ndarray) -> dict:
        self.frame_count += 1
        annotated = frame.copy()

        if self.frame_count % self.FRAME_SKIP == 0:
            caption = self._caption(frame)
            if caption:
                self.last_caption = caption
                natural = self._naturalise(caption)
                self.maybe_speak(natural)

        annotated = self._annotate(annotated, self.last_caption)

        return {
            "text":            self.last_caption,
            "speak":           bool(self.last_caption),
            "annotated_frame": annotated
        }

    def describe_image(self, image_path: str) -> str:
        """One-shot description of an uploaded image file."""
        frame = cv2.imread(image_path)
        if frame is None:
            return ""
        caption = self._caption(frame)
        natural = self._naturalise(caption)
        self.tts.speak(natural)
        return natural

    # ── BLIP Inference ───────────────────────────────────────────────────────

    def _caption(self, frame: np.ndarray) -> str:
        try:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            inputs    = self.processor(pil_image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=60,
                    num_beams=4,
                    early_stopping=True
                )
            caption = self.processor.decode(output[0], skip_special_tokens=True)
            return caption.strip()
        except Exception as e:
            print(f"[Scene error] {e}")
            return ""

    def _naturalise(self, caption: str) -> str:
        """Make the caption sound more natural when spoken."""
        if not caption:
            return ""
        # Capitalise and add context prefix
        caption = caption[0].upper() + caption[1:]
        return f"I can see: {caption}."

    # ── Annotation ───────────────────────────────────────────────────────────

    def _annotate(self, frame: np.ndarray, caption: str) -> np.ndarray:
        h = frame.shape[0]
        cv2.rectangle(frame, (0, h - 60), (frame.shape[1], h), (20, 20, 20), -1)
        text = caption if caption else "Analysing scene..."
        # Word-wrap at ~70 chars
        words, line, lines = text.split(), "", []
        for w in words:
            if len(line) + len(w) + 1 > 70:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        if line:
            lines.append(line)
        for i, l in enumerate(lines[:2]):
            cv2.putText(frame, l, (10, h - 35 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 230, 255), 1)
        return frame
