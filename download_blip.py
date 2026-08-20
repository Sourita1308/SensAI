# download_blip.py — run this, leave downloading while you read ahead
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

MODEL_ID = "Salesforce/blip-image-captioning-base"
print(f"Downloading/Loading {MODEL_ID}...")
print("Takes 15-30 min first time (~1 GB, unless already cached)\n")

processor = BlipProcessor.from_pretrained(MODEL_ID)
print("Processor downloaded [OK]")

model = BlipForConditionalGeneration.from_pretrained(
    MODEL_ID, torch_dtype=torch.float32
)
print("Model downloaded [OK]")
total = sum(p.numel() for p in model.parameters())
print(f"Parameters: {total:,}")
print("\nBLIP ready!")
