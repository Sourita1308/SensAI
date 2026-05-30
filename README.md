<div align="center">
  <img src="https://img.icons8.com/fluency/96/accessibility.png" alt="SensAI Logo" width="100"/>
  
  <h1>♿ SensAI</h1>
  <p><b>Multimodal Accessibility AI System</b></p>

  <!-- Tech Stack Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
    <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
    <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" />
    <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
    <img src="https://img.shields.io/badge/Transformers-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" />
    <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
    <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" />
  </p>

  <!-- GitHub Stats Badges -->
  <p>
    <img src="https://img.shields.io/github/last-commit/Sourita1308/SensAI?style=flat-square&color=blue" alt="Last Commit"/>
    <img src="https://img.shields.io/github/repo-size/Sourita1308/SensAI?style=flat-square" alt="Repo Size"/>
    <img src="https://img.shields.io/github/license/Sourita1308/SensAI?style=flat-square" alt="License"/>
  </p>
</div>

<hr/>

## 🌟 About SensAI
SensAI is a comprehensive **Multimodal Accessibility Assistant** designed to bridge communication and sensory gaps using state-of-the-art AI models. It features a unified dashboard that integrates four major assistive modes, providing real-time text-to-speech, computer vision, and natural language processing capabilities.

Supports **English** and **Bengali**.

## 🛠️ System Architecture

Below is the high-level system architecture outlining the core flow of SensAI:

<div align="center">
  <img src="./architecture.png" alt="SensAI Architecture" width="800" style="border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);"/>
</div>

The application serves four primary modes:
1. **🤟 Sign Language to Speech**: Live keypoint extraction using MediaPipe, classified via PyTorch models to translate Indian Sign Language (ISL) gestures to spoken words.
2. **📖 Printed Text to Speech (OCR)**: Leverages Tesseract OCR and `pyttsx3`/`gTTS` to extract text from images or live camera feeds and read it aloud.
3. **😊 Facial Emotion to Speech**: Uses DeepFace and Keras to detect user emotions in real-time, providing spoken contextual feedback (useful for autism support).
4. **🌍 Scene Description to Speech**: Utilizes Hugging Face Transformers (e.g., BLIP-2) to generate rich, descriptive text of a visual scene and reads it out for visually impaired users.

## 🚀 Getting Started

### Prerequisites
Make sure you have Python installed.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sourita1308/SensAI.git
   cd SensAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 📅 Daily Push Log Table

| Date | Commits / Updates | Author | Status |
| :--- | :--- | :--- | :--- |
| **2026-05-30** | Updated README with modern UI & badges | Sourita1308 | 🟢 Completed |
| **YYYY-MM-DD** | Add your next update here | Sourita1308 | 🟡 In Progress |
| **YYYY-MM-DD** | Example of a future planned update | Sourita1308 | ⚪ Pending |

> **Note**: Update this table daily to keep track of your feature pushes and progress.

## 📊 GitHub Activity
To automatically track daily pushes, below is the real-time GitHub activity graph:
<div align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=Sourita1308&bg_color=0f0f23&color=e0e0ff&line=5C3EE8&point=FFFFFF&area=true&hide_border=true" alt="Sourita1308's Activity Graph"/>
</div>
