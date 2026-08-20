"""
utils/train_sign_model.py
Train the SignTransformer on your collected ISL dataset.
Run AFTER collect_dataset.py.

Usage:
    python utils/train_sign_model.py

IMPORTANT COLAB INSTRUCTION ("Clean Slate" Strategy):
If you are running this in Google Colab, make sure to wipe any old dataset before uploading a new one to prevent 'Folder Ghosts'.
Run this cell in Colab BEFORE unzipping your dataset:
!rm -rf data/isl_dataset
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tqdm import tqdm
import sys
sys.path.append('.')
from modes.sign_language import SignTransformer, normalize_and_approximate_keypoints

# ── Config ────────────────────────────────────────────────────────────────────
DATA_PATH   = "data/isl_dataset"
MODEL_PATH  = "models/saved/sign_transformer.pt"
EPOCHS      = 50
BATCH_SIZE  = 32
LR          = 1e-3
SEQ_LEN     = 30
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ── Dataset ───────────────────────────────────────────────────────────────────

class ISLDataset(Dataset):
    def __init__(self, sequences, labels):
        self.X = torch.tensor(sequences, dtype=torch.float32)
        self.y = torch.tensor(labels,    dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def load_data(data_path: str, labels: list) -> tuple:
    X, y = [], []
    for label_idx, gesture in enumerate(labels):
        gesture_dir = os.path.join(data_path, gesture)
        if not os.path.isdir(gesture_dir):
            continue
        for seq_dir in sorted(os.listdir(gesture_dir)):
            seq_path = os.path.join(gesture_dir, seq_dir)
            if not os.path.isdir(seq_path):
                continue
            frames = []
            for i in range(SEQ_LEN):
                npy = os.path.join(seq_path, f"{i}.npy")
                frame_data = np.load(npy) if os.path.exists(npy) else np.zeros(225)
                frame_data = normalize_and_approximate_keypoints(frame_data)
                frames.append(frame_data)
            X.append(frames)
            y.append(label_idx)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


# ── Training Loop ─────────────────────────────────────────────────────────────

def train():
    os.makedirs("models/saved", exist_ok=True)

    # Load labels
    labels_path = os.path.join(DATA_PATH, "labels.json")
    with open(labels_path) as f:
        labels = json.load(f)
    print(f"[Train] {len(labels)} gesture classes: {labels}")

    # Load data
    print("[Train] Loading dataset...")
    X, y = load_data(DATA_PATH, labels)
    print(f"[Train] Dataset shape: X={X.shape}, y={y.shape}")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    train_loader = DataLoader(ISLDataset(X_train, y_train),
                              batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(ISLDataset(X_val,   y_val),
                              batch_size=BATCH_SIZE)

    # Model
    model     = SignTransformer(input_dim=225, num_classes=len(labels)).to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    print(f"[Train] Training on {DEVICE} for {EPOCHS} epochs...\n")

    for epoch in range(1, EPOCHS + 1):
        # ── Train ──
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        for X_batch, y_batch in tqdm(train_loader, desc=f"Epoch {epoch:3d}", leave=False):
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            logits = model(X_batch)
            loss   = criterion(logits, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()
            correct    += (logits.argmax(1) == y_batch).sum().item()
            total      += len(y_batch)
        scheduler.step()

        train_acc = correct / total * 100

        # ── Validate ──
        model.eval()
        val_correct, val_total = 0, 0
        all_preds, all_true    = [], []
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                preds = model(X_batch).argmax(1)
                val_correct += (preds == y_batch).sum().item()
                val_total   += len(y_batch)
                all_preds.extend(preds.cpu().numpy())
                all_true.extend(y_batch.cpu().numpy())
        val_acc = val_correct / val_total * 100

        print(f"Epoch {epoch:3d} | Loss: {train_loss/len(train_loader):.4f} "
              f"| Train: {train_acc:.1f}% | Val: {val_acc:.1f}%")

        # Save best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"           [OK] Saved best model ({val_acc:.1f}%)")

    print(f"\n[Done] Best validation accuracy: {best_val_acc:.1f}%")
    print(f"[Done] Model saved to {MODEL_PATH}")

    # Final classification report
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    all_preds, all_true = [], []
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            preds = model(X_batch.to(DEVICE)).argmax(1)
            all_preds.extend(preds.cpu().numpy())
            all_true.extend(y_batch.numpy())
    print("\n" + classification_report(all_true, all_preds, target_names=labels))


if __name__ == "__main__":
    train()
