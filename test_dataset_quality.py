import numpy as np
import os
import json

DATA_PATH = "data/isl_dataset"

with open(os.path.join(DATA_PATH, "labels.json")) as f:
    labels = json.load(f)

print(f"{'Gesture':<15} {'Sequences':>10} {'Avg non-zero %':>16} {'Status':>10}")
print("-" * 55)

for gesture in labels:
    gesture_dir = os.path.join(DATA_PATH, gesture)
    seq_dirs = [d for d in os.listdir(gesture_dir)
                if os.path.isdir(os.path.join(gesture_dir, d))]

    nonzero_pcts = []
    for seq in seq_dirs:
        frames = []
        for i in range(30):
            fp = os.path.join(gesture_dir, seq, f"{i}.npy")
            if os.path.exists(fp):
                frames.append(np.load(fp))
        if frames:
            arr = np.array(frames)
            pct = np.count_nonzero(arr) / arr.size * 100
            nonzero_pcts.append(pct)

    avg_pct = np.mean(nonzero_pcts) if nonzero_pcts else 0
    status = "✓ Good" if avg_pct > 40 else "⚠ Re-record"
    print(f"{gesture:<15} {len(seq_dirs):>10} {avg_pct:>15.1f}% {status:>10}")