# 🏙️ Smart City Violation & Anomaly Detection

[![Node.js](https://img.shields.io/badge/Node.js-v18+-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Mongoose-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.0-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, multimodal (audio-visual) artificial intelligence platform and web dashboard engineered for smart city surveillance and public safety monitoring. The system fuses visual motion cues and acoustic signals (screams, explosions, physical fighting, crashes) using deep learning to reliably detect violent acts and anomalies in real-time.

---

## 📑 Table of Contents

- [📌 Project Overview & Motivation](#-project-overview--motivation)
- [✨ Key Features](#-key-features)
- [🏛️ System Architecture & Workflow](#️-system-architecture--workflow)
- [🧠 Deep Learning Architecture (Multi-Agent Fusion)](#-deep-learning-architecture-multi-agent-fusion)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Project Directory Structure](#-project-directory-structure)
- [🔌 API Reference](#-api-reference)
  - [Node.js Express Backend](#nodejs-express-backend)
  - [FastAPI Python Microservice](#fastapi-python-microservice)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [🚀 Installation & Setup Guide](#-installation--setup-guide)
  - [1. Prerequisites](#1-prerequisites)
  - [2. Dependencies Setup](#2-dependencies-setup)
  - [3. Python Conda Environment](#3-python-conda-environment)
- [🏃 How to Run](#-how-to-run)
- [🔬 Model Training & Evaluation](#-model-training--evaluation)
- [🩺 Troubleshooting & FAQ](#-troubleshooting--faq)
- [📄 License & Authors](#-license--authors)

---

## 📌 Project Overview & Motivation

In traditional city surveillance operations, human operators are overwhelmed by thousands of live camera feeds, leading to missed critical events and delayed emergency response times. Furthermore, unimodal video-only detection models struggle with occlusions, bad weather, poor lighting, or camera angles.

**Smart City Violation Detection** addresses these challenges through a multimodal multi-agent architecture:
1. **Visual Streams:** Analyze motion, posture, and spatial-temporal interactions using pretrained 3D convolutional features (**MIL-NCE / I3D**).
2. **Audio Streams:** Capture vital acoustic cues (gunshots, screaming, physical clashes) extracted at 16 kHz using **VGGish**.
3. **Adaptive Gating:** Dynamically weighs audio versus visual evidence, ensuring reliable classification even if visual visibility is compromised.
4. **Full-Stack Application:** Includes a Node.js/Express orchestration backend, Cloudinary video storage, MongoDB historical logs, and a reactive React 19 web dashboard.

---

## ✨ Key Features

- **Multimodal Audio-Visual Fusion:** Combines visual and acoustic signals with learnable gating to detect fights, abuse, weapons, and public disturbance.
- **Asynchronous Non-Blocking Processing:** Video uploads respond immediately while FastAPI and PyTorch background tasks handle heavy feature extraction and inference.
- **Interactive Surveillance Dashboard:**
  - Drag-and-drop or file selector video upload.
  - Video player modal for reviewing footage.
  - Real-time detection status indicators (`Pending`, `Safe`, `Violation Detected`).
  - Anomaly probability and accuracy percentage scores.
  - Historical query panel with pagination and smooth Framer Motion animations.
- **Microservice Design:** Decoupled architecture separating web presentation, business logic, and heavy AI inference.
- **Cloud-Ready Asset Storage:** Automatic streaming upload to Cloudinary with secure URLs.

---

## 🏛️ System Architecture & Workflow

```mermaid
flowchart TD
    User([User / Operator]) -->|1. Upload Surveillance Video| Client[React 19 + Vite Web App]
    Client -->|2. POST /anomaly (Multipart)| NodeServer[Node.js / Express API]
    NodeServer -->|3. Upload Video Stream| Cloudinary[(Cloudinary Cloud Storage)]
    Cloudinary -->|4. Return Secure Video URL| NodeServer
    NodeServer -->|5. Save Initial Record| MongoDB[(MongoDB Database)]
    NodeServer -->|6. POST /analyze {id, videoUrl}| PyService[FastAPI AI Microservice]
    
    subgraph PyService Pipeline
        PyService -->|7. Download Video & Extract Audio via FFMPEG| FFMPEG[FFMPEG]
        FFMPEG -->|16kHz Mono WAV| VGGish[VGGish Audio Extractor]
        FFMPEG -->|24 FPS RGB Frames| I3D[MIL-NCE / I3D Visual Extractor]
        VGGish -->|128-d Feature Vector| MultiAgent[Multi-Agent Fusion Model]
        I3D -->|1024-d Feature Vector| MultiAgent
        MultiAgent -->|Compute Violence Score & Threshold 0.53| Decision[Inference Decision Engine]
    end
    
    Decision -->|8. PATCH /anomaly/:id {isAnomaly, accuracy}| NodeServer
    NodeServer -->|9. Update Record| MongoDB
    Client -.->|10. Poll / Fetch Logs| NodeServer
```

---

## 🧠 Deep Learning Architecture (Multi-Agent Fusion)

The AI engine in `pyService/src/model.py` is implemented using a custom **MultiAgentViolenceModel** architecture in PyTorch:

```text
[Input Video]
      ├──> FFMPEG (24 FPS)      ──> MIL-NCE / I3D ──> [B, T, 1024] ──> VisualAgent ──> [B, 256] ──┐
      ├──> FFMPEG (16kHz Mono)  ──> VGGish        ──> [B, T, 128]  ──> AudioAgent  ──> [B, 128] ──┼──> ModalityGating ──> DecisionAgent ──> Logits / Prob
      └──> (Optional Flow)      ──> TV-L1 / Flow  ──> [B, T, 1024] ──> MotionAgent ──> [B, 256] ──┘
```

### Agents & Modules:
- **`TemporalAttention`:** Calculates normalized attention scores over temporal frames ($T$), allowing the model to focus on the exact seconds where violent activity occurs rather than static background frames.
- **`AudioAgent`:** Applies temporal attention over 128-dimensional VGGish audio embeddings, followed by an MLP (`Linear(128->256) -> ReLU -> Dropout(0.3) -> Linear(256->128)`).
- **`VisualAgent`:** Applies temporal attention over 1024-dimensional visual features, followed by an MLP (`Linear(1024->512) -> ReLU -> Dropout(0.3) -> Linear(512->256)`).
- **`MotionAgent`:** Supports optical flow dynamics to capture velocity vectors of violent motions.
- **`ModalityGating`:** Learnable gating network (`Linear -> Softmax`) that dynamically computes importance weights across modalities based on input context.
- **`DecisionAgent`:** Fuses gated representations and passes through a multi-layer classifier with `Dropout(0.5)` to output final violence logits.
- **Dataset & Weights:** Trained on the benchmark **XD-Violence** dataset (19,770 training instances, 4,000 test instances) using `BCEWithLogitsLoss` with positive class balancing. Production checkpoint: `TrueTrueFalsebest_model.pth` (Audio + Visual enabled) with an optimal decision threshold of **0.53**.

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 19 (`react`, `react-dom`)
- **Build Tool:** Vite 7
- **Language:** TypeScript 5.9
- **Styling:** Tailwind CSS 4, PostCSS, Autoprefixer
- **Animations & UX:** Framer Motion 12, `@studio-freight/lenis` (smooth scrolling), `react-icons`
- **Networking:** Axios, React Router DOM 7

### Backend API
- **Runtime:** Node.js (v18+)
- **Framework:** Express 5
- **Language:** TypeScript 5.9 (`ts-node`, `ts-node-dev`, `nodemon`)
- **Database:** MongoDB via Mongoose 9
- **Media Upload:** Multer, Streamifier, Cloudinary SDK v2
- **Utilities:** `cors`, `dotenv`, `compression`, `cookie-parser`, `body-parser`

### AI / Microservice
- **Framework:** FastAPI, Uvicorn
- **Deep Learning:** PyTorch, TorchVision
- **Audio Extraction:** VGGish, FFMPEG
- **Visual Extraction:** MIL-NCE (I3D backbone), OpenCV (`cv2`), TensorFlow (for feature extractors)
- **Scientific Computing:** NumPy, Scikit-Learn, Matplotlib

---

## 📂 Project Directory Structure

```text
Anomaly-Detection/
├── client/                             # React 19 Frontend Application
│   ├── src/
│   │   ├── components/                 # Reusable UI components (Modal, Buttons, Cards)
│   │   ├── layouts/                    # Layout wrappers, Sidebar, Alert provider
│   │   ├── pages/                      # Application views (Home.tsx dashboard)
│   │   ├── services/                   # Axios API calls (uploadService, getAnomaliesService)
│   │   ├── App.tsx                     # Main routing & application wrapper
│   │   └── main.tsx                    # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── server/                             # Node.js + Express + TypeScript Backend
│   ├── src/
│   │   ├── config/                     # Cloudinary and environment config
│   │   ├── controllers/                # Request handlers (anomalies.ts)
│   │   ├── db/                         # Mongoose schemas & data access (anomalies.ts)
│   │   ├── helpers/                    # Cloudinary stream upload helper
│   │   ├── middlewares/                # Multer memory storage middleware
│   │   ├── router/                     # API route declarations
│   │   └── index.ts                    # Server startup & DB connection
│   ├── package.json
│   └── tsconfig.json
│
├── pyService/                          # Python Deep Learning Inference Microservice
│   ├── checkpoints/                    # Saved weights (TrueTrueFalsebest_model.pth)
│   ├── data/                           # Dataset annotations and cache
│   ├── feature_extract/                # Feature extraction engines (VGGish, MIL-NCE)
│   ├── requirements/                   # Conda environment definition (environment.yml)
│   ├── src/
│   │   ├── api.py                      # FastAPI app & background analysis endpoint
│   │   ├── dataset.py                  # PyTorch Dataset for XD-Violence
│   │   ├── extract_feature.py          # FFMPEG audio/video feature extraction routines
│   │   ├── inference.py                # ViolenceInferenceService wrapper class
│   │   ├── model.py                    # MultiAgentViolanceModel & Attention architecture
│   │   ├── test.py                     # Evaluation script (ROC-AUC, Confusion Matrix)
│   │   └── train.py                    # Training script with Adam & BCEWithLogitsLoss
│   ├── ffmpeg.exe                      # Local FFMPEG binary (or use system PATH)
│   └── README.md
│
├── package.json                        # Root concurrently runner
├── ReadMe.txt                          # Quick startup notes
└── README.md                           # Main project documentation
```

---

## 🔌 API Reference

### Node.js Express Backend
Base URL: `http://localhost:8080`

| Method | Endpoint | Description | Request Body / Params | Response |
|---|---|---|---|---|
| `POST` | `/anomaly` | Upload video for anomaly analysis | `multipart/form-data` with `video` file (.mp4) | `200 OK` (Anomaly Document) |
| `GET` | `/anomalies` | Retrieve all anomaly history logs | None | `200 OK` (Array of Anomaly Documents) |
| `GET` | `/anomaly/:id` | Fetch details of a single record | `id`: MongoDB ObjectId | `200 OK` (Anomaly Document) |
| `PATCH` | `/anomaly/:id` | Update anomaly classification result | JSON: `{ isAnomaly: boolean, accuracy: number }` | `200 OK` (Updated Document) |

#### Sample MongoDB Anomaly Document:
```json
{
  "_id": "665c8f8b345e56e0e3b9c123",
  "originalUrl": "https://res.cloudinary.com/your-cloud/video/upload/v1/anomaly-videos/sample.mp4",
  "videoName": "street_fight_01.mp4",
  "isAnomaly": true,
  "accuracy": 89.42,
  "createdAt": "2026-09-02T19:00:00.000Z",
  "updatedAt": "2026-09-02T19:00:15.000Z"
}
```

---

### FastAPI Python Microservice
Base URL: `http://localhost:8000` (Swagger UI: `http://localhost:8000/docs`)

| Method | Endpoint | Description | Payload |
|---|---|---|---|
| `POST` | `/analyze` | Enqueue video for feature extraction & inference | `{"id": "mongo_id", "videoUrl": "https://..."}` |

---

## ⚙️ Environment Configuration

### 1. Server Configuration (`server/.env`)
Create a `.env` file in the `server/` directory:
```env
PORT=8080
DATABASE_URL=mongodb://localhost:27017/anomaly-detection
# Or MongoDB Atlas: mongodb+srv://<user>:<password>@cluster.mongodb.net/anomaly-detection
FRONTEND_URL=http://localhost:5173
FASTAPI_URL=http://localhost:8000

# Cloudinary Storage Credentials
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### 2. Client Configuration (`client/.env`)
Create a `.env` file in the `client/` directory:
```env
VITE_API_URL=http://localhost:8080
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- **Node.js** (v18.0.0 or later) & **npm**
- **Anaconda** or **Miniconda** (Python 3.10)
- **FFMPEG** installed and available in system PATH (or placed in `pyService/ffmpeg.exe`)
- **MongoDB** running locally or a remote MongoDB Atlas URI

---

### 2. Dependencies Setup

#### Root & Web Services
Clone the repository and install all Node.js dependencies:
```bash
# In the root repository folder
npm install

# Install server packages
cd server
npm install

# Install client packages
cd ../client
npm install

cd ..
```

---

### 3. Python Conda Environment
Set up the Python AI inference environment:
```bash
cd pyService

# Create conda environment from environment.yml
conda env create -f requirements/environment.yml

# Activate environment
conda activate visea-venv

# If PyTorch with CUDA support is required (Recommended for GPU):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Ensure other required libraries are installed
pip install fastapi uvicorn httpx opencv-python pydantic scikit-learn
```

> **Note on Model Checkpoints:**
> Ensure that the model weights are located at:
> - `pyService/checkpoints/TrueTrueFalsebest_model.pth`
> - `pyService/feature_extract/vggish/checkpoints/vggish_model.ckpt`
> - `pyService/feature_extract/milnce-i3d/`

---

## 🏃 How to Run

### Method 1: Standard Dual-Terminal Execution

#### 🔹 Terminal 1: Full-Stack Web Application (Server + Client)
From the project root:
```bash
npm start
```
*This uses `concurrently` to run both the Express backend (`http://localhost:8080`) and Vite frontend (`http://localhost:5173`).*

#### 🔹 Terminal 2: AI Inference Microservice
From the `pyService` directory:
```bash
cd pyService
conda activate visea-venv
uvicorn src.api:app --host 0.0.0.0 --port 8000
```
*The FastAPI inference engine is now listening on port 8000.*

---

## 🔬 Model Training & Evaluation

To train or re-evaluate the multimodal multi-agent model from scratch:

1. **Prepare Dataset:**
   Place the XD-Violence dataset under the path configured in `pyService/src/train.py` (e.g. `data/XDViolance/`).
2. **Extract Multimodal Features:**
   ```bash
   python src/extract_feature.py
   ```
3. **Train Multi-Agent Model:**
   ```bash
   python src/train.py
   ```
   *Trains the `MultiAgentViolanceModel` for 50 epochs with `ReduceLROnPlateau` scheduler and saves checkpoints to `checkpoints/`.*
4. **Evaluate Model:**
   ```bash
   python src/test.py
   ```
   *Generates ROC-AUC curves, accuracy scores, and confusion matrix displays.*

---

## 🩺 Troubleshooting & FAQ

#### 1. FFMPEG not found error
- **Cause:** FFMPEG is not detected in your PATH or in `pyService/`.
- **Solution:** Place `ffmpeg.exe` directly inside `pyService/` or install FFMPEG system-wide (`winget install Gyan.FFmpeg` on Windows) and add it to your System Environment PATH.

#### 2. CUDA Out of Memory / CPU Fallback
- `pyService/src/api.py` automatically checks `torch.cuda.is_available()` and falls back to `"cpu"`. If running on GPU, reduce video length or adjust batch sizes.

#### 3. Cloudinary Upload Errors
- Verify that your Cloudinary credentials (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`) in `server/.env` are correct and that the upload preset allows video files.

#### 4. MongoDB Connection Timeout
- Ensure your MongoDB server is active (`mongod` service on local machine) or check network whitelist access in MongoDB Atlas (IP 0.0.0.0/0 for development).

---

## 📄 License & Authors

- **Author:** [Berkay Cengiz](https://github.com/berkaycengiz)
- **Repository:** [Smart-City-Violation-Detection](https://github.com/berkaycengiz/Smart-City-Violation-Detection)
- **License:** Distributed under the MIT License. See [LICENSE](LICENSE) for more details.
