"""
modes/ocr_tts.py
Mode 2 — Printed Text → Speech (for visually impaired users)
Pipeline: Image → Preprocessing → Tesseract OCR → Language Detection → TTS
Supports: English + Bengali (Kolkata-specific) + Hindi
"""

import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from langdetect import detect, LangDetectException
from core.base_mode import BaseMode
from core.tts_engine import TTSEngine

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables (e.g. GEMINI_API_KEY)
load_dotenv()


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
        
        # Force load the .env file every time this mode initializes
        # This handles the case where the user creates the .env file without restarting Streamlit
        load_dotenv(override=True)
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # Initialize Gemini Client
        self.client = None
        if api_key:
            print("[OCR] Initializing Gemini Cloud Vision API...")
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[OCR Error] Failed to initialize Gemini Client: {e}")
        else:
            print("[WARNING] GEMINI_API_KEY not found in environment. OCR will fail.")

    def get_mode_name(self) -> str:
        return "Printed Text → Speech"

    def process_frame(self, frame: np.ndarray, lang_preset: str = "default") -> dict:
        """Process a captured image frame and extract + speak text."""
        preprocessed = self._preprocess(frame)
        text         = self._run_ocr(preprocessed, lang_preset)
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
        Preprocessing pipeline optimized for Cloud Vision APIs.
        We only resize to avoid uploading massive images, keeping colors and textures intact.
        """
        # Resize to max 800px width/height to save network upload bandwidth
        h, w = frame.shape[:2]
        max_dim = 800
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return frame

    # ── OCR ──────────────────────────────────────────────────────────────────

    def _run_ocr(self, preprocessed: np.ndarray, lang_preset: str) -> str:
        if not self.client:
            return "Error: GEMINI_API_KEY not set. Please add it to your .env file."
            
        try:
            # Convert OpenCV BGR frame to RGB PIL Image
            rgb_frame = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            
            # Compress to JPEG to drastically speed up network upload
            import io
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=85)
            
            # Pass raw bytes directly to Gemini
            image_data = types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type='image/jpeg')
            
            prompt = (
                "Extract all the text from this image exactly as written. "
                "Preserve the original language (e.g., Bengali, English). "
                "Return ONLY the extracted text and absolutely nothing else. "
                "Do not add any commentary, formatting, or markdown blocks."
            )
            
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[image_data, prompt],
            )
            
            return response.text.strip()
        except Exception as e:
            print(f"[Gemini OCR Error] {e}")
            return f"API Error: {str(e)}"

    def _clean(self, text: str) -> str:
        """Clean excessive whitespace. Cloud Vision models usually output clean text directly."""
        if not text or text.startswith("Error") or text.startswith("API Error"):
            return text
            
        # Remove floating isolated punctuation that might have been hallucinated from noise
        text = re.sub(r'\s+[,.!?"\'-]\s+', ' ', text)
        
        # Remove extra spaces and normalize newlines
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

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

    def process_image_file(self, image_path: str, lang_preset: str = "default") -> dict:
        """Process a static image file (for Streamlit file upload)."""
        frame = cv2.imread(image_path)
        if frame is None:
            return {"text": "", "speak": False, "annotated_frame": None}
        return self.process_frame(frame, lang_preset=lang_preset)
