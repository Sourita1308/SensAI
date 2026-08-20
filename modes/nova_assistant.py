"""
modes/nova_assistant.py
SensAI — Multimodal Accessibility AI System
Nova AI Accessibility Assistant — Interactive Glassmorphic Studio providing:
1. Context-Aware Chat with Intelligent Mode Recommendation & Smart Suggestions
2. Interactive Tutorials (Numbered walkthroughs in sleek cards)
3. Smart Image Guidance (Pre-upload camera checklists)
4. Upload Validation Assistant & Troubleshooting Diagnostics
5. AI Feature Explainer (Beginner vs. Technical Deep-Dive)
6. Frequently Asked Questions (FAQ) & Keyboard Navigation Accessibility Guide
"""

import streamlit as st
import time
from typing import Dict, Any, List
from core.nova_ai import NovaAI
from utils.ui_styles import (
    render_hero_header,
    render_result_box,
    render_status_pill,
    render_feature_card
)


class NovaAssistantMode:
    """
    Interactive Studio UI for Nova, SensAI's dedicated Accessibility Assistant.
    """

    def __init__(self, tts=None):
        self.tts = tts
        self.nova = NovaAI(tts=tts)

    def get_mode_name(self) -> str:
        return "🤖 Nova — AI Accessibility Assistant"

    def render(self) -> None:
        """
        Render the complete Nova Accessibility Assistant studio dashboard in Streamlit.
        Calls the original interactive Streamlit UI with all backend logic intact.
        """
        self.render_legacy_studio()

    def render_legacy_studio(self) -> None:
        """
        Original Streamlit tabs interface for Nova Assistant with full backend logic.
        """
        # 1. Glassmorphic Hero Card
        st.markdown("""
        <div class="glass-card" style="padding: 1.8rem 2rem; border-left: 4px solid #6366f1; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 1.25rem;">
                    <span style="font-size: 3.2rem; background: rgba(99,102,241,0.15); padding: 12px; border-radius: 16px;
                                 border: 1px solid rgba(99,102,241,0.3);">🤖</span>
                    <div>
                        <div style="margin-bottom: 6px;">
                            <span class="badge-gradient">✨ NOVA NEURAL ACCESSIBILITY ENGINE</span>
                        </div>
                        <h2 style="margin: 0; color: var(--text-primary); font-weight: 700; font-size: 1.8rem;">
                            Nova — AI Accessibility Guide
                        </h2>
                        <p style="margin: 6px 0 0 0; color: var(--text-secondary); font-size: 1.05rem;">
                            Your intelligent companion for SensAI. Ask questions in simple language, get interactive tutorials,
                            diagnose camera/upload issues, and understand AI models.
                        </p>
                    </div>
                </div>
                <span class="status-pill"><span class="pulse-dot"></span> CONTEXT-AWARE AI LIVE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Initialize session state for Nova chat & context
        if "nova_history" not in st.session_state:
            st.session_state.nova_history = [
                {
                    "role": "assistant",
                    "content": self.nova.get_greeting(),
                    "recommended_mode": None,
                    "suggestion": "Ask me anything or try clicking a quick-action button below!"
                }
            ]
        if "nova_context" not in st.session_state:
            st.session_state.nova_context = {}

        # 2. Quick Action Chips / Intent Shortcuts
        st.markdown("#### ⚡ Instant Accessibility Actions & Recommended Questions")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button(
                "🤟 'I want to understand this sign'",
                key="instant_action_sign",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("I want to understand this sign.",)
            )
            st.button(
                "📖 'I have a picture with Bengali text'",
                key="instant_action_ocr",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("I have a picture containing Bengali text.",)
            )
        with col2:
            st.button(
                "😊 'I want to know how this person feels'",
                key="instant_action_emo",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("I want to know how this person feels.",)
            )
            st.button(
                "🌍 'I am blind, please describe this image'",
                key="instant_action_scene",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("I'm visually impaired. Please describe this image.",)
            )
        with col3:
            st.button(
                "🔧 'Why is my prediction incorrect?'",
                key="instant_action_error",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("Why is my prediction incorrect?",)
            )
            st.button(
                "🧠 'How do the AI models work?'",
                key="instant_action_ai",
                use_container_width=True,
                on_click=self._send_quick_message,
                args=("Explain how the AI models work in simple words.",)
            )

        st.divider()

        # 3. 6 Main Feature Studio Tabs
        tab_chat, tab_tut, tab_guide, tab_diag, tab_ai, tab_faq = st.tabs([
            "💬 Chat Studio",
            "📖 Interactive Walkthroughs",
            "📷 Camera Guidance",
            "🔧 Upload Troubleshooting",
            "🧠 AI Feature Studio",
            "❓ FAQ & Accessibility"
        ])

        # ── TAB 1: CONTEXT-AWARE CHAT WITH NOVA ─────────────────────────────────
        with tab_chat:
            col_title, col_clr = st.columns([5, 1])
            with col_title:
                st.markdown("#### 💬 Natural & Context-Aware AI Companion")
                st.caption("Ask Nova anything in simple words. Nova remembers conversation context and suggests next steps.")
            with col_clr:
                if st.button("🗑️ Clear Chat", key="clear_nova_chat_btn", use_container_width=True):
                    st.session_state.nova_history = [
                        {
                            "role": "assistant",
                            "content": self.nova.get_greeting(),
                            "recommended_mode": None,
                            "suggestion": "Ask me anything or try clicking a quick-action button below!"
                        }
                    ]
                    st.rerun()

            # Display conversation history
            chat_container = st.container()
            with chat_container:
                for idx, msg in enumerate(st.session_state.nova_history):
                    if msg["role"] == "user":
                        with st.chat_message("user", avatar="👤"):
                            st.write(msg["content"])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(
                                f'<div style="font-size: 1.05rem; line-height: 1.6; color: var(--text-primary);">{msg["content"]}</div>',
                                unsafe_allow_html=True
                            )

                            # Show mode recommendation badge if present
                            if msg.get("recommended_mode"):
                                st.markdown(f"""
                                <div class="glass-card" style="padding: 1rem; border-left: 4px solid #10b981;
                                             background: rgba(16, 185, 129, 0.08); margin-top: 10px;">
                                    <div style="font-weight: 700; color: #10b981;">✨ RECOMMENDED ACTION</div>
                                    <div style="color: var(--text-primary); margin-top: 4px;">
                                        Switch to <b>{msg['recommended_mode']}</b> from the sidebar menu to start!
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            # Show Smart Suggestion callout
                            if msg.get("suggestion"):
                                st.markdown(
                                    f'<div class="glass-card" style="padding: 10px 14px; border-left: 4px solid #06b6d4; '
                                    f'background: rgba(6, 182, 212, 0.08); margin-top: 8px; font-size: 0.95rem; color: var(--text-primary);">'
                                    f'💡 <b>Nova Suggests:</b> {msg["suggestion"]}</div>',
                                    unsafe_allow_html=True
                                )

                            # Read Aloud button for accessibility
                            col_tts, _ = st.columns([1, 4])
                            with col_tts:
                                if st.button(f"🔊 Read Aloud", key=f"tts_msg_{idx}"):
                                    if self.tts:
                                        st.toast("🔊 Nova speaking...")
                                        self.tts.speak(msg["content"])

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

            # Interactive Quick-Action Buttons inside Chat Tab
            st.markdown("##### 💡 Try Asking Nova:")
            qcol1, qcol2, qcol3 = st.columns(3)
            with qcol1:
                st.button(
                    "🤟 Explain Sign Language mode",
                    key="quick_chat_1",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("Explain Sign Language mode in simple words.",)
                )
                st.button(
                    "📖 How to read Bengali text?",
                    key="quick_chat_2",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("How do I scan a document with Bengali text?",)
                )
            with qcol2:
                st.button(
                    "😊 How does Emotion Recognition work?",
                    key="quick_chat_3",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("Explain how Emotion Recognition works.",)
                )
                st.button(
                    "🌍 Describe my surroundings",
                    key="quick_chat_4",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("I'm visually impaired. Please explain Scene Description mode.",)
                )
            with qcol3:
                st.button(
                    "🔧 Why is my photo blurry?",
                    key="quick_chat_5",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("Why is my photo blurry and how can I fix it?",)
                )
                st.button(
                    "🧠 Explain PyTorch AI models",
                    key="quick_chat_6",
                    use_container_width=True,
                    on_click=self._send_quick_message,
                    args=("Explain the PyTorch and Transformer AI models in SensAI.",)
                )

            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

            # Chat Input at bottom of tab with reliable session state callback
            def _on_nova_chat_submit():
                text = st.session_state.get("nova_chat_input_text", "").strip()
                if text:
                    self._send_quick_message(text)
                    st.session_state["nova_chat_input_text"] = ""

            inp_col, btn_col = st.columns([6, 1])
            with inp_col:
                st.text_input(
                    "Ask Nova anything about SensAI",
                    key="nova_chat_input_text",
                    placeholder="Ask Nova anything about SensAI (e.g., 'How do I scan a document?' or 'Why is my photo blurry?')...",
                    label_visibility="collapsed",
                    on_change=_on_nova_chat_submit
                )
            with btn_col:
                if st.button("Send 🚀", key="send_nova_btn", use_container_width=True):
                    _on_nova_chat_submit()
                    st.rerun()



        # ── TAB 2: INTERACTIVE TUTORIALS ────────────────────────────────────────
        with tab_tut:
            st.markdown("#### 📖 Step-by-Step Interactive Walkthroughs")
            st.write("Select any assistive feature below to view numbered instructions:")

            tut_choice = st.selectbox(
                "Choose a tutorial walkthrough:",
                [
                    "How to use Sign Language Recognition",
                    "How to scan documents correctly (OCR)",
                    "How to capture emotion images",
                    "How Scene Description works"
                ],
                key="tut_select"
            )

            tut_data = self.nova.get_tutorial(tut_choice)
            st.markdown(f"### {tut_data['title']}")
            
            for step_idx, step in enumerate(tut_data["steps"], 1):
                st.markdown(f"""
                <div class="glass-card" style="padding: 1rem 1.25rem; display: flex; align-items: flex-start; gap: 1rem;
                            border-left: 4px solid #6366f1; margin-bottom: 0.75rem;">
                    <div style="background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.5);
                                color: var(--text-primary); width: 32px; height: 32px; border-radius: 50%;
                                display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">
                        {step_idx}
                    </div>
                    <div style="color: var(--text-primary); font-size: 1.05rem; line-height: 1.5; align-self: center;">
                        {step}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            col_tts_tut, _ = st.columns([1, 3])
            with col_tts_tut:
                if st.button("🔊 Read Tutorial Aloud", key="tts_tutorial"):
                    if self.tts:
                        spoken = f"{tut_data['title']}. " + " ".join(tut_data["steps"])
                        st.toast("🔊 Speaking tutorial steps...")
                        self.tts.speak(spoken)

        # ── TAB 3: SMART IMAGE GUIDANCE ─────────────────────────────────────────
        with tab_guide:
            st.markdown("#### 📷 Smart Camera & Lighting Guidance (Pre-Upload Checklist)")
            st.write("Before uploading a photo or launching a live camera, verify these rules for maximum neural accuracy:")

            guide_mode = st.radio(
                "Select mode checklist:",
                [
                    "🤟 Sign Language Recognition",
                    "📖 Printed Text (OCR)",
                    "😊 Facial Emotion Detection",
                    "🌍 Scene Description"
                ],
                horizontal=True,
                key="guide_radio"
            )

            guide_data = self.nova.get_image_guidance(guide_mode)
            st.markdown(f"### {guide_data['title']}")

            for tip in guide_data["tips"]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 0.9rem 1.2rem; display: flex; align-items: center; gap: 0.8rem;
                            border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.07); margin-bottom: 0.6rem;">
                    <span style="font-size: 1.3rem;">✅</span>
                    <span style="color: var(--text-primary); font-size: 1.05rem; font-weight: 500;">{tip}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── TAB 4: UPLOAD VALIDATION & TROUBLESHOOTING ──────────────────────────
        with tab_diag:
            st.markdown("#### 🔧 Upload Validation & Diagnostic Studio")
            st.write("Experiencing poor predictions or blurry results? Select an issue below for instant diagnosis:")

            issue_choice = st.selectbox(
                "Select symptom or error condition:",
                [
                    "Blurry image",
                    "Low lighting",
                    "Wrong camera angle",
                    "Unsupported gesture",
                    "Text too small",
                    "Face partially hidden",
                    "Multiple people in frame"
                ],
                key="diag_select"
            )

            diag_res = self.nova.get_upload_validation_advice(issue_choice)

            render_result_box(
                text=f'<span style="color: var(--text-primary); font-weight: 600;">{diag_res["diagnosis"]}</span>',
                title=f"Diagnosis: {diag_res['issue']}",
                icon="🔍",
                subtext="Neural Confidence Root Cause Analysis"
            )

            st.markdown("#### 🛠️ Recommended Practical Solutions")
            for sol in diag_res["solutions"]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 0.8rem 1.1rem; display: flex; align-items: center; gap: 0.75rem;
                            border-left: 4px solid #8b5cf6; margin-bottom: 0.5rem;">
                    <span style="color: #a78bfa;">👉</span>
                    <span style="color: var(--text-primary); font-size: 1rem;">{sol}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 🔄 Actionable Recovery Protocol")
            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; border-left: 4px solid #10b981;
                        background: rgba(16, 185, 129, 0.1); color: var(--text-primary); font-size: 1.05rem;">
                ✔ <b>Next Step:</b> {diag_res['actionable_recovery']}
            </div>
            """, unsafe_allow_html=True)

        # ── TAB 5: AI FEATURE EXPLAINER ─────────────────────────────────────────
        with tab_ai:
            st.markdown("#### 🧠 Neural Architecture & AI Explainer Studio")
            st.write("Understand how SensAI processes multimodal data using PyTorch, TensorFlow, OpenCV, and Transformers:")

            tech_toggle = st.toggle("🔬 Developer Technical Deep-Dive Mode (Architecture details)", value=False, key="tech_toggle")

            model_choice = st.selectbox(
                "Select AI model or pipeline:",
                [
                    "PyTorch Temporal Transformer (Sign Language)",
                    "MediaPipe (Hand & Landmark Tracking)",
                    "Tesseract OCR (Printed Text Reader)",
                    "DeepFace FER+ (Facial Emotion Detection)",
                    "Salesforce BLIP (Scene Description)",
                    "All Features Overview"
                ],
                key="model_select"
            )

            exp_data = self.nova.get_feature_explanation(model_choice, technical=tech_toggle)

            render_result_box(
                text=f'<div style="line-height: 1.7; color: var(--text-primary);">{exp_data["text"]}</div>',
                title=exp_data["title"],
                icon="🧠",
                subtext="Technical Level: Developer Deep-Dive" if tech_toggle else "Technical Level: Simple & Accessible"
            )

            col_tts_ai, _ = st.columns([1, 3])
            with col_tts_ai:
                if st.button("🔊 Read Explainer Aloud", key="tts_ai"):
                    if self.tts:
                        st.toast("🔊 Speaking AI explanation...")
                        self.tts.speak(exp_data["text"])

        # ── TAB 6: FAQ & ACCESSIBILITY GUIDE ────────────────────────────────────
        with tab_faq:
            st.markdown("#### ❓ Frequently Asked Questions (FAQ)")
            st.write("Expand any topic below for quick answers:")

            faq_list = self.nova.get_faq()
            for faq in faq_list:
                with st.expander(f"📌 {faq['question']}"):
                    st.write(faq["answer"])
                    if st.button("🔊 Read Aloud", key=f"tts_faq_{faq['question'][:10]}"):
                        if self.tts:
                            st.toast("🔊 Speaking FAQ answer...")
                            self.tts.speak(faq["answer"])

            st.divider()

            st.markdown("#### ♿ Accessibility & Keyboard Navigation Guide")
            acc_data = self.nova.get_accessibility_tips()
            
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.1rem; border-left: 4px solid #06b6d4; background: rgba(6, 182, 212, 0.08);">
                <div style="font-weight: 700; color: #06b6d4; margin-bottom: 4px;">🤝 SENSAI ACCESSIBILITY PLEDGE</div>
                <div style="color: var(--text-primary); font-size: 1rem;">{acc_data['simple_language_pledge']}</div>
            </div>
            """, unsafe_allow_html=True)

            col_kb, col_sr = st.columns(2)
            with col_kb:
                st.markdown("##### ⌨️ Keyboard Navigation")
                for kb in acc_data["keyboard_navigation"]:
                    st.markdown(f"• **{kb}**")
                    
            with col_sr:
                st.markdown("##### 🔊 Screen Reader Tips")
                for sr in acc_data["screen_reader_tips"]:
                    st.markdown(f"• **{sr}**")

    def _send_quick_message(self, text: str) -> None:
        """
        Helper to append user input and Nova response into session state chat history.
        """
        st.session_state.nova_history.append({"role": "user", "content": text})
        res = self.nova.process_chat_message(
            text,
            st.session_state.nova_history,
            st.session_state.nova_context
        )
        if res.get("context_updates"):
            st.session_state.nova_context.update(res["context_updates"])
        st.session_state.nova_history.append({
            "role": "assistant",
            "content": res["reply"],
            "recommended_mode": res.get("recommended_mode"),
            "suggestion": res.get("suggestion", "")
        })
