"""
Quick diagnostic script for sign language detection pipeline.
Tests each component independently to find the failure point.
"""
import os, sys, json
import numpy as np
import torch
sys.path.append('.')

MODEL_PATH  = "models/saved/sign_transformer.pt"
LABELS_PATH = "data/isl_dataset/labels.json"
DATA_PATH   = "data/isl_dataset"

print("=" * 60)
print("SensAI Sign Language — Diagnostic Report")
print("=" * 60)

# ── Step 1: Check labels ──
print("\n[1] Labels")
if os.path.exists(LABELS_PATH):
    with open(LABELS_PATH) as f:
        labels = json.load(f)
    print(f"    ✓ Loaded {len(labels)} labels: {labels}")
else:
    print(f"    ✗ labels.json NOT FOUND at {LABELS_PATH}")
    sys.exit(1)

# ── Step 2: Check dataset ──
print("\n[2] Dataset")
for gesture in labels:
    gdir = os.path.join(DATA_PATH, gesture)
    if not os.path.isdir(gdir):
        print(f"    ✗ Missing gesture folder: {gdir}")
        continue
    seqs = [d for d in os.listdir(gdir) if os.path.isdir(os.path.join(gdir, d))]
    # Check first sequence for frame count
    if seqs:
        first_seq = os.path.join(gdir, seqs[0])
        npy_files = [f for f in os.listdir(first_seq) if f.endswith('.npy')]
        # Load one to check shape
        if npy_files:
            sample = np.load(os.path.join(first_seq, npy_files[0]))
            print(f"    '{gesture}': {len(seqs)} sequences, sample shape={sample.shape}")
        else:
            print(f"    '{gesture}': {len(seqs)} sequences, but NO .npy files in first seq!")
    else:
        print(f"    '{gesture}': folder exists but 0 sequences")

# ── Step 3: Load model ──
print("\n[3] Model")
from modes.sign_language import SignTransformer
try:
    model = SignTransformer(input_dim=225, num_classes=len(labels))
    state = torch.load(MODEL_PATH, map_location='cpu')
    
    # Check if num_classes in checkpoint matches labels
    # The classifier head weight shape reveals the num_classes
    classifier_weight = state.get('classifier.1.weight')
    if classifier_weight is not None:
        saved_num_classes = classifier_weight.shape[0]
        print(f"    Model was trained for {saved_num_classes} classes")
        print(f"    Labels file has {len(labels)} classes")
        if saved_num_classes != len(labels):
            print(f"    ✗ MISMATCH! Model has {saved_num_classes} classes but labels.json has {len(labels)}.")
            print(f"      You need to RE-TRAIN the model: python utils/train_sign_model.py")
        else:
            print(f"    ✓ Class count matches")
    
    model.load_state_dict(state)
    model.eval()
    print(f"    ✓ Model loaded successfully")
except Exception as e:
    print(f"    ✗ Failed to load model: {e}")
    sys.exit(1)

# ── Step 4: Test inference with real data ──
print("\n[4] Inference test (using real dataset sequences)")
for gesture_idx, gesture in enumerate(labels):
    gdir = os.path.join(DATA_PATH, gesture)
    seqs = sorted([d for d in os.listdir(gdir) if os.path.isdir(os.path.join(gdir, d))])
    if not seqs:
        continue
    # Load first sequence
    seq_path = os.path.join(gdir, seqs[0])
    frames = []
    for i in range(30):
        npy = os.path.join(seq_path, f"{i}.npy")
        frames.append(np.load(npy) if os.path.exists(npy) else np.zeros(225))
    
    seq_tensor = torch.tensor(np.array(frames), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        logits = model(seq_tensor)
        probs = torch.softmax(logits, dim=-1)
        conf, pred_idx = probs.max(dim=-1)
        conf = conf.item()
        pred_idx = pred_idx.item()
    
    correct = "✓" if pred_idx == gesture_idx else "✗"
    print(f"    {correct} Gesture '{gesture}' → predicted '{labels[pred_idx]}' "
          f"(confidence: {conf:.2%})")

# ── Step 5: Test with random noise (should be low confidence) ──
print("\n[5] Noise test (random input — should show low confidence)")
noise = torch.randn(1, 30, 225)
with torch.no_grad():
    logits = model(noise)
    probs = torch.softmax(logits, dim=-1)
    conf, pred_idx = probs.max(dim=-1)
print(f"    Random noise → '{labels[pred_idx.item()]}' "
      f"(confidence: {conf.item():.2%})")

print("\n" + "=" * 60)
print("Diagnostic complete.")
print("=" * 60)
