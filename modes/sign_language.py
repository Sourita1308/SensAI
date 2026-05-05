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
                 seq_len: int = 30, d_model: int = 128,
                 nhead: int = 4, num_layers: int = 3, dropout: float = 0.1):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_embed  = nn.Embedding(seq_len, d_model)
        encoder_layer   = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=256, dropout=dropout, batch_first=True
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

def extract_keypoints(results) -> np.ndarray:
    """
    Extract 75 landmarks from MediaPipe Holistic results.
    Returns flat array of shape (225,): 21 left hand + 21 right hand + 33 pose = 75 pts × 3
    """
    lh = np.array([[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark]).flatten() \
         if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark]).flatten() \
         if results.right_hand_landmarks else np.zeros(21 * 3)
    pose = np.array([[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]).flatten() \
           if results.pose_landmarks else np.zeros(33 * 3)
    return np.concatenate([lh, rh, pose])   # (225,)


# ─── Mode Class ───────────────────────────────────────────────────────────────

class SignLanguageMode(BaseMode):
    SEQ_LEN      = 30       # frames per gesture window
    CONF_THRESH  = 0.75     # minimum confidence to display prediction

    def __init__(self, tts: TTSEngine,
                 model_path: str = "C:/Users/souri/OneDrive/Desktop/sensai/models/sensai_transformer.pth",
                 labels_path: str = "C:/Users/souri/OneDrive/Desktop/sensai/data/isl_dataset/labels.json"):
        super().__init__(tts)
        self.mp_holistic  = mp.solutions.holistic
        self.mp_draw      = mp.solutions.drawing_utils
        self.holistic     = self.mp_holistic.Holistic(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

        # Sliding window of keypoint sequences
        self.sequence: deque = deque(maxlen=self.SEQ_LEN)
        self.sentence: list  = []

        # Load labels
        self.labels: list[str] = []
        if os.path.exists(labels_path):
            with open(labels_path) as f:
                self.labels = json.load(f)

        # Load trained model
        self.model  = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"DEBUG 1: Does brain exist? {os.path.exists(model_path)}")
        print(f"DEBUG 2: How many words loaded? {len(self.labels)}")
        if os.path.exists(model_path) and self.labels:
            self.model = SignTransformer(
                input_dim=225, num_classes=len(self.labels)
            ).to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            self.model.eval()

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

        keypoints = extract_keypoints(results)
        self.sequence.append(keypoints)

        prediction_text = ""
        confidence      = 0.0
        print(f"Bucket status: {len(self.sequence)} / {self.SEQ_LEN}")
        if len(self.sequence) == self.SEQ_LEN and self.model is not None:
            seq_tensor = torch.tensor(
                np.array(self.sequence), dtype=torch.float32
            ).unsqueeze(0).to(self.device)   # (1, 30, 225)

            with torch.no_grad():
                logits = self.model(seq_tensor)
                probs  = torch.softmax(logits, dim=-1)
                confidence, idx = probs.max(dim=-1)
                confidence = confidence.item()
                idx        = idx.item()
                print(f"DEBUG: AI guessed index {idx} with confidence {confidence:.4f}")
            if confidence >= self.CONF_THRESH and self.labels:
                word = self.labels[idx]
                if not self.sentence or self.sentence[-1] != word:
                    self.sentence.append(word)
                    if len(self.sentence) > 8:
                        self.sentence.pop(0)
                prediction_text = " ".join(self.sentence)
                threading.Thread(target=self.maybe_speak, args=(word,)).start()

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

    def clear_sentence(self) -> None:
        self.sentence.clear()
        self.sequence.clear()

    def cleanup(self) -> None:
        self.holistic.close()
