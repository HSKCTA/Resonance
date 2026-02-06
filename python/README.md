Resonance – Node B
AI Inference & Worker Communication Module
1. Overview

Node B is the edge AI inference and GenAI communication component of the Resonance Industrial Acoustic Anomaly Detection System.

It performs:

Real-time anomaly detection on spectrogram tensors received from Node A

Unsupervised learning of healthy machine behavior using a convolutional autoencoder

Severity scoring and anomaly decision logic

Local language alert generation (Marathi / Hindi / English) using a fully offline LLM

Node B is designed to run:

Offline

On edge hardware

Without requiring datasets during runtime

With optional AMD Ryzen AI / GPU acceleration

2. Role of Node B in the Full System
Machine Sensor → Node A (C++ DSP)
                     │
                     │ ZeroMQ (spectrogram tensor)
                     ▼
              Node B (Python AI)
                     │
                     ├─ Reconstruction Error
                     ├─ Anomaly Detection
                     └─ Worker Alert (GenAI)


Node B does not handle:

Raw audio acquisition

FFT or DSP processing

UI rendering

It strictly focuses on AI inference + communication.

3. Core Capabilities
Real-Time AI Inference

Receives (1 × 1024 × 64) spectrogram tensors via ZeroMQ PUB/SUB

Runs ONNX-based convolutional autoencoder inference

Computes MSE reconstruction error

Classifies:

Normal

Low anomaly

Medium anomaly

High anomaly

Offline GenAI Worker Alerts

Uses local LLM (Phi-3 / Llama-3 via Ollama)

Converts anomaly severity into:

Marathi

Hindi

English

Ensures factory-safe offline deployment

4. Model Design & Training
Dataset

CWRU Bearing Dataset

Trained only on healthy baseline data

Enables zero-shot detection of unseen faults

Input Representation

Pipeline:

Time-series vibration
→ FFT
→ Magnitude
→ Log-magnitude spectrogram
→ Normalize
→ (1 × 1024 × 64)

Architecture

Convolutional Autoencoder

Encoder → latent normal-behavior manifold

Decoder → reconstructs healthy spectrogram

High reconstruction error ⇒ anomaly

Training Environment

Executed on Google Colab GPU

Saved artifacts:

weights/autoencoder.pth

onnx/autoencoder.onnx

onnx/autoencoder.onnx.data

5. Deployment Pipeline (Inference-Only Runtime)
ZeroMQ Listener
      ↓
ONNX Autoencoder Inference
      ↓
Reconstruction Error (MSE)
      ↓
Threshold-Based Severity
      ↓
Local LLM Alert (optional)


Runtime does NOT require:

Dataset

Training scripts

Internet access

6. Project Structure (Node B)
python/
├── inference/
│   ├── main.py
│   ├── zmq_listener.py
│   ├── ae_inference.py
│   └── anomaly_score.py
│
├── training/
│   ├── autoencoder.py
│   ├── train.py
│   └── export_onnx.py
│
├── llm/
│   ├── local_llm.py
│   ├── prompt.py
│   └── translator.py
│
├── utils/
│   ├── spectrogram.py
│   └── config.py
│
├── weights/
│   └── autoencoder.pth
│
├── onnx/
│   ├── autoencoder.onnx
│   └── autoencoder.onnx.data
│
├── requirements.txt
└── README.md

7. Installation & Running
Install dependencies
pip install -r requirements.txt

Run Node B
cd python
python inference/main.py


Expected output:

[INFO] Autoencoder ONNX model loaded
[NODE B] Resonance AI Inference Started
Listening on tcp://localhost:5555


Node B will wait until Node A publishes spectrograms.

8. Integration with Node A
Communication Protocol

Transport: ZeroMQ PUB/SUB

Endpoint: tcp://localhost:5555

Message format: multipart

Frame 0 → JSON metadata

Frame 1 → float32 spectrogram bytes

Spectrogram Shape
(1 × 1024 × 64)


If Node A follows this contract → Node B works without modification.

9. Running in Google Colab (Training Only)

Steps:

Upload python/ and CWRU dataset

Run:

python training/train.py


Export:

python training/export_onnx.py


Download:

autoencoder.pth

autoencoder.onnx

autoencoder.onnx.data

Place into local python/ folder

After this, runtime is fully reproducible.

10. Threshold Calibration (Planned)

Future enhancement:

Log reconstruction error over time

Capture:

Idle

Healthy

Induced vibration

Derive statistical anomaly thresholds

This converts heuristic detection → data-driven reliability.

11. Hardware Acceleration Roadmap

Planned optimizations:

AMD Ryzen AI NPU (Vitis AI INT8 quantization)

ROCm GPU inference

Edge deployment packaging

12. Key Engineering Highlights

Fully offline-capable AI system

Zero-shot anomaly detection

Real-time streaming inference

Local-language GenAI alerts

Edge-ready modular architecture

Clean MLOps artifact management

13. Status
Completed

Training pipeline

ONNX deployment

Real-time inference

ZeroMQ integration

Local GenAI alerts

In Progress

Threshold calibration

Edge acceleration

14. Authors & Contribution

Node B – AI Inference & GenAI Communication

Model design

Training & ONNX export

Real-time inference pipeline

Local multilingual alert generation

Integration with Node A
