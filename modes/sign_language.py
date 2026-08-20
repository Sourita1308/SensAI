"""
modes/sign_language.py
Mode 1 — Real-Time Indian Sign Language (ISL) Recognition
Pipeline: Webcam → MediaPipe Holistic → Keypoint Sequences → Transformer → Text → TTS
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import mediapipe as mp
import json
import os
import threading
import time
from collections import deque
from core.base_mode import BaseMode
from core.tts_engine import TTSEngine


# ─── Transformer Model ────────────────────────────────────────────────────────

class SignTransformer(nn.Module):
    """
    Temporal Transformer for gesture classification.
    Input:  (batch, seq_len=30, features=225)   [75 landmarks × 3 coords]
    Output: (batch, num_classes)
    """
    def __init__(self, input_dim: int = 225, num_classes: int = 30,
                 seq_len: int = 30, d_model: int = 256,
                 nhead: int = 4, num_layers: int = 3, dropout: float = 0.5):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_embed  = nn.Embedding(seq_len, d_model)
        encoder_layer   = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=512, dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier  = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, _ = x.shape
        positions = torch.arange(T, device=x.device).unsqueeze(0)
        x = self.input_proj(x) + self.pos_embed(positions)
        x = self.transformer(x)
        x = x.mean(dim=1)          # global average pool over time
        return self.classifier(x)


# ─── Keypoint Utilities ───────────────────────────────────────────────────────

def normalize_and_approximate_keypoints(keypoints_225: np.ndarray) -> np.ndarray:
    """
    Normalizes a 225-dim keypoint array (63 left hand, 63 right hand, 99 pose)
    by centering relative to the pose nose, and interpolating missing hands from pose.
    Forces Z=0 to avoid extreme depth inconsistency between training and inference.
    """
    kp = keypoints_225.copy().reshape(-1, 3)
    
    pose = kp[42:75] # 33 points
    if np.all(pose == 0):
        return keypoints_225
        
    nose = pose[0].copy() 
    l_shoulder = pose[11]
    r_shoulder = pose[12]
    
    # Use 2D distance for robust scaling
    shoulder_width = np.linalg.norm(l_shoulder[:2] - r_shoulder[:2])
    scale = shoulder_width if shoulder_width > 0.05 else 1.0
    
    # Left hand approximation
    lh = kp[0:21]
    if np.all(lh == 0):
        l_wrist = pose[15]
        if not np.all(l_wrist == 0):
            kp[0:21] = l_wrist 
            
    # Right hand approximation
    rh = kp[21:42]
    if np.all(rh == 0):
        r_wrist = pose[16]
        if not np.all(r_wrist == 0):
            kp[21:42] = r_wrist
            
    # Spatial Normalization (center and scale in 2D, drop 3D depth)
    for i in range(75):
        if not (kp[i, 0] == 0 and kp[i, 1] == 0):
            kp[i, 0] = (kp[i, 0] - nose[0]) / scale
            kp[i, 1] = (kp[i, 1] - nose[1]) / scale
            kp[i, 2] = 0.0  # Erase Z coordinate
            
    return kp.flatten()


def extract_keypoints(results) -> tuple:
    """
    Extract 75 landmarks from MediaPipe Holistic results.
    Returns:
        keypoints: flat array of shape (225,)
        hand_detected: True if at least one hand was found
    """
    lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten() \
         if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten() \
         if results.right_hand_landmarks else np.zeros(21 * 3)
    pose = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]).flatten() \
           if results.pose_landmarks else np.zeros(33 * 3)

    hand_detected = results.left_hand_landmarks is not None or results.right_hand_landmarks is not None
    
    # Fallback: if detailed hands are lost (e.g. resting on chest for 'sorry'/'please'), check if wrists are raised
    if not hand_detected and results.pose_landmarks:
        # 15: left_wrist, 16: right_wrist, 23: left_hip, 24: right_hip
        lw_y = results.pose_landmarks.landmark[15].y
        rw_y = results.pose_landmarks.landmark[16].y
        lh_y = results.pose_landmarks.landmark[23].y
        rh_y = results.pose_landmarks.landmark[24].y
        # In MediaPipe, y increases downwards. If wrist_y < hip_y, hand is raised above the hip.
        if lw_y < lh_y or rw_y < rh_y:
            hand_detected = True

    raw_keypoints = np.concatenate([lh, rh, pose])
    normalized_keypoints = normalize_and_approximate_keypoints(raw_keypoints)

    return normalized_keypoints, hand_detected   # (225,), bool


# ─── Mode Class ───────────────────────────────────────────────────────────────

class SignLanguageMode(BaseMode):
    SEQ_LEN      = 30       # frames per gesture window
    CONF_THRESH  = 0.75     # minimum confidence to display prediction
    HAND_RATIO   = 0.40     # require hands in 40% of frames before classifying

    def __init__(self, tts: TTSEngine,
                 model_path: str = "C:/Users/souri/OneDrive/Desktop/sensai/models/saved/sign_transformer.pt",
                 labels_path: str = "C:/Users/souri/OneDrive/Desktop/sensai/data/isl_dataset/labels.json"):
        super().__init__(tts)
        self.mp_holistic  = mp.solutions.holistic
        self.mp_draw      = mp.solutions.drawing_utils
        self.holistic     = self.mp_holistic.Holistic(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        # Sliding window of keypoint sequences + hand-detection flags
        self.sequence: deque = deque(maxlen=self.SEQ_LEN)
        self.hand_flags: deque = deque(maxlen=self.SEQ_LEN)
        self.sentence: list  = []
        self.last_spoken_time = 0
        self.prediction_buffer: deque = deque(maxlen=15)
        self.labels = ["hello", "no", "yes"]
        if os.path.exists(labels_path):
            try:
                with open(labels_path) as f:
                    self.labels = json.load(f)
            except Exception:
                pass

        # Load trained model
        self.model  = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[SensAI] Model path exists: {os.path.exists(model_path)}")
        print(f"[SensAI] Labels loaded: {len(self.labels)} -> {self.labels}")
        if os.path.exists(model_path) and self.labels:
            self.model = SignTransformer(
                input_dim=225, num_classes=len(self.labels)
            ).to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.model.eval()
            print(f"[SensAI] Model loaded successfully on {self.device}")
        else:
            print(f"[SensAI] WARNING: Model NOT loaded!")

    def get_mode_name(self) -> str:
        return "Sign Language → Speech"

    def process_frame(self, frame: np.ndarray) -> dict:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        annotated = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw landmarks
        self.mp_draw.draw_landmarks(annotated, results.left_hand_landmarks,
                                    self.mp_holistic.HAND_CONNECTIONS)
        self.mp_draw.draw_landmarks(annotated, results.right_hand_landmarks,
                                    self.mp_holistic.HAND_CONNECTIONS)
        self.mp_draw.draw_landmarks(annotated, results.pose_landmarks,
                                    self.mp_holistic.POSE_CONNECTIONS)

        keypoints, hand_detected = extract_keypoints(results)
        self.sequence.append(keypoints)
        self.hand_flags.append(hand_detected)

        confidence = 0.0
        # Check: buffer full, model loaded, AND enough frames have hands
        hand_ratio = sum(self.hand_flags) / len(self.hand_flags) if self.hand_flags else 0
        buffer_ready = len(self.sequence) == self.SEQ_LEN and self.model is not None
        hands_present = hand_ratio >= self.HAND_RATIO

        if buffer_ready and hands_present:
            seq_tensor = torch.tensor(
                np.array(self.sequence), dtype=torch.float32
            ).unsqueeze(0).to(self.device)   # (1, 30, 225)

            with torch.no_grad():
                logits = self.model(seq_tensor)
                probs  = torch.softmax(logits, dim=-1)
                conf, idx = probs.max(dim=-1)
                confidence = conf.item()
                idx        = idx.item()
                print(f"DEBUG: AI guessed index {idx} with confidence {confidence:.4f}")
                
                word = self.labels[idx] if self.labels else ""
                
                # Prediction smoothing: use a rolling buffer instead of strict clearing
                if confidence >= self.CONF_THRESH and word:
                    self.prediction_buffer.append(word)
                else:
                    self.prediction_buffer.append("")
                    
                # Ensure 4 consecutive frames of the SAME word for responsive real-time recognition
                recent_preds = [w for w in list(self.prediction_buffer)[-4:] if w]
                if len(recent_preds) == 4 and len(set(recent_preds)) == 1:
                    consistent_word = recent_preds[0]
                    current_time = time.time()

                    # Only add a new word if 2.0 seconds have passed and it differs
                    if (current_time - self.last_spoken_time) > 2.0:
                        if not self.sentence or self.sentence[-1] != consistent_word:
                            self.sentence.append(consistent_word)
                            if len(self.sentence) > 8:
                                self.sentence.pop(0)

                            # Automatically convert prediction into speech using Text-to-Speech
                            threading.Thread(target=self.speak_gesture, args=(consistent_word,), daemon=True).start()

                        # Reset the timer whenever threshold is met
                        self.last_spoken_time = current_time
                        self.prediction_buffer.clear() # Clear buffer after registering

        # Always show the full sentence built so far
        prediction_text = " ".join(self.sentence) if self.sentence else ""

        # Flip image for mirror effect in UI BEFORE drawing text
        annotated = cv2.flip(annotated, 1)

        # Overlay sentence on frame
        cv2.rectangle(annotated, (0, 0), (640, 40), (0, 0, 0), -1)
        cv2.putText(annotated, prediction_text or "Waiting for gesture...",
                    (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Confidence bar
        if confidence > 0:
            bar_w = int(confidence * 200)
            cv2.rectangle(annotated, (10, 45), (10 + bar_w, 55), (0, 200, 100), -1)

        return {
            "text":             prediction_text,
            "confidence":       confidence,
            "speak":            bool(prediction_text),
            "annotated_frame":  annotated
        }

    def speak_gesture(self, text: str) -> None:
        """Automatically speak recognized gesture using Text-to-Speech."""
        if text and self.tts:
            try:
                self.tts.speak(text)
            except Exception as e:
                print(f"[speak_gesture error] {e}")

    def clear_sentence(self) -> None:
        self.sentence.clear()
        self.sequence.clear()
        self.hand_flags.clear()

    def cleanup(self) -> None:
        self.holistic.close()
