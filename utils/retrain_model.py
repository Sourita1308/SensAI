"""
utils/retrain_model.py
Retrain the SignTransformer with data augmentation to combat overfitting.

Problem: The original model gives 94%+ confidence on random noise (massive overfit).
Solution: Add noise/scale/shift augmentation + dropout + reduced model capacity.

Usage:
    python utils/retrain_model.py

IMPORTANT COLAB INSTRUCTION ("Clean Slate" Strategy):
If you are running this in Google Colab, make sure to wipe any old dataset before uploading a new one to prevent 'Folder Ghosts'.
Run this cell in Colab BEFORE unzipping your dataset:
!rm -rf data/isl_dataset
"""

import os
import sys
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

sys.path.append('.')

# -- Config -------------------------------------------------------------------
DATA_PATH   = "data/isl_dataset"
MODEL_PATH  = "models/saved/sign_transformer.pt"
EPOCHS      = 80
BATCH_SIZE  = 16
LR          = 5e-4
SEQ_LEN     = 30
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -- Augmented Dataset --------------------------------------------------------

class AugmentedISLDataset(Dataset):
    """Dataset with on-the-fly augmentation to prevent overfitting."""

    def __init__(self, sequences, labels, augment=True):
        self.X = torch.tensor(sequences, dtype=torch.float32)
        self.y = torch.tensor(labels, dtype=torch.long)
        self.augment = augment

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = self.X[idx].clone()
        if self.augment:
            x = self._apply_augmentation(x)
        return x, self.y[idx]

    def _apply_augmentation(self, x):
        # 1. Gaussian noise (simulates hand jitter — tuned down to preserve subtle finger movements)
        if torch.rand(1).item() < 0.7:
            noise = torch.randn_like(x) * 0.008
            x = x + noise

        # 2. Random scaling (simulates distance from camera)
        if torch.rand(1).item() < 0.5:
            scale = 0.85 + torch.rand(1).item() * 0.30  # 0.85 to 1.15
            x = x * scale

        # 3. Temporal shift (slide the sequence by a few frames)
        if torch.rand(1).item() < 0.5:
            shift = int(torch.randint(-3, 4, (1,)).item())
            if shift > 0:
                pad = x[-1:].repeat(shift, 1)
                x = torch.cat([x[shift:], pad], dim=0)
            elif shift < 0:
                pad = x[0:1].repeat(-shift, 1)
                x = torch.cat([pad, x[:shift]], dim=0)

        # 5. Coordinate jitter (independent per-landmark noise — tuned down for finger clarity)
        if torch.rand(1).item() < 0.4:
            jitter = torch.randn_like(x) * 0.004
            x = x + jitter

        return x


# -- Improved Transformer Model -----------------------------------------------

class SignTransformerV2(nn.Module):
    """
    Smaller, more regularized transformer for small datasets.
    Compared to original: fewer layers, more dropout, label smoothing.
    """
    def __init__(self, input_dim=225, num_classes=3,
                 seq_len=30, d_model=64, nhead=4,
                 num_layers=2, dropout=0.3):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_embed  = nn.Embedding(seq_len, d_model)
        self.input_drop = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=128, dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(dropout),
            nn.Linear(d_model, num_classes)
        )

    def forward(self, x):
        B, T, _ = x.shape
        positions = torch.arange(T, device=x.device).unsqueeze(0)
        x = self.input_proj(x) + self.pos_embed(positions)
        x = self.input_drop(x)
        x = self.transformer(x)
        x = x.mean(dim=1)  # global average pool
        return self.classifier(x)


# -- Data Loading --------------------------------------------------------------

def load_data(data_path, labels):
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
                frames.append(np.load(npy) if os.path.exists(npy) else np.zeros(225))
            X.append(frames)
            y.append(label_idx)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


# -- Training ------------------------------------------------------------------

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

    train_loader = DataLoader(
        AugmentedISLDataset(X_train, y_train, augment=True),
        batch_size=BATCH_SIZE, shuffle=True
    )
    val_loader = DataLoader(
        AugmentedISLDataset(X_val, y_val, augment=False),
        batch_size=BATCH_SIZE
    )

    # Use the SAME architecture as SignTransformer from sign_language.py
    # so it can be loaded with the existing code
    from modes.sign_language import SignTransformer
    model = SignTransformer(input_dim=225, num_classes=len(labels),
                            d_model=256, nhead=4, num_layers=3,
                            dropout=0.5).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=5e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    # Label smoothing helps prevent overconfident predictions
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    best_val_acc = 0.0
    patience = 15
    patience_counter = 0

    print(f"[Train] Training on {DEVICE} for up to {EPOCHS} epochs...")
    print(f"[Train] Using: augmentation + label_smoothing=0.1 + weight_decay=5e-3 + dropout=0.3")
    print(f"{'Epoch':>6} {'Train Loss':>12} {'Train Acc':>10} {'Val Acc':>10}")
    print("-" * 44)

    for epoch in range(1, EPOCHS + 1):
        # -- Train --
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()
            correct += (logits.argmax(1) == y_batch).sum().item()
            total += len(y_batch)
        scheduler.step()

        train_acc = correct / total * 100

        # -- Validate --
        model.eval()
        val_correct, val_total = 0, 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
                preds = model(X_batch).argmax(1)
                val_correct += (preds == y_batch).sum().item()
                val_total += len(y_batch)
        val_acc = val_correct / val_total * 100

        print(f"{epoch:>6}   {train_loss/len(train_loader):>10.4f}   "
              f"{train_acc:>8.1f}%   {val_acc:>8.1f}%")

        # Save best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_PATH)
            print(f"           >>> Saved best model ({val_acc:.1f}%)")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n[Early Stop] No improvement for {patience} epochs. Stopping.")
                break

    print(f"\n[Done] Best validation accuracy: {best_val_acc:.1f}%")
    print(f"[Done] Model saved to {MODEL_PATH}")

    # -- Final test: noise rejection --
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    with torch.no_grad():
        noise = torch.randn(1, 30, 225).to(DEVICE)
        probs = torch.softmax(model(noise), dim=-1)
        conf, idx = probs.max(dim=-1)
        print(f"\n[Noise Test] Random input -> '{labels[idx.item()]}' "
              f"(confidence: {conf.item():.2%})")
        if conf.item() > 0.8:
            print("[WARNING] Model may still be overfit. Consider collecting more data.")
        else:
            print("[OK] Noise confidence is reasonable.")


if __name__ == "__main__":
    train()
