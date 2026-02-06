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

##🧰 Core Modules

#📥 ZeroMQ Listener (inference/zmq_listener.py)

Listens for multipart messages from Node A:

Frame 0: JSON metadata

Frame 1: raw float32 bytes representing spectrogram

Shape: (1 × 1024 × 64)

#🔍 Autoencoder Inference (inference/ae_inference.py)

Loads the quantized ONNX model and runs inference.

#⚙️ Anomaly Scoring (inference/anomaly_score.py)

Calculates reconstruction error and maps it to severity:

Normal
Low
Medium
High

#🗣️ Local GenAI Alerts (llm/)

Uses a local LLM (Phi-3/Llama-3 via Ollama):
Generates natural language alerts
Supports Marathi, Hindi, English
Runs fully offline
--

##🗂️ Project Structure

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


##🛠️ Installation & Usage

#📌 Install dependencies
cd Resonance/python
pip install -r requirements.txt

#🚀 Run Node B
python inference/main.py

Expected output:

[INFO] Autoencoder ONNX model loaded
[NODE B] Resonance AI Inference Started
Listening on tcp://localhost:5555
--
## Integration Guide
ZeroMQ Messaging Contract
Field	Value
Protocol	ZeroMQ PUB/SUB
Endpoint	tcp://localhost:5555
Metadata	JSON in Frame 0
Payload	float32 spectrogram bytes
Shape	(1 × 1024 × 64)

Ensure Node A uses multipart ZeroMQ with this scheme.

--

##📌 Training & ONNX Export

Run training (with dataset) on GPU/Colab:

python training/train.py
python training/export_onnx.py


This will generate:

weights/autoencoder.pth
onnx/autoencoder.onnx
onnx/autoencoder.onnx.data

Place these into the local project.
--

##🧠 Future Enhancements

Log reconstruction error over time for real threshold calibration

AMD Ryzen AI NPU acceleration (INT8 via Vitis AI)

UI / Dashboard integration

--

##📌 Notes

Node B requires no datasets at runtime

Fully offline and edge-deployable

GenAI runs locally (no cloud)
--
##🛡️ Credits

Node B developed by Tanmay Bhole
Part of the Resonance Industrial Anomaly Detection System
