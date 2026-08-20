"""
app.py
SensAI — Multimodal Accessibility AI Studio
Main Streamlit Application — State-of-the-art Glassmorphism Dashboard for all 5 modes
With Synchronized Dark Mode / Light Mode Theme Switching

Run with:
    streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import time
import pandas as pd
from PIL import Image

from core.tts_engine import TTSEngine
from modes.sign_language    import SignLanguageMode
from modes.ocr_tts          import OCRTTSMode
from modes.emotion_detection import EmotionDetectionMode
from modes.scene_description import SceneDescriptionMode
from modes.nova_assistant    import NovaAssistantMode
from utils.ui_styles        import (
    get_custom_css,
    render_hero_header,
    render_metric_card,
    render_result_box,
    render_status_pill,
    render_feature_card
)

# ── 1. Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SensAI — AI Multimodal Accessibility Studio",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Theme (Default to Dark Mode)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Inject Synchronized Design System CSS (Dark Mode / Light Mode)
st.markdown(get_custom_css(theme=st.session_state.theme), unsafe_allow_html=True)


# ── 2. Session State & Cached Engines ─────────────────────────────────────────
@st.cache_resource
def get_tts():
    return TTSEngine()

@st.cache_resource
def get_sign_mode():
    # Cache busted to completely restore original model with tweaked thresholds
    return SignLanguageMode(get_tts())

@st.cache_resource
def get_ocr_mode_v8():
    return OCRTTSMode(get_tts())

@st.cache_resource
def get_emotion_mode():
    return EmotionDetectionMode(get_tts())

@st.cache_resource
def get_scene_mode():
    return SceneDescriptionMode(get_tts())

def get_nova_mode():
    return NovaAssistantMode(get_tts())

def open_camera(index=0):
    return cv2.VideoCapture(index, cv2.CAP_DSHOW)

# Track gesture history for sentence formation in Sign Language mode
if "sl_history" not in st.session_state:
    st.session_state.sl_history = []

# ── 2b. URL Query Parameter Handler (for Seamless HTML Landing Page Navigation) ──
if hasattr(st, "query_params"):
    _qp_mode = st.query_params.get("mode")
    _qp_modal = st.query_params.get("modal")
    if _qp_mode:
        _mode_map = {
            "sign_language": "🤟 Sign Language → Speech",
            "sign": "🤟 Sign Language → Speech",
            "isl": "🤟 Sign Language → Speech",
            "ocr": "📖 Printed Text → Speech (OCR)",
            "tts": "📖 Printed Text → Speech (OCR)",
            "ocr_tts": "📖 Printed Text → Speech (OCR)",
            "emotion": "😊 Facial Emotion → Speech",
            "emotion_detection": "😊 Facial Emotion → Speech",
            "scene": "🌍 Scene Description → Speech",
            "scene_description": "🌍 Scene Description → Speech",
            "nova": "🤖 Nova — AI Accessibility Assistant",
            "nova_ai": "🤖 Nova — AI Accessibility Assistant",
            "home": "🏠 Home (Landing Page)",
            "landing": "🏠 Home (Landing Page)"
        }
        _qp_str = _qp_mode.lower() if isinstance(_qp_mode, str) else str(_qp_mode).lower()
        _target = _mode_map.get(_qp_str)
        if _target:
            st.query_params.clear()
            if st.session_state.get("selected_mode") != _target:
                st.session_state.selected_mode = _target
                st.session_state["mode_selector_radio"] = _target
                st.rerun()
    elif _qp_modal:
        st.query_params.clear()
        from views.landing_page import handle_modal_query
        handle_modal_query(_qp_modal)



# ── 3. Premium Sidebar Dashboard with Theme Switcher ──────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 0.75rem 0; text-align: center;">
        <div style="font-size: 3.2rem; margin-bottom: 4px;">♿</div>
        <h2 style="margin: 0; color: var(--text-primary); font-size: 1.6rem; letter-spacing: -0.02em;">SensAI Studio</h2>
        <span class="badge-gradient" style="margin-top: 6px;">v3.2 PRO • MULTIMODAL</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Dark / Light Theme Mode Switcher
    theme_choice = st.radio(
        "🎨 THEME MODE",
        options=["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True,
        key="theme_mode_selector"
    )
    new_theme = "dark" if "Dark" in theme_choice else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()
    
    st.divider()

    MODES_LIST = [
        "🏠 Home (Landing Page)",
        "🤖 Nova — AI Accessibility Assistant",
        "🤟 Sign Language → Speech",
        "📖 Printed Text → Speech (OCR)",
        "😊 Facial Emotion → Speech",
        "🌍 Scene Description → Speech"
    ]
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "🏠 Home (Landing Page)"

    try:
        current_idx = MODES_LIST.index(st.session_state.selected_mode)
    except ValueError:
        current_idx = 0

    mode = st.radio(
        "⚡ SELECT ASSISTIVE MODE",
        options=MODES_LIST,
        index=current_idx,
        key="mode_selector_radio"
    )
    if mode != st.session_state.selected_mode:
        st.session_state.selected_mode = mode
        st.rerun()

    st.divider()

    # Audio Engine & TTS Control Panel
    with st.expander("🔊 Speech & Voice Studio", expanded=True):
        st.markdown(
            '<div style="margin-bottom: 10px;">'
            '<span class="status-pill"><span class="pulse-dot"></span> AUDIO ENGINE LIVE</span>'
            '</div>',
            unsafe_allow_html=True
        )
        tts_rate = st.slider("Speech Velocity (WPM)", 100, 250, 150, step=10)
        tts_vol  = st.slider("Voice Volume", 0.1, 1.0, 1.0, 0.1)
        
        # Apply settings to cached engine
        tts_engine = get_tts()
        try:
            tts_engine.rate = tts_rate
            tts_engine.volume = tts_vol
        except Exception:
            pass

    st.divider()
    
    # System Status Monitor
    st.markdown("""
    <div style="background: var(--card-inner-bg); border: 1px solid var(--border-glass);
                border-radius: 12px; padding: 12px; font-size: 0.8rem; color: var(--text-secondary); text-align: center;">
        <div style="color: var(--text-primary); font-weight: 600; margin-bottom: 4px;">🖥️ NEURAL PIPELINE</div>
        <div>🟢 PyTorch / Tesseract / BLIP-2</div>
        <div style="color: #10b981; margin-top: 4px;">⚡ Real-time Multi-Threading Active</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("Supports: English + Bengali | Accessibility First")


# ── 4. Main Application Header & Landing Page ─────────────────────────────────
if mode == "🏠 Home (Landing Page)":
    from views.landing_page import render_landing_page
    def _navigate_to_mode(target_mode: str):
        st.session_state.selected_mode = target_mode
        if "mode_selector_radio" in st.session_state:
            st.session_state.mode_selector_radio = target_mode
        st.rerun()
    render_landing_page(on_navigate=_navigate_to_mode)

else:
    if "Nova" not in mode:
        render_hero_header(
            title="SensAI — Accessibility Studio",
            subtitle="Bridging sensory and communication barriers with real-time Multimodal AI",
            badge_text="v3.2 AI MULTIMODAL ENGINE",
            is_live=True
        )

# ─────────────────────────────────────────────────────────────────────────────
# MODE 0 — NOVA AI ACCESSIBILITY ASSISTANT
# ─────────────────────────────────────────────────────────────────────────────
if "Nova" in mode:
    get_nova_mode().render()


# ─────────────────────────────────────────────────────────────────────────────
# MODE 1 — SIGN LANGUAGE TO SPEECH (ISL)
# ─────────────────────────────────────────────────────────────────────────────
elif "Sign Language" in mode:
    st.markdown("### 🤟 Sign Language → Text + Speech")
    st.info("Shows live keypoint overlay and translates ISL gestures to spoken words.")

    mode_obj = get_sign_mode()

    col1, col2 = st.columns([2, 1])
    with col1:
        run       = st.checkbox("Start Camera 📹", key="sl_cam_run_v2")
        print(f"[DEBUG] UI Widget evaluation -> run: {run}, session_state.sl_cam_run_v2: {st.session_state.get('sl_cam_run_v2')}")
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
        print("[DEBUG] 'run' is True! Entering camera block.")
        if "sl_camera" not in st.session_state:
            print("[DEBUG] 'sl_camera' not in session_state. Initializing VideoCapture...")
            with st.spinner("🔄 Initializing camera hardware... Please wait up to 5 seconds."):
                st.session_state.sl_camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                print(f"[DEBUG] VideoCapture initialized. isOpened: {st.session_state.sl_camera.isOpened()}")
        cap = st.session_state.sl_camera
            
        while run:
            print("[DEBUG] Attempting to read frame...")
            ret, frame = cap.read()
            print(f"[DEBUG] Frame read result: ret={ret}")
            if not ret:
                print("[DEBUG] Frame read failed. Displaying error and turning off toggle.")
                st.error("Failed to read from camera. It might be locked by another application.")
                st.session_state.sl_cam_run_v2 = False
                time.sleep(1)
                st.rerun()
            else:
                print("[DEBUG] Processing frame with mode_obj...")
                try:
                    result = mode_obj.process_frame(frame)
                    print("[DEBUG] Frame processed successfully.")
                except Exception as e:
                    print(f"[DEBUG] Exception in process_frame: {e}")
                    raise e

                print("[DEBUG] Updating Streamlit UI placeholders...")
                _, buffer = cv2.imencode('.jpg', result["annotated_frame"])
                frame_ph.image(buffer.tobytes(), use_column_width=True)
                with col2:
                    text_ph.markdown(f'<div class="result-box">{result["text"] or "—"}</div>',
                                      unsafe_allow_html=True)
                    conf_ph.metric("Confidence", f"{result['confidence']:.0%}")
                
                time.sleep(0.01) # Yield
            
    else:
        print("[DEBUG] 'run' is False. Ensuring camera is released.")
        if "sl_camera" in st.session_state:
            print("[DEBUG] Releasing camera...")
            st.session_state.sl_camera.release()
            del st.session_state.sl_camera
            print("[DEBUG] Camera released.")

# ─────────────────────────────────────────────────────────────────────────────
# MODE 2 — PRINTED TEXT TO SPEECH (OCR TTS)
# ─────────────────────────────────────────────────────────────────────────────
elif "Printed Text" in mode:
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.4rem;">📖 Printed Text → Audio Speech (OCR Studio)</h3>
                <p style="margin: 4px 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">
                    Extract and read aloud printed or digital text in English & Bengali using Tesseract OCR.
                </p>
            </div>
            <span class="status-pill">📖 EN + BN MULTILINGUAL OCR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_live = st.tabs(["📁 Image OCR Studio", "📷 Live Camera Reader"])

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload an image containing text (JPG, PNG, JPEG)",
            type=["jpg", "jpeg", "png"],
            key="ocr_uploader"
        )
        if uploaded:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(uploaded.read())
                tmp = f.name
            mode_obj = get_ocr_mode_v8()
            
            col_img, col_ocr = st.columns([6, 6])
            with col_img:
                st.image(uploaded, caption="Uploaded Document Preview", use_column_width=True)
            with col_ocr:
                with st.spinner("🔍 Extracting bilingual text via Neural Tesseract Engine..."):
                    result = mode_obj.process_image_file(tmp)
                    
                rec_text = result["text"] or "No readable text detected in image."
                render_result_box(
                    text=rec_text,
                    title="Extracted Document Text",
                    icon="📄",
                    subtext="Supports English + Bengali character scripts"
                )
                
                if result["text"]:
                    col_btn_1, col_btn_2 = st.columns([1, 1])
                    with col_btn_1:
                        if st.button("🔊 Read Aloud Now", key="ocr_speak_btn"):
                            get_tts().speak(result["text"])
                            st.toast("🔊 Speech synthesis activated!")
                    with col_btn_2:
                        st.download_button(
                            label="📥 Download Text (.txt)",
                            data=result["text"],
                            file_name="extracted_text.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            os.unlink(tmp)
        else:
            st.markdown("""
            <div style="background: var(--card-inner-bg); border: 2px dashed rgba(99, 102, 241, 0.35);
                        border-radius: 16px; padding: 3rem; text-align: center; margin: 1rem 0;">
                <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">📄</div>
                <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Drag and drop or select a photo of a document</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">Supports high-resolution PNG, JPG, JPEG files in English and Bengali</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_live:
        run      = st.toggle("⚡ Activate Live OCR Reader", key="ocr_run")
        ocr_lang = st.radio("Target Text Language:", ["English", "Bengali", "Bilingual (Auto)"], horizontal=True, key="ocr_lang")
        capture  = st.button("📸 Capture Frame & Extract Text")
        
        col_cam, col_ocr = st.columns([7, 5])
        frame_ph = col_cam.empty()
        text_ph  = col_ocr.empty()

        if run:
            if "ocr_camera" not in st.session_state:
                with st.spinner("🔄 Initializing camera hardware... Please wait up to 5 seconds."):
                    st.session_state.ocr_camera = open_camera(0)
            cap = st.session_state.ocr_camera
            
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from camera. It might be locked by another application.")
                    st.session_state.ocr_run = False
                    time.sleep(1)
                    st.rerun()
                else:
                    mode_obj = get_ocr_mode_v8()
                    
                    # Downscale preview to max 640px to prevent UI lag
                    preview = frame.copy()
                    h, w = preview.shape[:2]
                    if max(h, w) > 640:
                        scale = 640 / max(h, w)
                        preview = cv2.resize(preview, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                        
                    annotated = mode_obj._annotate(preview, "")
                    # Use lower JPEG quality for faster websocket streaming
                    _, buffer = cv2.imencode('.jpg', annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                    frame_ph.image(buffer.tobytes(), use_column_width=True)
                    if capture:
                        with text_ph.container():
                            st.info("🔍 Extracting text via Gemini Vision AI... Please wait...")
                        
                        # Process frame
                        result = mode_obj.process_frame(frame, lang_preset=ocr_lang)
                        
                        with text_ph.container():
                            render_result_box(
                                text=result["text"] or "No text recognized.",
                                title="Live Captured Text",
                                icon="📷"
                            )
                        capture = False
                    time.sleep(0.05)
        else:
            if "ocr_camera" in st.session_state:
                st.session_state.ocr_camera.release()
                del st.session_state.ocr_camera
            ph_img = np.zeros((480, 640, 3), dtype=np.uint8)
            ph_img[:] = (15, 20, 38)
            cv2.putText(ph_img, "Live OCR Camera Standby", (160, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (148, 163, 184), 2)
            frame_ph.image(ph_img, channels="BGR", use_column_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 3 — FACIAL EMOTION DETECTION (AUTISM SUPPORT COMPANION)
# ─────────────────────────────────────────────────────────────────────────────
elif "Emotion" in mode:
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.4rem;">😊 Facial Emotion → Spoken Contextual Feedback</h3>
                <p style="margin: 4px 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">
                    Real-time affective computing via DeepFace helping neurodivergent and autism-spectrum users interpret emotions.
                </p>
            </div>
            <span class="status-pill">😊 AFFECTIVE COMPANION AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_cam, col_em = st.columns([7, 5])
    with col_cam:
        run = st.toggle("⚡ Activate Emotion Detection Studio", key="em_run")
        frame_ph = st.empty()
    with col_em:
        st.markdown("#### 😊 Live Mood Dashboard")
        emo_ph   = st.empty()
        st.markdown("#### 📊 Affective Breakdown")
        bars_ph  = st.empty()

    if run:
        if "em_camera" not in st.session_state:
            with st.spinner("🔄 Initializing camera hardware... Please wait up to 5 seconds."):
                st.session_state.em_camera = open_camera(0)
        mode_obj = get_emotion_mode()
        cap = st.session_state.em_camera
        
        while run:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to read from camera. It might be locked by another application.")
                st.session_state.em_run = False
                time.sleep(1)
                st.rerun()
            else:
                # Flip for mirror effect
                frame = cv2.flip(frame, 1)
                
                result = mode_obj.process_frame(frame)
                
                # Downscale preview to max 640px to prevent UI lag
                preview = result["annotated_frame"].copy()
                h, w = preview.shape[:2]
                if max(h, w) > 640:
                    scale = 640 / max(h, w)
                    preview = cv2.resize(preview, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                    
                _, buffer = cv2.imencode('.jpg', preview, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                frame_ph.image(buffer.tobytes(), use_column_width=True)
                
                if result["emotion_data"]:
                    dom  = result["emotion_data"].get("dominant_emotion", "neutral")
                    emos = result["emotion_data"].get("emotions", {})
                    
                    emoji_map = {
                        "happy": "😄", "neutral": "😐", "sad": "😢",
                        "angry": "😠", "surprise": "😲", "fear": "😨", "disgust": "🤢"
                    }
                    curr_emoji = emoji_map.get(dom.lower(), "😊")
                    
                    with emo_ph.container():
                        render_result_box(
                            text=f'<div style="text-align: center; font-size: 1.8rem; font-weight: 800; color: var(--text-primary);">{curr_emoji} {dom.upper()}</div>',
                            title="Dominant Affective State",
                            icon="🎭",
                            subtext="DeepFace Real-Time Facial Analysis"
                        )
                        
                        if emos:
                            sorted_emos = sorted(emos.items(), key=lambda x: x[1], reverse=True)[:5]
                            bars_html = '<div class="glass-card" style="padding: 1rem;">\n'
                            for em_name, em_val in sorted_emos:
                                bar_width = min(100, max(5, int(em_val)))
                                # Remove indentation to prevent Markdown from rendering as a code block
                                bars_html += f"""<div style="margin-bottom: 8px;">
<div style="display:flex; justify-content:space-between; font-size:0.85rem; color: var(--text-primary); margin-bottom:2px;">
<span style="text-transform: capitalize;">{em_name}</span>
<span>{em_val:.1f}%</span>
</div>
<div style="width:100%; background: var(--bar-empty); border-radius:4px; height:8px; overflow:hidden;">
<div style="width:{bar_width}%; background:linear-gradient(90deg, #6366f1, #06b6d4); height:100%; border-radius:4px;"></div>
</div>
</div>\n"""
                            bars_html += '</div>'
                            bars_ph.markdown(bars_html, unsafe_allow_html=True)
                time.sleep(0.05)
    else:
        if "em_camera" in st.session_state:
            st.session_state.em_camera.release()
            del st.session_state.em_camera
        ph_img = np.zeros((480, 640, 3), dtype=np.uint8)
        ph_img[:] = (15, 20, 38)
        cv2.putText(ph_img, "Emotion Companion Studio Standby", (130, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (148, 163, 184), 2)
        frame_ph.image(ph_img, channels="BGR", use_column_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# MODE 4 — SCENE DESCRIPTION TO SPEECH (BLIP-2 VISION AI STUDIO)
# ─────────────────────────────────────────────────────────────────────────────
elif "Scene" in mode:
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h3 style="margin: 0; color: var(--text-primary); font-size: 1.4rem;">🌍 Scene Description → Audio Speech (BLIP-2 Vision Studio)</h3>
                <p style="margin: 4px 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">
                    Generates rich visual scene captions for visually impaired users using state-of-the-art vision-language models.
                </p>
            </div>
            <span class="status-pill">🌍 BLIP-2 VISION TRANSFORMER</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_upload, tab_live = st.tabs(["📁 Image Vision Studio", "📷 Live Scene Explorer"])

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload any visual scene image (JPG, PNG, JPEG)",
            type=["jpg", "jpeg", "png"],
            key="scene_uploader"
        )
        if uploaded:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
                f.write(uploaded.read())
                tmp = f.name
            
            col_img, col_scene = st.columns([6, 6])
            with col_img:
                st.image(tmp, caption="Visual Input Scene", use_column_width=True)
            with col_scene:
                with st.spinner("🤖 Generating rich visual caption with BLIP-2 AI..."):
                    mode_obj = get_scene_mode()
                    caption  = mode_obj.describe_image(tmp)
                
                render_result_box(
                    text=f'<span style="font-size: 1.25rem; color: var(--text-primary); font-weight: 500;">{caption}</span>',
                    title="Generated Scene Description",
                    icon="🌍",
                    subtext="Accessible high-contrast captioning"
                )
                
                col_btn_1, col_btn_2 = st.columns([1, 1])
                with col_btn_1:
                    if st.button("🔊 Speak Scene Aloud", key="scene_speak_btn"):
                        get_tts().speak(caption)
                        st.toast("🔊 Describing scene aloud...")
                with col_btn_2:
                    st.download_button(
                        label="📥 Download Caption (.txt)",
                        data=caption,
                        file_name="scene_description.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            os.unlink(tmp)
        else:
            st.markdown("""
            <div style="background: var(--card-inner-bg); border: 2px dashed rgba(99, 102, 241, 0.35);
                        border-radius: 16px; padding: 3rem; text-align: center; margin: 1rem 0;">
                <div style="font-size: 2.8rem; margin-bottom: 0.5rem;">🌅</div>
                <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">Upload a photo of an indoor or outdoor scene</h4>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">SensAI will analyze objects, lighting, and activities and describe them aloud</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_live:
        run      = st.toggle("⚡ Activate Live Scene Explorer", key="sc_run")
        col_cam, col_sc = st.columns([7, 5])
        frame_ph = col_cam.empty()
        text_ph  = col_sc.empty()

        if run:
            if "sc_camera" not in st.session_state:
                with st.spinner("🔄 Initializing camera hardware... Please wait up to 5 seconds."):
                    st.session_state.sc_camera = open_camera(0)
            mode_obj = get_scene_mode()
            cap = st.session_state.sc_camera
            
            while run:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from camera. It might be locked by another application.")
                    st.session_state.sc_run = False
                    time.sleep(1)
                    st.rerun()
                else:
                    # Flip for mirror effect
                    frame = cv2.flip(frame, 1)
                    
                    result = mode_obj.process_frame(frame)
                    # Downscale preview to max 640px to prevent UI lag
                    preview = result["annotated_frame"].copy()
                    h, w = preview.shape[:2]
                    if max(h, w) > 640:
                        scale = 640 / max(h, w)
                        preview = cv2.resize(preview, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                        
                    _, buffer = cv2.imencode('.jpg', preview, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    frame_ph.image(buffer.tobytes(), use_column_width=True)
                    
                    with text_ph.container():
                        render_result_box(
                            text=result["text"] or "Analyzing visual stream...",
                            title="Real-Time Visual Description",
                            icon="🌍"
                        )
                    time.sleep(0.05)
        else:
            if "sc_camera" in st.session_state:
                st.session_state.sc_camera.release()
                del st.session_state.sc_camera
            ph_img = np.zeros((480, 640, 3), dtype=np.uint8)
            ph_img[:] = (15, 20, 38)
            cv2.putText(ph_img, "Live Scene Explorer Standby", (150, 240),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (148, 163, 184), 2)
            frame_ph.image(ph_img, channels="BGR", use_column_width=True)


# ── 5. Universal Floating/Bottom Help Tray ────────────────────────────────────
if "Nova" not in mode and mode != "🏠 Home (Landing Page)":
    st.divider()
    with st.expander("🤖 Nova Smart Assistant — Guidance & Diagnostic Checklist", expanded=False):
        nova_core = get_nova_mode().nova
        col_tips, col_cta = st.columns([8, 4])
        
        with col_tips:
            st.markdown("#### 💡 Smart Camera & Lighting Checklist:")
            guide_tips = nova_core.get_image_guidance(mode)["tips"]
            for tip in guide_tips:
                st.markdown(f"• **{tip}**")
                
        with col_cta:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 1.25rem;">
                <div style="font-size: 2rem; margin-bottom: 6px;">💡</div>
                <h4 style="margin: 0 0 6px 0; color: var(--text-primary);">Need Troubleshooting?</h4>
                <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">
                    Ask Nova interactive questions or view step-by-step walkthroughs.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.info("💡 **Tip**: Switch to **'🤖 Nova — AI Accessibility Assistant'** from the sidebar for full interactive chat!")









