# SensAI Mode 4 — Viva & Technical Interview Q&A Reference
**Topic:** Scene Description → Speech (Salesforce BLIP-2 / BLIP-base)

---

### Q1: What model powers your scene description?
**A:** **Salesforce BLIP** (Bootstrapped Language-Image Pretraining).
- **Architecture:** It uses a **Vision Transformer (ViT)** encoder that splits the image into $16 \times 16$ pixel patches and encodes them into visual tokens.
- **Bridge & Decoder:** A cross-attention module bridges those tokens to a **GPT-style text decoder** that generates the caption one word at a time, conditioned on both the image and previous words.
- **Size & Privacy:** The base model (`Salesforce/blip-image-captioning-base`) has **247 million parameters** and runs **100% locally on CPU** without any external API calls.

---

### Q2: How is this different from a simple image classifier?
**A:** A classifier picks from a fixed list of labels (e.g., `"cat"`, `"dog"`, `"car"`). BLIP **generates free-form natural language** — it can describe a scene as *"a man reading a newspaper on a bench near a fountain"* which no fixed vocabulary could capture. This makes it dramatically more useful for visually impaired users who need rich contextual descriptions, not just isolated object names.

---

### Q3: Why not use GPT-4V or Google Vision API?
**A:** Three critical reasons: **Privacy, Cost, and Offline Capability**.
1. **Privacy:** Cloud APIs require uploading user photos to external servers, which is a significant privacy risk for personal, household, or medical images.
2. **Cost:** Commercial APIs charge per request, making them unsustainable for a free accessibility tool.
3. **Offline Capability:** BLIP runs entirely on-device — weights are cached locally after one download, and it works without any internet connection (vital for users in low-connectivity areas of India).

---

### Q4: What are the limitations of Mode 4?
**A:** There are three main limitations to be transparent about:
1. **CPU Speed (4–8 seconds):** Inference on laptop CPUs takes 4–8 seconds, which is fine for uploaded images but too slow for instantaneous 60 fps real-time description. (We mitigate this in live camera mode using `FRAME_SKIP = 60` so it describes the scene every 2 seconds).
2. **Struggles with Text in Images:** It describes the physical layout (e.g., *"a sign on a wall"*) but does not reliably read the printed words. (**Solution:** We built Mode 2 — OCR — specifically for reading text!).
3. **Western Training Bias:** Since BLIP was trained predominantly on Western image datasets, it may produce culturally generic descriptions for Indian items — for example, describing a *dhoti* as *"a white cloth wrapped around the waist"* rather than naming it correctly.

---

### Q5: How does `num_beams` affect caption quality and speed?
**A:** **Beam search** keeps the top $N$ candidate sequences at each generation step instead of greedily picking just one word.
- With `num_beams=4`, the decoder explores 4 parallel caption hypotheses simultaneously and returns the highest-scoring complete sentence.
- More beams = slightly better grammatical structure but slower inference.
- **Our Optimization:** We use `num_beams=3` as an optimal balance — **~30% faster** than 4 beams with negligible quality difference for short captions under 40 tokens.
