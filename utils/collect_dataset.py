"""
utils/collect_dataset.py
ISL Dataset Collector — records keypoint sequences from your webcam.
Run this BEFORE training to build your own Indian Sign Language dataset.

Usage:
    python utils/collect_dataset.py
"""

import cv2
import numpy as np
import mediapipe as mp
import os
import json
import time
from modes.sign_language import extract_keypoints

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_PATH   = "data/isl_dataset"
GESTURES    = [   # Add your ISL gesture labels here
    "hello", "thankyou", "yes", "no", "help",
    "water", "food", "sorry", "please", "good",
    "bad", "stop", "go", "come", "sit",
    "stand", "eat", "drink", "sleep", "name",
    "what", "where", "how", "who", "when",
    "iloveyou", "fine", "sick", "pain", "doctor"
]
N_SEQUENCES = 40    # videos per gesture
SEQ_LEN     = 30    # frames per video
START_DELAY = 2     # seconds to prepare between gestures

# ── Setup ─────────────────────────────────────────────────────────────────────

def setup_dirs():
    os.makedirs(DATA_PATH, exist_ok=True)
    for g in GESTURES:
        for i in range(N_SEQUENCES):
            os.makedirs(os.path.join(DATA_PATH, g, str(i)), exist_ok=True)
    # Save labels
    with open(os.path.join(DATA_PATH, "labels.json"), "w") as f:
        json.dump(GESTURES, f, indent=2)
    print(f"[Setup] Created dirs for {len(GESTURES)} gestures × {N_SEQUENCES} sequences")


def collect():
    setup_dirs()
    mp_holistic = mp.solutions.holistic
    mp_draw     = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    with mp_holistic.Holistic(min_detection_confidence=0.7,
                               min_tracking_confidence=0.5) as holistic:
        for gesture in GESTURES:
            print(f"\n{'='*50}")
            print(f"Gesture: {gesture.upper()}")
            print(f"{'='*50}")

            for seq_idx in range(N_SEQUENCES):
                # Countdown before each sequence
                for countdown in range(START_DELAY, 0, -1):
                    ret, frame = cap.read()
                    if not ret: break
                    cv2.putText(frame, f"NEXT: {gesture}  [{seq_idx+1}/{N_SEQUENCES}]",
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Starting in {countdown}...",
                                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 100, 255), 3)
                    cv2.imshow("SensAI Dataset Collector", frame)
                    cv2.waitKey(1000)

                # Record SEQ_LEN frames
                for frame_idx in range(SEQ_LEN):
                    ret, frame = cap.read()
                    if not ret: break

                    # MediaPipe processing
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = holistic.process(image)
                    image.flags.writeable = True
                    frame   = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    # Draw landmarks
                    mp_draw.draw_landmarks(frame, results.left_hand_landmarks,
                                           mp_holistic.HAND_CONNECTIONS)
                    mp_draw.draw_landmarks(frame, results.right_hand_landmarks,
                                           mp_holistic.HAND_CONNECTIONS)

                    # HUD
                    cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
                    cv2.putText(frame, f"{gesture}  seq:{seq_idx+1}  frame:{frame_idx+1}/{SEQ_LEN}",
                                (10, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 120), 2)

                    # Progress bar
                    prog = int((frame_idx / SEQ_LEN) * 300)
                    cv2.rectangle(frame, (10, 55), (10 + prog, 65), (0, 180, 255), -1)

                    cv2.imshow("SensAI Dataset Collector", frame)
                    cv2.waitKey(1) & 0xFF

                    # Save keypoints
                    keypoints = extract_keypoints(results)
                    save_path = os.path.join(DATA_PATH, gesture, str(seq_idx), str(frame_idx))
                    np.save(save_path, keypoints)

                if cv2.waitKey(10) & 0xFF == ord("q"):
                    print("Aborted by user.")
                    cap.release()
                    cv2.destroyAllWindows()
                    return

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[Done] Dataset saved to {DATA_PATH}/")
    print(f"Total samples: {len(GESTURES)} gestures × {N_SEQUENCES} sequences × {SEQ_LEN} frames")


if __name__ == "__main__":
    collect()
