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

        import re
        # Clean markdown formatting, HTML tags, backticks, asterisks, URLs
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[*#_`~]', '', text)
        text = re.sub(r'https?://\S+', '', text)
        # Convert uppercase English words (2+ chars) to Title Case so TTS engines
        # pronounce them as complete words instead of spelling each letter out!
        text = re.sub(r'\b[A-Z]{2,}\b', lambda m: m.group(0).capitalize(), text)
        text = text.strip()
        if not text:
            return

        detected_lang = lang
        if lang == "auto":
            if any("\u0980" <= c <= "\u09FF" for c in text):
                detected_lang = "bn"
            elif any("\u0900" <= c <= "\u097F" for c in text):
                detected_lang = "hi"
            else:
                detected_lang = "en"

        # If Bengali or Hindi script detected, use gTTS so Indian languages are pronounced accurately!
        if detected_lang in ("bn", "hi"):
            self._speak_gtts(text, detected_lang)
        else:
            # Use Mode 1's offline subprocess technique (pyttsx3) for English text
            self._speak_offline(text)

    def _speak_offline(self, text: str) -> None:
        import subprocess
        import sys
        
        try:
            # Create a tiny, invisible Python script that speaks with Microsoft Zira voice
            script = (
                "import pyttsx3; engine = pyttsx3.init(); "
                "engine.setProperty('rate', 160); "
                "voices = engine.getProperty('voices'); "
                "[engine.setProperty('voice', v.id) for v in voices if 'zira' in v.name.lower() or 'female' in v.name.lower()]; "
                f"engine.say({repr(text)}); engine.runAndWait()"
            )
            
            # Launch it completely detached from your camera app
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
            
            # Cross-platform audio without GUI popups or COM worker thread issues
            if os.name == "nt": # If the system is Windows
                import subprocess
                # Calculate sleep duration dynamically based on text length (~12 chars/sec + buffer)
                sleep_sec = max(10, int(len(text) / 10) + 8)
                path_uri = tmp_path.replace("\\", "/")
                ps_script = (
                    f"Add-Type -AssemblyName presentationCore; "
                    f"$player = New-Object System.Windows.Media.MediaPlayer; "
                    f"$player.Open([System.Uri]'{path_uri}'); "
                    f"Start-Sleep -Milliseconds 500; "
                    f"$player.Play(); "
                    f"Start-Sleep -Seconds {sleep_sec}; "
                    f"$player.Close()"
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    creationflags=0x08000000 # CREATE_NO_WINDOW
                )
            else: # If Mac/Linux
                os.system(f"mpg123 -q {tmp_path} 2>/dev/null || afplay {tmp_path} 2>/dev/null || cvlc --play-and-exit {tmp_path} 2>/dev/null")
            
            try:
                os.unlink(tmp_path)
            except:
                pass
                
        except Exception as e:
            print(f"[gTTS failed, falling back to pyttsx3] {e}")
            self._speak_offline(text) # fallback

    def stop(self) -> None:
        if self.use_offline:
            try:
                self.engine.stop()
            except Exception:
                pass
