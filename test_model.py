import torch
import torch.nn as nn
import sys
sys.path.append('.')
from modes.sign_language import SignTransformer


model = SignTransformer(
    input_dim=225,
    num_classes=30,
    seq_len=30,
    d_model=128,
    nhead=4,
    num_layers=3,
    dropout=0.1
)
model.eval()


x = torch.randn(1, 30, 225)
print(f"INPUT shape:              {tuple(x.shape)}")
print(f"  → 1 sample, 30 frames, 225 keypoints per frame\n")


with torch.no_grad():

    
    x_proj = model.input_proj(x)
    print(f"After input_proj:         {tuple(x_proj.shape)}")
    print(f"  → 225 raw keypoints compressed to 128 learned features\n")

    
    B, T, _ = x_proj.shape
    positions = torch.arange(T).unsqueeze(0)
    pos = model.pos_embed(positions)
    x_pos = x_proj + pos
    print(f"After pos_embed (added):  {tuple(x_pos.shape)}")
    print(f"  → Each of 30 frames now has a unique time tag added\n")

    
    x_enc = model.transformer(x_pos)
    print(f"After transformer:        {tuple(x_enc.shape)}")
    print(f"  → Self-attention + FFN applied 3 times, shape unchanged\n")

    
    x_pool = x_enc.mean(dim=1)
    print(f"After mean pool:          {tuple(x_pool.shape)}")
    print(f"  → 30 frames collapsed into 1 summary vector\n")

    
    x_out = model.classifier(x_pool)
    print(f"After classifier:         {tuple(x_out.shape)}")
    print(f"  → 30 scores, one per gesture class\n")

    
    probs = torch.softmax(x_out, dim=-1)
    top_score, top_idx = probs.max(dim=-1)
    print(f"Predicted class index:    {top_idx.item()}")
    print(f"Confidence:               {top_score.item():.2%}")
    print(f"  → Random input = ~3.3% (1/30 chance) ← expected\n")


total   = sum(p.numel() for p in model.parameters())
trained = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters:         {total:,}")
print(f"Trainable parameters:     {trained:,}")
print(f"  → All parameters train from scratch on your ISL dataset")

import torch, sys
sys.path.append('.')
from modes.sign_language import SignTransformer

model = SignTransformer(225, 30, 30, 128, 4, 3, 0.1)

print(f"\n{'Layer':<35} {'Parameters':>12}")
print("-" * 50)
for name, param in model.named_parameters():
    print(f"{name:<35} {param.numel():>12,}")
print("-" * 50)
total = sum(p.numel() for p in model.parameters())
print(f"{'TOTAL':<35} {total:>12,}")

