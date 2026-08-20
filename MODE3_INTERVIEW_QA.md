# SensAI Mode 3 — Facial Emotion Detection Technical Interview Q&A

This document contains the 5 core technical interview questions and answers for **Mode 3: Facial Emotion → Spoken Feedback (Autism / Therapy Support)** in SensAI.

---

### Q1: What model powers your emotion detection?
**Answer:**
> "I used **DeepFace** as the inference wrapper, which internally uses a **CNN trained on FER-2013** — a dataset of 35,887 facial images labelled with 7 emotions. The model crops and resizes the detected face to 48×48 grayscale, then runs the emotion CNN to produce 7 probability scores. I run inference every 5 frames using a background thread to keep the webcam feed smooth."

---

### Q2: Why is this useful for autism support?
**Answer:**
> "Many autistic individuals have **alexithymia** — difficulty identifying and describing their own emotions. A real-time mirror that names the emotion out loud serves as an external emotional feedback loop. The contextual phrasing I used — *'You might be feeling frustrated'* instead of *'You look angry'* — is intentionally softer and less alarming, which is an important consideration for this user group."

---

### Q3: What are the limitations of your emotion detector?
**Answer:**
> "Three main limitations. First, **FER-2013 is predominantly Western faces** — the model may be less accurate on South Asian facial expressions. Second, it only detects **basic emotions from static expressions** — complex emotions like contempt, pride or embarrassment aren't in the model. Third, **poor lighting significantly degrades accuracy** — the 48×48 input means subtle facial details are lost in dim conditions. For production I'd fine-tune on a diverse Indian face dataset and add a lighting quality check."

---

### Q4: Why did you use threading for DeepFace inference?
**Answer:**
> "DeepFace analysis takes ~300ms per frame on CPU. Without threading it would block the main loop, causing the webcam feed to run at only ~3fps — too choppy for real-time use. Running DeepFace in a **daemon background thread** lets the main loop capture and display frames at full 30fps, while the emotion result updates every 5 frames asynchronously. The user sees smooth video with emotion labels that update ~6 times per second."

---

### Q5: Why a 5-second cooldown before speaking again?
**Answer:**
> "Without a cooldown the system would repeat *'You look happy'* every few seconds — which is **annoying and counterproductive**, especially for an autistic individual who may be sensitive to audio repetition. 5 seconds gives enough time for the message to register without constant interruption. The cooldown also resets when the emotion changes."
