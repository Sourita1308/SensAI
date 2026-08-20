# SensAI Mode 2 — OCR & TTS Technical Interview Q&A

This document contains the core technical interview questions and answers for **Mode 2: Printed Text → Speech (OCR)** in SensAI.

---

### Q1: How does your OCR pipeline work?
**Answer:**
The image goes through a 4-step preprocessing pipeline before OCR:
1. **Grayscale conversion** (`cv2.cvtColor`)
2. **Noise removal** (`cv2.fastNlMeansDenoising`)
3. **Adaptive thresholding** (`cv2.adaptiveThreshold`)
4. **Deskewing & 2x Scaling** (`cv2.warpAffine` + `cv2.resize`)

> **Key Differentiator:** **Adaptive thresholding** is the critical step — it adjusts the binarization threshold locally for each region, which handles uneven lighting (shadows, phone camera glare) much better than a global threshold. Finally, **Tesseract with `--oem 3 --psm 6`** config extracts text using the LSTM neural network engine.

---

### Q2: Why Tesseract and not Google Vision API?
**Answer:**
Two reasons — **privacy and cost**:
- **Privacy:** Google Vision API sends images to external cloud servers, which is a serious privacy concern when reading medical prescriptions, bank statements, or personal mail. Tesseract runs **entirely on-device with zero data leaving the user's machine**.
- **Cost:** Tesseract is 100% free with **no API quota limits or recurring costs**, which is essential for a real-world accessibility tool used by individuals who cannot afford subscription-based APIs.

---

### Q3: How did you handle multilingual text (English + Bengali)?
**Answer:**
1. **Multilingual Extraction:** We configure Tesseract with `lang='eng+ben'` to evaluate both English and Bengali language models simultaneously.
2. **Intelligent TTS Routing:** After text extraction, we use `langdetect` to identify the dominant language:
   - **English (`en`)** routes to the offline `pyttsx3` (SAPI5) TTS engine for zero latency.
   - **Bengali (`bn`)** routes to `gTTS`, which correctly pronounces Bengali Unicode script and conjunct characters that Windows SAPI5 cannot articulate.

---

### Q4: What is `--oem 3 --psm 6` in Tesseract?
**Answer:**
- **`--oem 3` (OCR Engine Mode 3):** Means *"use both Legacy and LSTM OCR engines"*. The combined approach yields higher character accuracy than either mode alone.
- **`--psm 6` (Page Segmentation Mode 6):** Means *"assume a single uniform block of text"*. It instructs Tesseract not to look for multi-column layouts or tables, but to read linearly from left to right, top to bottom — ideal for photos of textbook pages, signs, and labels.

---

### Q5: How accurate is your OCR?
**Answer:**
- **Printed English (good lighting):** **90%+ word accuracy**.
- **Printed Bengali:** **60–75% word accuracy** because Bengali script is structurally more complex with joined conjunct characters and vowel markers (matras).
- **Handwriting:** **~50% word accuracy** because Tesseract is trained predominantly on printed typography.
- **Mitigation Strategy:** The interface displays the extracted text visually on the dashboard so the user can verify it before audio playback, allowing them to re-capture if image quality or lighting was poor.
