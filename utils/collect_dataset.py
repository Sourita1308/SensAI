"""
utils/collect_dataset.py
ISL Dataset Collector — VARIATION MODE (Records folders 40-49)
"""

import sys
import os
# Allow Python to find the 'modes' folder when running from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
import mediapipe as mp
import json
from modes.sign_language import extract_keypoints

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_PATH   = "data/isl_dataset"
GESTURES = [
    # ── Batch A (Core Needs & States) ──
    "water",       # W handshape at chin
    "food",        # fingers to mouth
    "eat",         # fingers bunched to mouth repeatedly
    "drink",       # thumb to mouth, tilt hand like cup
    "sleep",       # hands together, tilt head on them
    "sick",        # middle fingers on forehead + stomach
    "pain",        # index fingers point at each other, twist
    "doctor",      # tap wrist like checking pulse

    # ── Batch B (Commands & Actions) ──
    "help",        # fist on palm, lift up
    "stop",        # flat hand chop down on palm
    "go",          # both index fingers forward
    "come",        # index finger curl toward you
    "sit",         # two fingers sit on other hand
    "stand",       # index + middle fingers pointing up

    # ── Batch C (Interrogatives & Social) ──
    "what",        # fingers spread, shake hand side to side
    "where",       # index finger wag side to side
    "how",         # knuckles together, roll forward
    "who",         # index finger circle near lips
    "when",        # index fingers circle each other
    "name",        # two index fingers tap together
    "sorry",       # fist circle on chest
    "please",      # flat hand circle on chest
    "good",        # flat hand from chin forward
    "bad",         # fingers from chin, flip down
    "fine",        # open hand, thumb on chest tap
    "iloveyou",    # pinky + index + thumb extended (ILY hand)
    "thankyou",    # hand to chin, move forward
    
    # ── Original 3 Gestures ──
    "hello",       # wave hand
    "yes",         # fist nod up-down
    "no",          # index finger wag left-right
]

N_SEQUENCES = 50    # Aiming for 50-100 video sequences per word
SEQ_LEN     = 30    # frames per video
START_DELAY = 2     # seconds to prepare between sequences
SEQ_OFFSET  = 0     # START SAVING AT FOLDER 0 (Adjust if resuming later)

# ── Setup ─────────────────────────────────────────────────────────────────────

def setup_dirs():
    os.makedirs(DATA_PATH, exist_ok=True)
    for g in GESTURES:
        # Adjusted to create folders 40 to 49
        for i in range(SEQ_OFFSET, SEQ_OFFSET + N_SEQUENCES):
            os.makedirs(os.path.join(DATA_PATH, g, str(i)), exist_ok=True)
    # Save labels
    with open(os.path.join(DATA_PATH, "labels.json"), "w") as f:
        json.dump(GESTURES, f, indent=2)
    print(f"[Setup] Created variation dirs (Folders {SEQ_OFFSET} to {SEQ_OFFSET + N_SEQUENCES - 1})")


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
            
            # --- SMART RESUME: Checks the offset folders (40-49) ---
            gesture_complete = True
            for seq_idx in range(SEQ_OFFSET, SEQ_OFFSET + N_SEQUENCES):
                seq_path = os.path.join(DATA_PATH, gesture, str(seq_idx))
                if not os.path.exists(seq_path) or len(os.listdir(seq_path)) < SEQ_LEN:
                    gesture_complete = False
                    break
            
            if gesture_complete:
                print(f"[Smart Resume] Skipping '{gesture.upper()}' variations - Already collected!")
                continue

            print(f"\n{'='*50}")
            print(f"Gesture: {gesture.upper()} (VARIATIONS)")
            print(f"{'='*50}")

            # --- MANUAL PAUSE ---
            while True:
                ret, frame = cap.read()
                if not ret: break
                cv2.putText(frame, f"UP NEXT: {gesture.upper()} (VARIATION)", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
                cv2.putText(frame, "Press SPACEBAR to start", (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Press Q to save and quit", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow("SensAI Dataset Collector", frame)
                
                key = cv2.waitKey(10) & 0xFF
                if key == ord(' '):
                    break
                elif key == ord('q'):
                    print("Aborted by user.")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit(0)

            # --- RECORDING LOOP: Adjusted to use SEQ_OFFSET ---
            for seq_idx in range(SEQ_OFFSET, SEQ_OFFSET + N_SEQUENCES):
                
                seq_path = os.path.join(DATA_PATH, gesture, str(seq_idx))
                if os.path.exists(seq_path) and len(os.listdir(seq_path)) == SEQ_LEN:
                    continue

                for countdown in range(START_DELAY, 0, -1):
                    ret, frame = cap.read()
                    if not ret: break
                    cv2.putText(frame, f"NEXT: {gesture}  [{seq_idx+1}/{SEQ_OFFSET + N_SEQUENCES}]",
                                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(frame, f"Starting in {countdown}...",
                                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 100, 255), 3)
                    cv2.imshow("SensAI Dataset Collector", frame)
                    cv2.waitKey(1000)

                for frame_idx in range(SEQ_LEN):
                    ret, frame = cap.read()
                    if not ret: break

                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = holistic.process(image)
                    image.flags.writeable = True
                    frame   = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    mp_draw.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                    mp_draw.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

                    cv2.rectangle(frame, (0, 0), (640, 50), (0, 0, 0), -1)
                    cv2.putText(frame, f"{gesture}  seq:{seq_idx+1}  frame:{frame_idx+1}/{SEQ_LEN}",
                                (10, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 120), 2)

                    prog = int((frame_idx / SEQ_LEN) * 300)
                    cv2.rectangle(frame, (10, 55), (10 + prog, 65), (0, 180, 255), -1)

                    cv2.imshow("SensAI Dataset Collector", frame)
                    cv2.waitKey(1) & 0xFF

                    keypoints, _ = extract_keypoints(results)
                    save_path = os.path.join(DATA_PATH, gesture, str(seq_idx), str(frame_idx))
                    np.save(save_path, keypoints)

                if cv2.waitKey(10) & 0xFF == ord("q"):
                    print("Aborted by user.")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit(0)

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[Done] Variation Dataset saved to {DATA_PATH}/")

if __name__ == "__main__":
    collect()