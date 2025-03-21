# 🗣️ Real-Time Speech-to-Command (Voice Control App)

<p align="center">
  <img src="https://github.com/user-attachments/assets/c2da5d98-2f75-4d11-b663-35ba9ac9727d" alt="logo" width="200"/>
</p>



Welcome to the **Real-Time Speech-to-Command** project — a voice control application that transcribes spoken commands in real-time and executes corresponding actions on your computer.

---

## 🚀 Project Overview

This project started as an experiment to explore **live speech-to-text** using AI models, and evolved into a desktop assistant that could control apps using voice commands like:

- **"Open notepad"**
- **"Scroll down"**
- **"Start typing"**

It was designed with a **focus on responsiveness**, aiming for low-latency transcription and accurate command recognition.

---

## 🧑‍💻 Features

- Real-time speech recognition
- Execute common system commands via voice
- Typing mode for dictating text
- Fuzzy matching for flexible command interpretation
- Multi-language support with switchable AI models

---

## 📸 Screenshot

![Screenshot 2025-03-21 234039](https://github.com/user-attachments/assets/5452855d-18d6-4331-b830-96c58b21c934)


---

## 📜 Development Journey

### 🌀 Initial Version: **Whisper by OpenAI**

The project began using **OpenAI’s Whisper** for speech recognition. Whisper offered **excellent transcription quality**, especially for longer audio files.

However, it came with significant drawbacks for live use:

- **High latency** for real-time transcription.
- **External dependency on FFmpeg**, which complicated installation and portability.
- Heavy CPU usage with larger models.

---

### ⚡ Transition to Faster-Whisper

To improve speed and reduce system resource usage, the project migrated to **Faster-Whisper**, a faster implementation with GPU support.

> 🎯 **Goal:** Real-time command execution without noticeable delays.

**Improvements:**
- Lower latency.
- Lighter system load.

But... despite these improvements, **Whisper (even Faster-Whisper)** proved **unreliable for real-time voice command recognition** due to its design for batch processing rather than streaming audio.

---

## 🧠 Lessons Learned

- Gained **deep insight into Whisper models**, their performance trade-offs, and deployment requirements.
- Learned **how to choose the best AI model** based on application needs: 
  - Large models = high accuracy, slow
  - Small models = fast, less accurate
- Understood the limitations of general-purpose ASR (automatic speech recognition) in **live control scenarios**.


---

## ❌ Project Status: Canceled

---

## 📄 License

This project is licensed under the **MIT License** — free for both personal and commercial use. See the [LICENSE](LICENSE) file for details.



