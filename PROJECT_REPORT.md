# 🎬 Advanced Media Processing Toolkit
## Automated Downloader, Segmenter & Neural Dubber
**Subject:** Software Development (Micro-Project)  
**Type:** Full Stack Web Application (React + Python)

---

## 📌 1. PROJECT OVERVIEW
This project is an advanced **Automated Media Pipeline** designed to simplify the process of acquiring, editing, and enhancing web video content. Unlike standard downloaders, this toolkit integrates **Artificial Intelligence (Neural Dubbing)** and **Video Processing (Segmentation)** directly into the download workflow.

It features a **Zero-Config** architecture, meaning it runs instantly on any Windows machine without complex installation steps, leveraging a bundled Python backend and a React-based frontend.

---

## 🛠️ 2. TECHNOLOGY STACK
The project is built using a **Hybrid Architecture**:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | **React.js (v18)** | Dynamic User Interface (Single Page App), State Management. |
| **Backend** | **Python (Flask)** | REST API Server, Orchestration of processing tasks. |
| **Core Engine** | **yt-dlp** | Robust media extraction, bypassing YouTube bot detection. |
| **Processing** | **MoviePy + FFmpeg** | Video editing, Audio merging, Segmentation. |
| **AI Voice** | **gTTS (Google TTS)** | Neural Text-to-Speech generation for dubbing. |
| **Deployment** | **Batch Script (.bat)** | One-click local deployment & dependency management. |

---

## ⚙️ 3. KEY FEATURES & FUNCTIONS

### A. Intelligent Media Extraction (`video_info`)
*   **Android Client Spoofing:** Mimics a mobile device to bypass YouTube's strict anti-bot blocking.
*   **Smart Quality Sorting:** Automatically identifies and ranks video resolutions (1080p, 720p, etc.) based on bitrate and height.
*   **Metadata Extraction:** Retrieves Thumbnail, Title, Duration, and Uploader details.

### B. Robust Download Engine (`process`)
*   **Audio-Video Merge:** Unlike standard tools that separate streams, our engine uses **FFmpeg** to merge the Best Video Stream (MP4) with the High-Fidelity Audio Stream (M4A) ensuring no quality loss.
*   **Auto-Retry Mechanism:** Includes socket timeouts and retry logic to handle unstable network connections.

### C. Neural Dubbing Engine (AI Feature)
*   **Dynamic Script Generation:** The system reads the Video Title and Channel Name to generate a custom introductory script.
*   **Voice Overlay:** Generates a professional **British English** AI voice.
*   **Smart Looping:** If the video is longer than the script, the audio is intelligently managed to fit the duration.

### D. Automated Post-Processing
*   **Auto-Segmenter:** Capable of slicing long videos into **30-second clips** (e.g., for Shorts/Reels usage).
*   **Direct Desktop Save:** Automatically locates the user's Desktop and saves the final output there.
*   **Temp Cleanup:** Uses a hidden `temp_processing` directory for heavy tasks and auto-deletes files after completion to save disk space.

---

## 📚 4. PYTHON LIBRARIES & IMPORTS EXPLAINED

This project utilizes specific libraries to achieve its "All-in-One" capability.

### 1. `flask` & `flask_cors`
```python
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
```
*   **Purpose:** creates the local web server.
*   **Why:** `jsonify` sends JSON data to React, `render_template` serves the HTML UI, and `CORS` allows the frontend to communicate with the backend securely.

### 2. `yt_dlp`
```python
import yt_dlp
```
*   **Purpose:** The successor to `youtube-dl`.
*   **Why:** It is currently the *only* library capable of reliably bypassing modern YouTube throttling and age-restrictions. We use `yt_dlp.YoutubeDL(options)` context managers for safe execution.

### 3. `moviepy.editor`
```python
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
```
*   **Purpose:** Video Editing.
*   **Why:** Allows us to load the video (`VideoFileClip`), replace its audio (`set_audio`), and cut it (`subclip`) programmatically without needing external software like Premiere Pro.

### 4. `imageio_ffmpeg`
```python
import imageio_ffmpeg
```
*   **Purpose:** Binary management.
*   **Why:** Automatically finds the FFmpeg executable binary on the system. This ensures the project runs even if the user hasn't manually installed FFmpeg in their PATH.

### 5. `gTTS` (Google Text-to-Speech)
```python
from gtts import gTTS
```
*   **Purpose:** AI Voice Generation.
*   **Why:** Converts the dynamically generated text string into an MP3 file, which MoviePy then overlays onto the video.

### 6. `os` & `shutil`
```python
import os, shutil
```
*   **Purpose:** File System Operations.
*   **Why:** `os.path.join` ensures cross-platform path compatibility. `shutil.move` transfers the final file to the Desktop, and `shutil.rmtree` cleans up the temporary folder.

---

## 🚀 5. SYSTEM ARCHITECTURE (Workflow)

1.  **User** pastes URL in **React UI**.
2.  **React** sends `POST /api/video-info` to **Flask**.
3.  **Flask** uses `yt-dlp` (Android Mode) to fetch metadata.
4.  **User** selects options (e.g., "1080p", "Neural Dub").
5.  **React** sends `POST /api/process`.
6.  **Backend Workflow:**
    *   Download Video -> `temp_processing/`
    *   Check for AI Dubbing? -> Generate MP3 -> Merge with MoviePy.
    *   Check for Segmentation? -> Cut Video.
    *   **Finalize:** Merge Audio/Video via FFmpeg.
    *   **Delivery:** Move file to `Desktop`.
    *   **Cleanup:** Delete `temp_processing/`.
7.  **Result:** "Notification" on UI.

---

## 🏁 6. CONCLUSION
This Micro-Project demonstrates the power of combining **Web Technologies** with **Python Automation**. By automating the complex tasks of downloading, merging, and dubbing, the tool saves significant manual effort and provides a seamless user experience.

---
**Developed for Micro-Project Submission (2025-26)**
