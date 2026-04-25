import os, json, sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
sys.path.append('.')
from modes.sign_language import SignTransformer

DATA_PATH  = "data/isl_dataset"
EPOCHS     = 5       
BATCH_SIZE = 32
LR         = 1e-3
DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ISLDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
    def __len__(self): return len(self.X)
    def __getitem__(self, i): return self.X[i], self.y[i]


with open(os.path.join(DATA_PATH, "labels.json")) as f:
    labels = json.load(f)
print(f"Labels loaded: {len(labels)} gestures")

X, y = [], []
for idx, gesture in enumerate(labels):
    gdir = os.path.join(DATA_PATH, gesture)
    for seq in sorted(os.listdir(gdir)):
        sdir = os.path.join(gdir, seq)
        if not os.path.isdir(sdir): continue
        frames = [np.load(os.path.join(sdir, f"{i}.npy"))
                  if os.path.exists(os.path.join(sdir, f"{i}.npy"))
                  else np.zeros(225) for i in range(30)]
        X.append(frames); y.append(idx)

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int64)
print(f"Dataset loaded: X={X.shape}, y={y.shape}")

X_tr, X_v, y_tr, y_v = train_test_split(X, y, test_size=0.2,
                                          stratify=y, random_state=42)
train_dl = DataLoader(ISLDataset(X_tr,y_tr), batch_size=BATCH_SIZE, shuffle=True)
val_dl   = DataLoader(ISLDataset(X_v, y_v),  batch_size=BATCH_SIZE)

model     = SignTransformer(225, len(labels)).to(DEVICE)
optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
criterion = nn.CrossEntropyLoss()

print(f"\nTraining on: {DEVICE}")
print(f"{'Epoch':>6} {'Train Loss':>12} {'Train Acc':>10} {'Val Acc':>10}")
print("-" * 44)

for epoch in range(1, EPOCHS+1):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for xb, yb in train_dl:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        optimizer.zero_grad()
        out  = model(xb)
        loss = criterion(out, yb)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += loss.item()
        correct    += (out.argmax(1)==yb).sum().item()
        total      += len(yb)

    model.eval()
    vc, vt = 0, 0
    with torch.no_grad():
        for xb, yb in val_dl:
            preds = model(xb.to(DEVICE)).argmax(1)
            vc   += (preds==yb.to(DEVICE)).sum().item()
            vt   += len(yb)

    tr_acc = correct/total*100
    vl_acc = vc/vt*100
    print(f"{epoch:>6}   {total_loss/len(train_dl):>10.4f}   "
          f"{tr_acc:>8.1f}%   {vl_acc:>8.1f}%")

print("\n✓ Mini training test complete — pipeline works!")