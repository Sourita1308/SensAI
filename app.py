"""
app.py
SensAI — Multimodal Accessibility AI System
Main Streamlit Application — unified dashboard for all 4 modes.

Run with:
    streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from PIL import Image

from core.tts_engine import TTSEngine
from modes.sign_language    import SignLanguageMode
from modes.ocr_tts          import OCRTTSMode
from modes.emotion_detection import EmotionDetectionMode
from modes.scene_description import SceneDescriptionMode

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SensAI — Accessibility Assistant",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 600; margin-bottom: 0; }
    .sub-header  { font-size: 1rem; color: #888; margin-bottom: 1.5rem; }
    .mode-badge  { display: inline-block; padding: 4px 12px; border-radius: 20px;
                   font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem; }
    .result-box  { background: #1a1a2e; border-radius: 12px; padding: 1rem;
                   font-size: 1.1rem; color: #e0e0ff; margin: 1rem 0; min-height: 60px; }
    .metric-card { background: #0f0f23; border-radius: 10px; padding: 0.8rem;
                   text-align: center; }
</style>
""", unsafe_allow_html=True)


# ── Session State & TTS ───────────────────────────────────────────────────────
@st.cache_resource
def get_tts():
    return TTSEngine()

@st.cache_resource
def get_sign_mode():
    return SignLanguageMode(get_tts())

@st.cache_resource
def get_ocr_mode():
    return OCRTTSMode(get_tts())

@st.cache_resource
def get_emotion_mode():
    return EmotionDetectionMode(get_tts())

@st.cache_resource
def get_scene_mode():
    return SceneDescriptionMode(get_tts())


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/accessibility.png", width=60)
    st.title("SensAI")
    st.caption("Multimodal Accessibility Assistant")
    st.divider()

    mode = st.radio(
        "Select Mode",
        options=[
            "🤟 Sign Language → Speech",
            "📖 Printed Text → Speech (OCR)",
            "😊 Facial Emotion → Speech",
            "🌍 Scene Description → Speech"
        ],
        index=0
    )

    st.divider()
    st.caption("Made with ♥ for accessibility")
    st.caption("Supports: English + Bengali")

    # TTS settings
    with st.expander("⚙️ Settings"):
        tts_rate = st.slider("Speech Rate", 100, 250, 150)
        tts_vol  = st.slider("Volume", 0.1, 1.0, 1.0, 0.1)


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">♿ SensAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multimodal AI Accessibility System</div>',
            unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 1 — SIGN LANGUAGE
# ─────────────────────────────────────────────────────────────────────────────
if "Sign Language" in mode:
    st.markdown("### 🤟 Sign Language → Text + Speech")
    st.info("Shows live keypoint overlay and translates ISL gestures to spoken words.")

    col1, col2 = st.columns([2, 1])
    with col1:
        run       = st.toggle("Start Camera", key="sl_run")
        clear_btn = st.button("Clear Sentence")
        frame_ph  = st.empty()
    with col2:
        st.markdown("**Recognised Text**")
        text_ph = st.empty()
        conf_ph = st.empty()

    mode_obj = get_sign_mode()
    if clear_btn:
        mode_obj.clear_sentence()

    if run:
        cap = cv2.VideoCapture(0)
        while st.session_state.get("sl_run", False):
            ret, frame = cap.read()
            if not ret: break
            result = mode_obj.process_frame(frame)
            frame_ph.image(result["annotated_frame"], channels="BGR", use_container_width=True)
            with col2:
                text_ph.markdown(f'<div class="result-box">{result["text"] or "—"}</div>',
                                  unsafe_allow_html=True)
                conf_ph.metric("Confidence", f"{result['confidence']:.0%}")
        cap.release()

# ─────────────────────────────────────────────────────────────────────────────
# MODE 2 — OCR TTS
# ─────────────────────────────────────────────────────────────────────────────
elif "Printed Text" in mode:
    st.markdown("### 📖 Printed Text → Speech")
    st.info("Upload an image of printed text or take a photo. Supports English + Bengali.")

    tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Live Camera"])

    with tab1:
        uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        if uploaded:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(uploaded.read())
                tmp = f.name
            mode_obj = get_ocr_mode()
            col1, col2 = st.columns(2)
            with col1:
                st.image(tmp, caption="Uploaded Image", use_container_width=True)
            with col2:
                with st.spinner("Extracting text..."):
                    result = mode_obj.process_image_file(tmp)
                st.markdown("**Extracted Text**")
                st.markdown(f'<div class="result-box">{result["text"] or "No text found."}</div>',
                             unsafe_allow_html=True)
                if result["text"]:
                    if st.button("🔊 Read Aloud"):
                        get_tts().speak(result["text"])
            os.unlink(tmp)

    with tab2:
        run      = st.toggle("Start Camera", key="ocr_run")
        capture  = st.button("📸 Capture & Read")
        frame_ph = st.empty()
        text_ph  = st.empty()

        if run:
            cap = cv2.VideoCapture(0)
            while st.session_state.get("ocr_run", False):
                ret, frame = cap.read()
                if not ret: break
                mode_obj = get_ocr_mode()
                annotated = mode_obj._annotate(frame.copy(), "")
                frame_ph.image(annotated, channels="BGR", use_container_width=True)
                if capture:
                    result = mode_obj.process_frame(frame)
                    text_ph.markdown(f'<div class="result-box">{result["text"]}</div>',
                                      unsafe_allow_html=True)
                    break
            cap.release()

# ─────────────────────────────────────────────────────────────────────────────
# MODE 3 — EMOTION
# ─────────────────────────────────────────────────────────────────────────────
elif "Emotion" in mode:
    st.markdown("### 😊 Facial Emotion → Spoken Feedback")
    st.info("Detects your facial emotion and speaks contextual feedback. Useful for autism support.")

    col1, col2 = st.columns([2, 1])
    with col1:
        run      = st.toggle("Start Camera", key="em_run")
        frame_ph = st.empty()
    with col2:
        st.markdown("**Detected Emotion**")
        emo_ph   = st.empty()
        chart_ph = st.empty()

    if run:
        mode_obj = get_emotion_mode()
        cap = cv2.VideoCapture(0)
        while st.session_state.get("em_run", False):
            ret, frame = cap.read()
            if not ret: break
            result = mode_obj.process_frame(frame)
            frame_ph.image(result["annotated_frame"], channels="BGR", use_container_width=True)
            if result["emotion_data"]:
                dom   = result["emotion_data"].get("dominant_emotion", "")
                emos  = result["emotion_data"].get("emotions", {})
                emo_ph.markdown(
                    f'<div class="result-box" style="text-align:center;font-size:1.6rem">'
                    f'{dom.upper()}</div>', unsafe_allow_html=True
                )
                if emos:
                    import pandas as pd
                    chart_ph.bar_chart(pd.Series(emos))
        cap.release()

# ─────────────────────────────────────────────────────────────────────────────
# MODE 4 — SCENE DESCRIPTION
# ─────────────────────────────────────────────────────────────────────────────
elif "Scene" in mode:
    st.markdown("### 🌍 Scene Description → Speech")
    st.info("Describes what is visible in any image using BLIP-2 vision language model.")

    tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Live Camera"])

    with tab1:
        uploaded = st.file_uploader("Upload any image", type=["jpg", "jpeg", "png"])
        if uploaded:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(uploaded.read())
                tmp = f.name
            col1, col2 = st.columns(2)
            with col1:
                st.image(tmp, use_container_width=True)
            with col2:
                with st.spinner("Generating scene description..."):
                    mode_obj = get_scene_mode()
                    caption  = mode_obj.describe_image(tmp)
                st.markdown("**Scene Description**")
                st.markdown(f'<div class="result-box">{caption}</div>',
                             unsafe_allow_html=True)
                if st.button("🔊 Read Again"):
                    get_tts().speak(caption)
            os.unlink(tmp)

    with tab2:
        run      = st.toggle("Start Camera", key="sc_run")
        frame_ph = st.empty()
        text_ph  = st.empty()

        if run:
            mode_obj = get_scene_mode()
            cap = cv2.VideoCapture(0)
            while st.session_state.get("sc_run", False):
                ret, frame = cap.read()
                if not ret: break
                result = mode_obj.process_frame(frame)
                frame_ph.image(result["annotated_frame"], channels="BGR", use_container_width=True)
                text_ph.markdown(
                    f'<div class="result-box">{result["text"] or "Analysing scene..."}</div>',
                    unsafe_allow_html=True
                )
            cap.release()
