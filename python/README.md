# 📡 Resonance – Node B  
## AI Inference & Worker Communication Module

---

## 🚀 Overview

Node B is the **AI inference engine** of the Resonance industrial acoustic anomaly detection system.

It receives **preprocessed spectrograms** from Node A via **ZeroMQ**, performs **real-time anomaly detection** using a convolutional autoencoder, and generates **worker-friendly alerts** via a local GenAI model in Marathi/Hindi/English.

This module is designed to run **offline** and is **edge-ready**, with optional GPU/NPU acceleration.

---

## 🧠 What Node B Does

- Listens to Node A spectrogram data over ZeroMQ
- Reconstructs input using a trained autoencoder
- Computes **reconstruction error (MSE)**
- Classifies normal vs anomaly with severity levels
- Converts anomalies into natural language alerts via a local LLM

---

### 📡 Resonance – Node B  
## AI Inference & Worker Communication Module

---

## 🚀 Overview

Node B is the **AI inference engine** of the Resonance industrial acoustic anomaly detection system.

It receives **preprocessed spectrograms** from Node A via **ZeroMQ**, performs **real-time anomaly detection** using a convolutional autoencoder, and generates **worker-friendly alerts** via a local GenAI model in Marathi/Hindi/English.

This module is designed to run **offline** and is **edge-ready**, with optional GPU/NPU acceleration.

---

## 🧠 What Node B Does

- Listens to Node A spectrogram data over ZeroMQ
- Reconstructs input using a trained autoencoder
- Computes **reconstruction error (MSE)**
- Classifies normal vs anomaly with severity levels
- Converts anomalies into natural language alerts via a local LLM

---

##🔍 Autoencoder Inference (inference/ae_inference.py)

Loads the quantized ONNX model and runs inference.

##⚙️ Anomaly Scoring (inference/anomaly_score.py)

Calculates reconstruction error and maps it to severity:

Normal

Low

Medium

High

##🗣️ Local GenAI Alerts (llm/)

Uses a local LLM (Phi-3/Llama-3 via Ollama):

Generates natural language alerts

Supports Marathi, Hindi, English

Runs fully offline


## 🏗️ High-Level Architecture

```mermaid
flowchart LR
    subgraph Node A (C++)
      A1[Sensor & ADC]
      A2[Signal Processing]
      A3[FFT & Spectrogram]
    end

    subgraph Messaging
      A3 -->|ZeroMQ PUB| ZMQ[(tcp://localhost:5555)]
    end

    subgraph Node B (Python AI)
      ZMQ --> B1[ZMQ Listener]
      B1 --> B2[ONNX Autoencoder Inference]
      B2 --> B3[Reconstruction Error (MSE)]
      B3 --> B4[Threshold & Severity]
      B4 --> B5[Local GenAI Alert]
    end

    subgraph Worker Interface
      B5 --> Worker[Worker/Ux/UI]
    end
---
🧠 Data Flow
sequenceDiagram
    participant A as Node A (C++)
    participant B as Node B (Python)
    participant L as Local LLM
    participant W as Worker/Ux

    A->>B: Send spectrogram (ZeroMQ)
    B->>B: Autoencoder reconstruction
    B->>B: Calculate MSE
    B->>B: Threshold + Severity
    B->>L: Generate alert text
    L->>W: Deliver worker message

----------
🗂️ Project Structure
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
│   ├── prompt.py
│   ├── local_llm.py
│   └── translator.py
│
├── utils/
│   ├── spectrogram.py
│   └── config.py
│
├── weights/
│   └── autoencoder.pth  ← training artifact
│
├── onnx/
│   ├── autoencoder.onnx
│   └── autoencoder.onnx.data
│
├── requirements.txt
└── README.md

-----------

##🛠️ Installation & Usage

📌 Install dependencies
cd Resonance/python
pip install -r requirements.txt
🚀 Run Node B
python inference/main.py
Expected output:

[INFO] Autoencoder ONNX model loaded
[NODE B] Resonance AI Inference Started
Listening on tcp://localhost:5555
Node B will wait until Node A starts publishing.

##🔗 Integration Guide
ZeroMQ Messaging Contract
Field	Value
Protocol	ZeroMQ PUB/SUB
Endpoint	tcp://localhost:5555
Metadata	JSON in Frame 0
Payload	float32 spectrogram bytes
Shape	(1 × 1024 × 64)
Ensure Node A uses multipart ZeroMQ with this scheme.

##📌 Training & ONNX Export
Run training (with dataset) on GPU/Colab:

python training/train.py
python training/export_onnx.py
This will generate:

weights/autoencoder.pth

onnx/autoencoder.onnx

onnx/autoencoder.onnx.data

Place these into the local project.

🧪 How to Test Without Node A
For demonstration or debugging, use a test publisher like this:

import zmq, time, json, numpy as np

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5555")
time.sleep(1)

while True:
    spec = np.random.randn(1,1024,64).astype(np.float32)
    meta = {"source":"sim","shape":spec.shape, "ts":time.time()}
    pub.send_multipart([json.dumps(meta).encode(), spec.tobytes()])
    time.sleep(1)
This simulates a real Node A.

##🧠 Future Enhancements
Log reconstruction error over time for real threshold calibration

AMD Ryzen AI NPU acceleration (INT8 via Vitis AI)

UI / Dashboard integration

##📌 Notes
Node B requires no datasets at runtime

Fully offline and edge-deployable

GenAI runs locally (no cloud)

##🛡️ Credits
Node B developed by Tanmay Bhole
Part of the Resonance Industrial Anomaly Detection System
