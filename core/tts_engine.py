"""
core/tts_engine.py
Shared Text-to-Speech engine used by all 4 modes.
Tries offline pyttsx3 first, falls back to gTTS (online).
"""

import pyttsx3
import threading
import tempfile
import os
from gtts import gTTS
from langdetect import detect


class TTSEngine:
    def __init__(self, rate: int = 150, volume: float = 1.0, use_offline: bool = True):
        self.use_offline = use_offline
        self._lock = threading.Lock()

        if use_offline:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", rate)
                self.engine.setProperty("volume", volume)
                voices = self.engine.getProperty("voices")
                # prefer a female voice if available
                for v in voices:
                    if "female" in v.name.lower() or "zira" in v.name.lower():
                        self.engine.setProperty("voice", v.id)
                        break
            except Exception:
                self.use_offline = False

    def speak(self, text: str, lang: str = "auto") -> None:
        """Speak text. Detects language automatically if lang='auto'."""
        if not text or not text.strip():
            return

        detected_lang = lang
        if lang == "auto":
            try:
                # FIX 1: langdetect gets confused by single gestures. 
                # Force English for short phrases to use the offline voice!
                if len(text.split()) <= 2:
                    detected_lang = "en"
                else:
                    detected_lang = detect(text)
            except Exception:
                detected_lang = "en"

        # Use offline engine for English
        if self.use_offline and detected_lang in ("en", "unknown"):
            self._speak_offline(text)
        else:
            # gTTS handles multilingual (Bengali, Hindi, etc.)
            self._speak_gtts(text, detected_lang)

    def _speak_offline(self, text: str) -> None:
        import subprocess
        import sys
        
        try:
            # Create a tiny, invisible Python script that only speaks the word
            script = f'import pyttsx3; engine = pyttsx3.init(); engine.setProperty("rate", 160); engine.say("{text}"); engine.runAndWait()'
            
            # Launch it completely completely detached from your camera app
            subprocess.Popen([sys.executable, "-c", script])
            
        except Exception as e:
            print(f"[TTS process error] {e}")
    def _speak_gtts(self, text: str, lang: str = "en") -> None:
        try:
            # Map langdetect codes to gTTS codes
            lang_map = {"bn": "bn", "hi": "hi", "en": "en", "fr": "fr"}
            gtts_lang = lang_map.get(lang, "en")
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_path = f.name
            tts.save(tmp_path)
            
            # FIX 2: Cross-platform audio so Windows doesn't crash
            if os.name == "nt": # If the system is Windows
                os.system(f"start /min {tmp_path}")
            else: # If Mac/Linux
                os.system(f"mpg123 -q {tmp_path} 2>/dev/null || afplay {tmp_path} 2>/dev/null || cvlc --play-and-exit {tmp_path} 2>/dev/null")
            
            # Note: os.unlink(tmp_path) might throw a permission error on Windows 
            # if the file is still playing, so we put it in a try block.
            try:
                os.unlink(tmp_path)
            except:
                pass
                
        except Exception as e:
            print(f"[TTS gTTS error] {e}")

    def stop(self) -> None:
        if self.use_offline:
            try:
                self.engine.stop()
            except Exception:
                pass
