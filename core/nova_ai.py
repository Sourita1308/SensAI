"""
core/nova_ai.py
SensAI — Multimodal Accessibility AI System
Nova AI Accessibility Assistant — Intelligent core engine for intent recognition,
smart image guidance, upload validation troubleshooting, accessibility assistance,
interactive tutorials, beginner vs. technical feature explanations, FAQ, and smart suggestions.
"""

import re
from typing import Dict, List, Optional, Any


class NovaAI:
    """
    Intelligent Accessibility Assistant ('Nova') for SensAI.
    Designed specifically to assist users with disabilities, guide them through features,
    recommend appropriate modes based on natural intent, diagnose image/prediction issues,
    and provide simple, step-by-step accessible guidance.
    """

    def __init__(self, tts=None):
        self.tts = tts
        self.name = "Nova"
        self.role = "Accessibility Assistant for SensAI"

    # ── 1. GREETING & ONBOARDING ──────────────────────────────────────────────
    def get_greeting(self) -> str:
        return (
            "Hello! I am Nova, your dedicated Accessibility Assistant for SensAI. "
            "I'm here to help you understand, navigate, and get the most out of every feature. "
            "How can I assist you today? You can ask me to recommend a mode, explain how to take "
            "a photo, walk you through a tutorial, or troubleshoot any issue!"
        )

    # ── 2. INTELLIGENT MODE RECOMMENDATION ────────────────────────────────────
    def detect_intent_and_recommend(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Understand user intention from natural language and recommend the correct SensAI mode.
        Examples:
            "I want to understand this sign." -> Sign Language Recognition
            "I have a picture containing Bengali text." -> Printed Text (OCR)
            "I want to know how this person feels." -> Facial Emotion Detection
            "I'm visually impaired. Please describe this image." -> Scene Description
        """
        msg = user_message.lower().strip()

        # 0. Check for general knowledge questions or AI model inquiries (e.g. "What is MediaPipe?")
        knowledge_keywords = [
            "what is ", "what are ", "who is ", "how does ", "how do ", "why is ", "tell me about ",
            "explain ", "mediapipe", "media pipe", "media-pipe", "tesseract", "blip", "deepface",
            "fer+", "pytorch", "transformer", "ai model", "ai models"
        ]
        if any(k in msg for k in knowledge_keywords):
            matched_model = self._match_model_explanation(msg)
            if matched_model:
                exp = self.get_feature_explanation(matched_model, technical=True)
                return {
                    "recommended_mode": None,
                    "mode_key": "knowledge",
                    "response": f"**{exp['title']}**\n\n{exp['both']}",
                    "suggestion": "Would you like a beginner summary or a technical explanation of another AI model?",
                    "update_context": {"last_topic": "explainer"}
                }
            exp = self.get_feature_explanation("overview", technical=True)
            return {
                "recommended_mode": None,
                "mode_key": "knowledge",
                "response": f"**{exp['title']}**\n\n{exp['text']}",
                "suggestion": "Ask me about any specific model like 'MediaPipe' or 'Tesseract OCR' for details!",
                "update_context": {"last_topic": "explainer"}
            }

        # Check for context-aware continuation (e.g. User says "text" after Nova asked what to analyze)
        if context and context.get("waiting_for_category"):
            if any(k in msg for k in ["sign", "hand", "gesture", "deaf"]):
                return self._recommend_result("sign_language")
            if any(k in msg for k in ["text", "bengali", "english", "book", "read", "document", "print"]):
                return self._recommend_result("ocr")
            if any(k in msg for k in ["face", "emotion", "feeling", "feel", "happy", "sad", "mood"]):
                return self._recommend_result("emotion")
            if any(k in msg for k in ["scene", "picture", "image", "describe", "surroundings", "environment"]):
                return self._recommend_result("scene")

        # Intent: Sign Language Recognition
        if any(k in msg for k in ["sign", "gesture", "hand", "isl", "deaf", "mute", "finger", "ekdike", "dao", "koro"]):
            return self._recommend_result("sign_language")

        # Intent: Printed Text -> Speech (OCR)
        if any(k in msg for k in ["bengali", "bangla", "text", "ocr", "read", "book", "document", "printed", "letter", "word", "page", "scan"]):
            return self._recommend_result("ocr")

        # Intent: Facial Emotion -> Speech
        if any(k in msg for k in ["feel", "feels", "emotion", "happy", "sad", "calm", "angry", "surprised", "face", "facial", "expression", "mood"]):
            return self._recommend_result("emotion")

        # Intent: Scene Description -> Speech
        if any(k in msg for k in ["describe", "visually impaired", "blind", "scene", "surroundings", "what is this", "what's in this", "picture of", "photo of", "around me", "environment"]):
            return self._recommend_result("scene")

        # General upload intent without specifying category
        if any(k in msg for k in ["upload", "image", "photo", "camera", "picture", "analyze", "analyse", "use"]):
            return {
                "recommended_mode": "General Guidance",
                "mode_key": "unknown",
                "response": "What would you like to analyze? A hand sign, text, a person's face, or a general scene?",
                "suggestion": "You can reply with 'hand sign', 'Bengali text', 'emotion', or 'describe scene'.",
                "update_context": {"waiting_for_category": True}
            }

        # Check if asking about error recovery or troubleshooting
        if any(k in msg for k in ["error", "wrong", "incorrect", "blurry", "fail", "not working", "bad", "poor"]):
            return self._troubleshoot_general()

        # Default helpful response
        return {
            "recommended_mode": None,
            "mode_key": "general",
            "response": (
                "I can help you choose the right mode! Here is what SensAI can do:\n"
                "• **Sign Language Recognition**: Translates Indian Sign Language gestures into speech.\n"
                "• **Printed Text (OCR)**: Reads Bengali and English printed text aloud.\n"
                "• **Facial Emotion Detection**: Recognizes facial emotions and announces them calmly.\n"
                "• **Scene Description**: Describes photos and surroundings in full, rich sentences."
            ),
            "suggestion": "Would you like me to show you a step-by-step tutorial on how to use any of these modes?",
            "update_context": {}
        }

    def _recommend_result(self, mode_key: str) -> Dict[str, Any]:
        recs = {
            "sign_language": {
                "recommended_mode": "🤟 Sign Language → Speech",
                "mode_key": "Sign Language",
                "response": (
                    "**I recommend: Sign Language Recognition Mode.**\n\n"
                    "This mode uses a deep learning Temporal Transformer and MediaPipe to detect "
                    "hand gestures and speak them aloud."
                ),
                "suggestion": "Before you try it, remember to keep your hand completely visible and use proper lighting!",
                "update_context": {"last_recommended": "Sign Language", "waiting_for_category": False}
            },
            "ocr": {
                "recommended_mode": "📖 Printed Text → Speech (OCR)",
                "mode_key": "Printed Text (OCR)",
                "response": (
                    "**I recommend: Printed Text → Speech (OCR) Mode.**\n\n"
                    "This mode uses Tesseract OCR to accurately extract Bengali and English text from "
                    "documents, books, or labels and reads the complete text aloud."
                ),
                "suggestion": "For best accuracy, ensure the text is sharp, avoid shadows, and capture from directly above!",
                "update_context": {"last_recommended": "Printed Text (OCR)", "waiting_for_category": False}
            },
            "emotion": {
                "recommended_mode": "😊 Facial Emotion → Speech",
                "mode_key": "Facial Emotion",
                "response": (
                    "**I recommend: Facial Emotion → Speech Mode.**\n\n"
                    "This mode uses DeepFace AI to analyze facial expressions and announce feelings calmly "
                    "with a 7-second cooldown so it never repeats continuously."
                ),
                "suggestion": "Ensure the person's face is clearly visible and avoid masks or heavy facial shadows.",
                "update_context": {"last_recommended": "Facial Emotion", "waiting_for_category": False}
            },
            "scene": {
                "recommended_mode": "🌍 Scene Description → Speech",
                "mode_key": "Scene Description",
                "response": (
                    "**I recommend: Scene Description → Speech Mode.**\n\n"
                    "This mode uses Salesforce BLIP AI to generate a full, rich natural sentence describing "
                    "the entire image or surroundings for visually impaired users."
                ),
                "suggestion": "Capture the whole scene and ensure the main objects are well-lit and not blurry.",
                "update_context": {"last_recommended": "Scene Description", "waiting_for_category": False}
            }
        }
        return recs.get(mode_key, {})

    # ── 3. SMART IMAGE GUIDANCE ───────────────────────────────────────────────
    def get_image_guidance(self, mode_name: str) -> Dict[str, Any]:
        """
        Explain how to obtain the best image results before uploading.
        """
        key = mode_name.lower().strip()
        guidance_map = {
            "sign language": {
                "title": "🤟 Smart Image Guidance: Sign Language Recognition",
                "tips": [
                    "**Keep your hand completely visible** within the camera frame.",
                    "**Maintain proper lighting** on your hand and fingers.",
                    "**Avoid cluttered backgrounds** so the AI can track fingers clearly.",
                    "**Keep the camera steady** without shaking during gesture capture."
                ]
            },
            "ocr": {
                "title": "📖 Smart Image Guidance: Printed Text (OCR)",
                "tips": [
                    "**Ensure text is sharp** and in clear focus without motion blur.",
                    "**Avoid shadows** or glare across the printed text.",
                    "**Capture from directly above** the page so text lines are horizontal.",
                    "**Use high resolution** so small Bengali or English letters are distinct."
                ]
            },
            "emotion": {
                "title": "😊 Smart Image Guidance: Facial Emotion Detection",
                "tips": [
                    "**Face should be clearly visible** and looking toward the camera.",
                    "**Avoid masks or heavy occlusion** covering the mouth or eyes.",
                    "**Good lighting improves accuracy**—ensure even lighting across your face.",
                    "**Hold expression briefly**—the assistant speaks calmly without repetition."
                ]
            },
            "scene": {
                "title": "🌍 Smart Image Guidance: Scene Description",
                "tips": [
                    "**Capture the whole scene** to give the AI context.",
                    "**Avoid blurry images** by holding the camera steady.",
                    "**Ensure the main objects are visible** and well-lit.",
                    "**Include backgrounds** for rich, multi-word environmental descriptions."
                ]
            }
        }
        for k, val in guidance_map.items():
            if k in key:
                return val
        # Default all guidance
        return {
            "title": "💡 Smart Image Guidance for All Modes",
            "tips": [
                "**Proper Lighting**: Ensure even, bright light on your subject.",
                "**Sharp Focus**: Hold your camera steady to prevent motion blur.",
                "**Clear Subject**: Keep hands, text, or faces centered and unhidden.",
                "**High Resolution**: Upload clear photos for highest AI accuracy."
            ]
        }

    # ── 4. UPLOAD VALIDATION ASSISTANT & TROUBLESHOOTING ──────────────────────
    def get_upload_validation_advice(self, issue_type: str) -> Dict[str, Any]:
        """
        Diagnose poor predictions and provide practical solutions.
        Possible reasons: Blurry image, Low lighting, Wrong camera angle, Unsupported gesture,
        Text too small, Face partially hidden, Multiple people in frame.
        """
        issues = {
            "blurry image": {
                "diagnosis": "The image or webcam stream is blurry or out of focus.",
                "solutions": [
                    "Hold your camera steady or rest it on a flat surface.",
                    "Wait 1-2 seconds for your camera auto-focus to lock before capturing.",
                    "Ensure the lens is clean and free of smudges."
                ]
            },
            "low lighting": {
                "diagnosis": "There is insufficient lighting on the subject.",
                "solutions": [
                    "Move closer to a window or turn on an overhead room light.",
                    "Avoid strong backlighting (don't stand with a bright window directly behind you).",
                    "Ensure light falls evenly on your hand, text, or face."
                ]
            },
            "wrong camera angle": {
                "diagnosis": "The camera angle is tilted or too oblique.",
                "solutions": [
                    "For documents (OCR): Position the camera directly above the paper.",
                    "For Sign Language: Position your hand at eye level facing the camera directly.",
                    "For Facial Emotion: Face the webcam straight-on rather than from the side."
                ]
            },
            "unsupported gesture": {
                "diagnosis": "The hand gesture is not yet in the active vocabulary dictionary.",
                "solutions": [
                    "SensAI currently recognizes trained Indian Sign Language (ISL) signs including 'Ekdike Cholachol', 'Dao', 'Koro', 'Ami', 'Tumi', etc.",
                    "Ensure your fingers and palm orientation match the standard ISL sign.",
                    "You can check the ISL dataset in the repository for supported signs."
                ]
            },
            "text too small": {
                "diagnosis": "The printed characters are too small for optical recognition.",
                "solutions": [
                    "Move the camera closer to the text or document.",
                    "Crop out extra borders so the text fills at least 70% of the image.",
                    "Ensure image resolution is high enough to see Bengali conjunct letters clearly."
                ]
            },
            "face partially hidden": {
                "diagnosis": "The person's face is partially occluded.",
                "solutions": [
                    "Remove masks, dark sunglasses, or items covering the mouth and eyes.",
                    "Ensure hair or hands are not blocking facial landmarks.",
                    "Look straight toward the camera."
                ]
            },
            "multiple people in frame": {
                "diagnosis": "There are multiple faces or people visible in the frame.",
                "solutions": [
                    "Ensure only one person is in the center of the frame for emotion detection.",
                    "For sign language, keep background bystanders out of view so MediaPipe tracks the correct hand."
                ]
            }
        }
        clean_key = issue_type.lower().strip()
        for k, val in issues.items():
            if k in clean_key:
                return {
                    "issue": k.title(),
                    "diagnosis": val["diagnosis"],
                    "solutions": val["solutions"],
                    "actionable_recovery": (
                        f"**Error Recovery Guidance:** I couldn't get a confident result because of a likely **{k}**. "
                        f"{val['solutions'][0]}"
                    )
                }
        return {
            "issue": "General Validation Checklist",
            "diagnosis": "Let's diagnose why the AI prediction was incorrect.",
            "solutions": [
                "Check that lighting is bright and even.",
                "Ensure the subject (hand, text, or face) is centered and sharp.",
                "Avoid blurry motion or harsh shadows across the frame."
            ],
            "actionable_recovery": "Please retake the photo with bright, even lighting and ensure the subject is centered and clearly visible."
        }

    def _troubleshoot_general(self) -> Dict[str, Any]:
        return {
            "recommended_mode": "Upload Validation Assistant",
            "mode_key": "troubleshoot",
            "response": (
                "**Let's diagnose why the prediction might be incorrect.**\n\n"
                "Here are the most common causes and practical solutions:\n"
                "1. **Blurry Image**: Hold the camera steady and wait for focus.\n"
                "2. **Low Lighting**: Turn on a room light or face a window.\n"
                "3. **Wrong Camera Angle**: For OCR, shoot directly from above.\n"
                "4. **Text Too Small**: Move closer so text fills the frame.\n"
                "5. **Face Partially Hidden / Multiple People**: Center one clear face."
            ),
            "suggestion": "You can ask me about any specific issue like 'blurry image' or 'text too small' for detailed advice!",
            "update_context": {}
        }

    # ── 5. ACCESSIBILITY ASSISTANT GUIDELINES ─────────────────────────────────
    def get_accessibility_tips(self) -> Dict[str, Any]:
        """
        Provide accessibility support, simple language explanations, and keyboard navigation guidance.
        """
        return {
            "title": "♿ SensAI Accessibility Guide & Keyboard Navigation",
            "simple_language_pledge": (
                "Nova uses short, easy-to-read language and avoids complex technical terms "
                "unless you specifically ask for a technical explanation."
            ),
            "keyboard_navigation": [
                "**Tab / Shift + Tab**: Navigate between buttons, tabs, and input fields.",
                "**Enter / Space**: Activate selected buttons (such as '🔊 Read Aloud' or mode switches).",
                "**Arrow Keys**: Move between options in the mode selector radio list.",
                "**Esc**: Close open menus or expandable settings panels."
            ],
            "screen_reader_tips": [
                "Every mode features a **'🔊 Read Aloud'** button that speaks results aloud.",
                "In OCR and Scene Description modes, SensAI reads complete words and sentences clearly.",
                "In Emotion mode, SensAI speaks calmly with a 7-second cooldown to prevent repetition."
            ]
        }

    # ── 6. INTERACTIVE TUTORIALS ──────────────────────────────────────────────
    def get_tutorial(self, tutorial_name: str) -> Dict[str, Any]:
        """
        Provide guided walkthroughs presented as simple numbered steps.
        """
        key = tutorial_name.lower().strip()
        tutorials = {
            "sign language": {
                "title": "How to use Sign Language Recognition",
                "steps": [
                    "Open the **'🤟 Sign Language → Speech'** tab from the sidebar.",
                    "Choose **Webcam Live Stream** or **Upload Image**.",
                    "Position your hand clearly in the center of the camera frame with good lighting.",
                    "Make the Indian Sign Language (ISL) gesture and hold it steady for 1 second.",
                    "SensAI will detect your hand landmarks, announce the gesture name aloud, and display the text on screen."
                ]
            },
            "ocr": {
                "title": "How to scan documents correctly",
                "steps": [
                    "Open the **'📖 Printed Text → Speech (OCR)'** tab from the sidebar.",
                    "Place your Bengali or English document flat on a well-lit table.",
                    "Ensure there are no dark shadows or glare covering the letters.",
                    "Upload the photo or capture it from directly above.",
                    "Click **'🔊 Read Aloud'** to hear the entire text read out loud as complete words and sentences."
                ]
            },
            "emotion": {
                "title": "How to capture emotion images",
                "steps": [
                    "Open the **'😊 Facial Emotion → Speech'** tab from the sidebar.",
                    "Ensure your face is clearly visible without masks, sunglasses, or heavy shadows.",
                    "Look naturally toward the camera with your expression.",
                    "SensAI analyzes facial micro-expressions and announces your emotion.",
                    "The assistant uses a 7-second calm cooldown so it never repeats continuously."
                ]
            },
            "scene": {
                "title": "How Scene Description works",
                "steps": [
                    "Open the **'🌍 Scene Description → Speech'** tab from the sidebar.",
                    "Upload a photo of any scene, object, or environment.",
                    "SensAI's vision-language AI model analyzes the entire picture.",
                    "It generates a complete, rich natural sentence describing what is around you.",
                    "Listen as SensAI speaks the full scene description aloud."
                ]
            }
        }
        for k, val in tutorials.items():
            if k in key:
                return val
        return {
            "title": "Interactive Tutorials Available",
            "steps": [
                "1. **How to use Sign Language Recognition**",
                "2. **How to scan documents correctly (OCR)**",
                "3. **How to capture emotion images**",
                "4. **How Scene Description works**"
            ]
        }

    # ── 7. AI FEATURE EXPLAINER (BEGINNER vs. TECHNICAL) ──────────────────────
    def get_feature_explanation(self, feature_name: str, technical: bool = False) -> Dict[str, str]:
        """
        Explain every feature in beginner-friendly language, or provide technical
        explanations describing the underlying AI models when requested.
        """
        key = feature_name.lower().strip()
        explainers = {
            "pytorch temporal transformer": {
                "name": "PyTorch Temporal Transformer (Sign Language)",
                "beginner": (
                    "**In Simple Words**: This AI watches how your hand moves through the air over time. "
                    "Just like reading a sentence word-by-word, it looks at the flow of your hand gesture "
                    "to understand which Indian Sign Language word you are signing."
                ),
                "technical": (
                    "**Technical Deep-Dive**: We use a custom PyTorch sequence-to-sequence Temporal Transformer. "
                    "It receives a time-series of 21 3D hand landmark coordinates (63 features per frame) across "
                    "a sequence buffer. Multi-head self-attention layers capture temporal dependencies and "
                    "motion dynamics, classifying gestures with high precision while ignoring background clutter."
                )
            },
            "mediapipe": {
                "name": "MediaPipe (Hand & Landmark Tracking)",
                "beginner": (
                    "**In Simple Words**: MediaPipe acts like an instant digital ruler that finds your hand "
                    "and fingers in the camera, drawing an invisible skeleton on your hand so the AI knows "
                    "exactly where your fingers are pointing."
                ),
                "technical": (
                    "**Technical Deep-Dive**: Google's MediaPipe Hands framework uses a single-shot palm detector "
                    "followed by a landmark regression subgraph to extract 21 3D spatial coordinates (x, y, z) "
                    "per hand in real time (>30 FPS) with palm orientation and confidence scoring."
                )
            },
            "tesseract ocr": {
                "name": "Tesseract OCR (Printed Text Reader)",
                "beginner": (
                    "**In Simple Words**: Tesseract is an electronic reading assistant. It scans a photo of "
                    "a book or label, recognizes letters in both Bengali and English, and turns them into "
                    "clean digital text that our speech voice can read out loud."
                ),
                "technical": (
                    "**Technical Deep-Dive**: Tesseract v4/v5 utilizes deep Long Short-Term Memory (LSTM) "
                    "recurrent neural networks trained on Unicode character sets. It performs adaptive line "
                    "thresholding, layout analysis, and Bengali conjunct character segmentation ('ben+eng')."
                )
            },
            "deepface fer+": {
                "name": "DeepFace FER+ (Facial Emotion Detection)",
                "beginner": (
                    "**In Simple Words**: This AI looks at facial expressions like smiles, calm eyes, or raised "
                    "eyebrows to understand how someone is feeling, speaking the emotion gently without being repetitive."
                ),
                "technical": (
                    "**Technical Deep-Dive**: DeepFace wraps deep convolutional architectures (e.g. VGG-Face / "
                    "FER+ models) trained on facial expression datasets. It detects facial bounding boxes, "
                    "normalizes pose, and outputs softmax probability distributions across 7 emotion classes."
                )
            },
            "salesforce blip": {
                "name": "Salesforce BLIP (Scene Description)",
                "beginner": (
                    "**In Simple Words**: BLIP is an artificial visual storyteller. You show it any photograph, "
                    "and it writes a complete, natural sentence describing what is in the picture so visually "
                    "impaired users can understand their surroundings."
                ),
                "technical": (
                    "**Technical Deep-Dive**: Bootstrapped Language-Image Pretraining (BLIP) is a multimodal "
                    "vision-language transformer. An image encoder (ViT) converts image patches into embeddings, "
                    "and a text decoder uses beam search (num_beams=5, min_length=12) to generate rich, descriptive "
                    "captions with no-repeat n-gram constraints."
                )
            }
        }

        for k, val in explainers.items():
            if k in key:
                return {
                    "title": val["name"],
                    "text": val["technical"] if technical else val["beginner"],
                    "both": f"{val['beginner']}\n\n{val['technical']}"
                }

        # Default summary of all models
        if technical:
            return {
                "title": "Technical AI Models in SensAI",
                "text": (
                    "• **PyTorch Temporal Transformer**: Sequence attention on 63D hand landmarks.\n"
                    "• **MediaPipe**: Real-time 21-point 3D hand and facial mesh tracking.\n"
                    "• **Tesseract OCR**: LSTM multilingual character recognition (Bengali + English).\n"
                    "• **DeepFace FER+**: Deep convolutional facial expression classification.\n"
                    "• **Salesforce BLIP**: Multimodal vision-language transformer for rich scene captioning."
                )
            }
        return {
            "title": "Beginner-Friendly AI Overview",
            "text": (
                "• **Sign Language AI**: Watches finger movements and translates gestures to speech.\n"
                "• **MediaPipe**: Draws an invisible skeleton on hands in real time.\n"
                "• **Tesseract OCR**: Reads Bengali and English printed letters from photos.\n"
                "• **DeepFace**: Understands calm, happy, or sad expressions naturally.\n"
                "• **Salesforce BLIP**: Describes whole pictures and scenes in complete sentences."
            )
        }

    def _match_model_explanation(self, msg: str) -> Optional[str]:
        if any(k in msg for k in ["mediapipe", "media pipe", "media-pipe"]):
            return "mediapipe"
        if any(k in msg for k in ["tesseract", "ocr"]):
            return "tesseract ocr"
        if any(k in msg for k in ["deepface", "fer+"]):
            return "deepface fer+"
        if any(k in msg for k in ["blip", "salesforce"]):
            return "salesforce blip"
        if any(k in msg for k in ["pytorch", "transformer"]):
            return "pytorch temporal transformer"
        return None

    # ── 8. FREQUENTLY ASKED QUESTIONS (FAQ) ───────────────────────────────────
    def get_faq(self) -> List[Dict[str, str]]:
        return [
            {
                "question": "What is SensAI?",
                "answer": (
                    "SensAI is a comprehensive multimodal AI accessibility platform designed to bridge communication "
                    "and perceptual gaps for individuals with visual, auditory, or speech impairments through live "
                    "sign language recognition, OCR document reading, facial emotion speech, and scene descriptions."
                )
            },
            {
                "question": "Who is this platform for?",
                "answer": (
                    "SensAI is designed for:\n"
                    "• **Deaf & Hard-of-Hearing Users**: Communicating via Indian Sign Language.\n"
                    "• **Visually Impaired Users**: Reading printed documents and understanding visual scenes.\n"
                    "• **Neurodivergent / Autistic Users**: Recognizing facial emotions in social interactions.\n"
                    "• **Anyone**: Needing accessible text-to-speech in English and Bengali."
                )
            },
            {
                "question": "Which mode should I use?",
                "answer": (
                    "• Use **Sign Language Mode** to translate hand gestures into speech.\n"
                    "• Use **Printed Text (OCR) Mode** to scan and read Bengali/English documents.\n"
                    "• Use **Facial Emotion Mode** to detect and announce facial expressions.\n"
                    "• Use **Scene Description Mode** to hear a rich description of an image or room."
                )
            },
            {
                "question": "Why is my prediction incorrect?",
                "answer": (
                    "The most common reasons are **blurry photos**, **low lighting**, **wrong camera angle**, "
                    "or **unsupported gestures**. You can use Nova's Upload Validation Assistant to diagnose "
                    "and fix the exact cause instantly!"
                )
            },
            {
                "question": "Which image formats are supported?",
                "answer": "SensAI supports standard image formats including **JPG, JPEG, PNG, and BMP**."
            },
            {
                "question": "Does the system work in real time?",
                "answer": (
                    "**Yes!** In Sign Language and Facial Emotion modes, SensAI supports real-time webcam "
                    "stream analysis. In OCR and Scene Description modes, it analyzes uploaded photos in seconds."
                )
            },
            {
                "question": "What languages are supported?",
                "answer": (
                    "SensAI supports **English** and **Bengali (বাংলা)** across text reading, OCR, and speech synthesis."
                )
            },
            {
                "question": "How accurate is the Sign Language model?",
                "answer": (
                    "The Sign Language Temporal Transformer achieves high precision (>90% on trained ISL gestures) "
                    "when proper lighting and a clear, unhidden hand posture are maintained."
                )
            }
        ]

    # ── 9. SMART SUGGESTIONS & PROACTIVE NEXT STEPS ───────────────────────────
    def get_smart_suggestion(self, last_action: str) -> str:
        """
        After every successful interaction, suggest useful next steps.
        """
        suggestions = {
            "sign_language": "You've translated a sign. Would you like to convert text from an image next?",
            "ocr": "You've read printed text. Would you like to see smart image tips for capturing documents?",
            "emotion": "I've analyzed that facial expression. Would you like to also describe the surrounding scene?",
            "scene": "I've described your image. Would you also like to extract any text present in it?",
            "tutorial": "Now that you've reviewed the steps, would you like to open that mode and try it out?"
        }
        return suggestions.get(last_action, "Would you like me to recommend another mode or show a tutorial?")

    # ── 10. CONTEXT-AWARE CONVERSATION PROCESSOR ──────────────────────────────
    def process_chat_message(self, user_message: str, history: List[Dict[str, str]], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user chat message in Nova Assistant, keeping track of conversation context.
        Returns:
            {
                "reply": str,
                "recommended_mode": Optional[str],
                "suggestion": str,
                "context_updates": dict
            }
        """
        msg = user_message.lower().strip()

        # 0a. Check Greetings & Persona Inquiries
        greeting_words = {"hi", "hello", "hey", "greetings", "start"}
        greeting_phrases = ["good morning", "good afternoon", "good evening", "who are you", "what is your name", "what is nova", "tell me about yourself"]
        msg_words = set(re.findall(r'\b\w+\b', msg))
        if msg_words.intersection(greeting_words) or any(p in msg for p in greeting_phrases):
            return {
                "reply": (
                    "👋 Hello! I am **Nova**, your dedicated AI Accessibility Companion for SensAI.\n\n"
                    "I can help you navigate SensAI's vision and speech modules, guide you through camera setups, "
                    "troubleshoot blurry or low-light uploads, explain our underlying PyTorch & Transformer AI models, "
                    "or recommend the best assistive mode for your needs!"
                ),
                "recommended_mode": None,
                "suggestion": "Ask me something like 'Which mode should I use?' or click a quick action button below!",
                "context_updates": {"last_topic": "greeting"}
            }


        # 0b. Check Platform Overview Queries
        if any(k in msg for k in ["what is sensai", "what is this app", "what is this platform", "who is this for", "about sensai"]):
            return {
                "reply": (
                    "**SensAI** is a state-of-the-art Multimodal AI Accessibility Studio designed to assist users with "
                    "visual, auditory, or speech impairments.\n\n"
                    "It offers 5 core intelligent modes:\n"
                    "• 🤟 **Sign Language → Speech**: Real-time ISL gesture translation.\n"
                    "• 📖 **Printed Text → Speech (OCR)**: Bengali & English document reader.\n"
                    "• 😊 **Facial Emotion → Speech**: Social expression & emotion announcer.\n"
                    "• 🌍 **Scene Description → Speech**: Environmental scene descriptor for visually impaired users.\n"
                    "• 🤖 **Nova AI Assistant**: Interactive companion for guidance and support."
                ),
                "recommended_mode": None,
                "suggestion": "Which mode would you like to explore first?",
                "context_updates": {"last_topic": "about_sensai"}
            }

        # 0c. Check Language & Speech Output Inquiries
        if any(k in msg for k in ["bengali", "bangla", "language", "audio", "speech", "voice", "read aloud", "tts"]):
            return {
                "reply": (
                    "**Languages & Audio Engine Features:**\n\n"
                    "• **Multilingual Support**: SensAI supports **English** and **Bengali (বাংলা)** for text extraction and speech.\n"
                    "• **Speech Velocity Control**: Adjust speech rate from 100 to 250 WPM in the sidebar.\n"
                    "• **Read Aloud Buttons**: Every answer and tutorial step includes a 🔊 **Read Aloud** button for accessible audio playback."
                ),
                "recommended_mode": "📖 Printed Text → Speech (OCR)",
                "suggestion": "Try clicking 🔊 Read Aloud on any response to hear Nova speak!",
                "context_updates": {"last_topic": "languages"}
            }

        # 1. Check if user asks for a tutorial
        if any(k in msg for k in ["how to", "tutorial", "walkthrough", "guide me", "steps", "instruction"]):
            for key in ["sign language", "ocr", "emotion", "scene"]:
                if key in msg:
                    tut = self.get_tutorial(key)
                    steps_text = "\n".join(tut["steps"])
                    reply = f"**{tut['title']}**\n\n{steps_text}"
                    return {
                        "reply": reply,
                        "recommended_mode": None,
                        "suggestion": self.get_smart_suggestion("tutorial"),
                        "context_updates": {"last_topic": "tutorial"}
                    }
            tut = self.get_tutorial("all")
            reply = (
                "**Here are the interactive tutorials available:**\n\n" +
                "\n".join(tut["steps"]) +
                "\n\nReply with any tutorial name (e.g. *'how to use sign language'*) for numbered steps!"
            )
            return {
                "reply": reply,
                "recommended_mode": None,
                "suggestion": "Which tutorial would you like to explore?",
                "context_updates": {"last_topic": "tutorial_list"}
            }

        # 2. Check if user asks about AI models / technical explanation / general knowledge
        knowledge_keywords = [
            "what is", "what are", "who is", "how does", "how do", "why is", "tell me about",
            "explain", "mediapipe", "media pipe", "media-pipe", "tesseract", "blip", "deepface",
            "fer+", "pytorch", "transformer", "ai model", "ai models", "technical"
        ]
        if any(k in msg for k in knowledge_keywords):
            matched_model = self._match_model_explanation(msg)
            if matched_model:
                exp = self.get_feature_explanation(matched_model, technical=True)
                return {
                    "reply": f"**{exp['title']}**\n\n{exp['both']}",
                    "recommended_mode": None,
                    "suggestion": "Would you like a beginner summary or a technical explanation of another AI model?",
                    "context_updates": {"last_topic": "explainer"}
                }
            exp = self.get_feature_explanation("overview", technical=True)
            return {
                "reply": f"**{exp['title']}**\n\n{exp['text']}",
                "recommended_mode": None,
                "suggestion": "Ask me about any specific model like 'MediaPipe' or 'Tesseract OCR' for details!",
                "context_updates": {"last_topic": "explainer"}
            }

        # 3. Check if user asks about errors or troubleshooting
        if any(k in msg for k in ["error", "blurry", "shadow", "wrong angle", "too small", "hidden", "not working", "why is my prediction", "incorrect", "problem", "issue"]):
            for issue_key in ["blurry image", "low lighting", "wrong camera angle", "unsupported gesture", "text too small", "face partially hidden", "multiple people in frame"]:
                if issue_key in msg or any(w in msg for w in issue_key.split() if len(w) > 3):
                    diag = self.get_upload_validation_advice(issue_key)
                    sols = "\n".join([f"• {s}" for s in diag["solutions"]])
                    reply = f"**Diagnosis: {diag['issue']}**\n{diag['diagnosis']}\n\n**Practical Solutions:**\n{sols}"
                    return {
                        "reply": reply,
                        "recommended_mode": None,
                        "suggestion": "Try adjusting your camera and let me know if the prediction improves!",
                        "context_updates": {"last_topic": "troubleshoot"}
                    }
            general = self._troubleshoot_general()
            return {
                "reply": general["response"],
                "recommended_mode": None,
                "suggestion": general["suggestion"],
                "context_updates": {"last_topic": "troubleshoot"}
            }

        # 4. Check FAQ questions
        for faq_item in self.get_faq():
            q_lower = faq_item["question"].lower()
            # Match if key query tokens exist in msg
            matching_tokens = [w for w in q_lower.split() if len(w) > 3 and w in msg]
            if len(matching_tokens) >= 2 or q_lower in msg:
                return {
                    "reply": f"**{faq_item['question']}**\n\n{faq_item['answer']}",
                    "recommended_mode": None,
                    "suggestion": "Would you like to ask another FAQ or try out one of the accessibility modes?",
                    "context_updates": {"last_topic": "faq"}
                }

        # 5. Default: Intelligent Mode Recommendation & Intent Recognition
        rec = self.detect_intent_and_recommend(user_message, context)
        return {
            "reply": rec.get("response", "I'm here to help you navigate SensAI! Ask me anything about sign language, text reading, emotion recognition, or scene descriptions."),
            "recommended_mode": rec.get("recommended_mode"),
            "suggestion": rec.get("suggestion", "What would you like to explore next?"),
            "context_updates": rec.get("update_context", {})
        }

