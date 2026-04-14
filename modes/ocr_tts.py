"""
modes/ocr_tts.py
Mode 2 — Printed Text → Speech (for visually impaired users)
Pipeline: Image → Preprocessing → Tesseract OCR → Language Detection → TTS
Supports: English + Bengali (Kolkata-specific) + Hindi
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
from langdetect import detect, LangDetectException
from core.base_mode import BaseMode
from core.tts_engine import TTSEngine


class OCRTTSMode(BaseMode):

    # Tesseract language codes for supported scripts
    LANG_MAP = {
        "en": "eng",
        "bn": "ben",   # Bengali
        "hi": "hin",
        "default": "eng+ben"
    }

    def __init__(self, tts: TTSEngine, tesseract_cmd: str = None):
        super().__init__(tts)
        # Set Tesseract path if provided (Windows users typically need this)
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.last_text = ""

    def get_mode_name(self) -> str:
        return "Printed Text → Speech"

    def process_frame(self, frame: np.ndarray) -> dict:
        """Process a captured image frame and extract + speak text."""
        preprocessed = self._preprocess(frame)
        text         = self._run_ocr(preprocessed)
        clean_text   = self._clean(text)
        annotated    = self._annotate(frame.copy(), clean_text)

        if clean_text and clean_text != self.last_text:
            self.last_text = clean_text
            self.maybe_speak(clean_text)

        return {
            "text":            clean_text,
            "speak":           bool(clean_text),
            "annotated_frame": annotated,
            "raw_ocr":         text
        }

    # ── Image Preprocessing ──────────────────────────────────────────────────

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Standard preprocessing pipeline for better OCR accuracy:
        Grayscale → Denoise → Adaptive Threshold → Deskew
        """
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)

        # Adaptive threshold handles uneven lighting (important for phone cameras)
        thresh  = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        deskewed = self._deskew(thresh)
        return deskewed

    def _deskew(self, img: np.ndarray) -> np.ndarray:
        """Correct slight rotation in captured text images."""
        coords = np.column_stack(np.where(img > 0))
        if len(coords) < 10:
            return img
        angle  = cv2.minAreaRect(coords)[-1]
        angle  = -(90 + angle) if angle < -45 else -angle
        if abs(angle) < 0.5:
            return img
        h, w   = img.shape
        M      = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h),
                              flags=cv2.INTER_CUBIC,
                              borderMode=cv2.BORDER_REPLICATE)

    # ── OCR ──────────────────────────────────────────────────────────────────

    def _run_ocr(self, preprocessed: np.ndarray) -> str:
        """Run Tesseract with multilingual config."""
        custom_config = r"--oem 3 --psm 6"
        pil_image     = Image.fromarray(preprocessed)
        try:
            text = pytesseract.image_to_string(
                pil_image,
                lang=self.LANG_MAP["default"],
                config=custom_config
            )
            return text
        except Exception as e:
            print(f"[OCR error] {e}")
            return ""

    def _clean(self, text: str) -> str:
        """Remove noise characters and excessive whitespace."""
        lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 2]
        return " ".join(lines)

    # ── Annotation ───────────────────────────────────────────────────────────

    def _annotate(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Draw OCR result overlay on the frame."""
        overlay_h = 80
        cv2.rectangle(frame, (0, 0), (frame.shape[1], overlay_h), (20, 20, 20), -1)
        if text:
            # Show first 80 chars to avoid overflow
            display = text[:80] + ("..." if len(text) > 80 else "")
            cv2.putText(frame, display, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 230, 100), 2)
            cv2.putText(frame, "OCR — Text detected", (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        else:
            cv2.putText(frame, "Point camera at printed text...", (10, 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)
        return frame

    def process_image_file(self, image_path: str) -> dict:
        """Process a static image file (for Streamlit file upload)."""
        frame = cv2.imread(image_path)
        if frame is None:
            return {"text": "", "speak": False, "annotated_frame": None}
        return self.process_frame(frame)
