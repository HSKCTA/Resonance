# 🏗️ Resonance: Industrial Acoustic Anomaly Detection (Edge AI)

**Resonance** is a physics-first, offline Edge AI system designed to detect mechanical anomalies (bearing wear, cavitation, misalignment) in industrial machinery using structure-borne audio analysis.

Unlike standard predictive maintenance tools, Resonance uses **deterministic signal processing** for safety gates and **generative AI** to translate technical faults into vernacular instructions (Hindi/Marathi) for factory floor workers.

---

## ⚡ Core Philosophy

Resonance operates on four non-negotiable engineering principles:

1. **Physics-First:** We do not rely on AI to clean audio. We use hardware filters and DSP to isolate mechanical frequency bands (100Hz - 10kHz) before the neural network sees data.


2. **Deterministic Safety:** If vibration RMS exceeds ISO safety thresholds, a hard-coded C++ gate triggers an immediate alarm, bypassing the AI entirely.


3. **Read-Only Doctrine:** The system acts as a "Digital Stethoscope." It is advisory only and **never** executes control commands on machinery, ensuring 100% operational safety.


4. **Edge Supremacy:** Designed for air-gapped environments. No cloud dependencies. No latency.



---

## 🛠️ System Architecture

The system follows a distributed **Hub-and-Spoke** architecture connected via a high-performance **ZeroMQ** mesh.

### 🔵 Node A: The "Ear" (C++ Core)

* **Role:** Signal Ingestion & DSP Pre-processing.
* **Tech:** `C++17`, `PortAudio`, `FFTW3`, `ZeroMQ`.
* **Pipeline:** Ingests raw audio from Piezoelectric Contact Sensors.


* Applies **High-Pass (100Hz)** and **Low-Pass (10kHz)** filters to remove DC offset, mains hum, and human speech.


* Computes **RMS Amplitude** for the deterministic safety gate.


* Generates `1024-bin` FFT Spectrograms and broadcasts via ZMQ PUB.





### 🧠 Node B: The "Brain" (Python AI)

* **Role:** Anomaly Detection & Worker Communication.
* **Tech:** `Python`, `PyTorch`, `Vitis AI`, `Ollama`.
* **Hardware:** Optimized for **AMD Ryzen AI NPU**.
* **Logic:**
* Runs a **Convolutional Autoencoder** trained *only* on normal vibration data.


* Calculates **Reconstruction Error (MSE)**. High error = Anomaly.


* On fault detection, uses a local SLM (Phi-3/Llama-3) to translate technical errors into local languages (Marathi/Hindi) for workers.





### 🟢 Node C: The "Face" (Dashboard)

* **Role:** Situational Awareness & Visualization.
* **Tech:** `Next.js`, `Node.js`, `Socket.io`, `Docker`.
* **Features:** Real-time 60FPS Waterfall Spectrogram, RMS history, and Safety Alerts.



---

## 📡 The Interface Contract

All nodes communicate via a strict **ZeroMQ PUB/SUB** protocol on port `5555`.

* **Topic:** `audio_data`
* **Input Shape:** `[1, 1024, 64]` (Channels × Frequency Bins × Time Steps).
* **Payload:** Flattened `float32` array representing the spectrogram.

```cpp
// Example ZMQ Packet Structure
{
  "header": "audio_data",
  "metadata": {
    "timestamp": 1706423000,
    "rms": 0.85,
    "shape": [1, 1024, 64]
  },
  "payload": <Binary Blob>
}

```

---

## 🔬 The Science: Why "Resonance" Works

Industrial faults have specific spectral signatures that human ears miss. Resonance targets these harmonics:

| Fault Type | Spectral Signature | Detection Method |
| :--- | :--- | :--- |
| **Bearing Wear** | High-frequency harmonics (>5kHz) | Autoencoder Reconstruction Error |
| **Misalignment** | Strong 2×, 3× shaft frequency peaks | FFT Peak Detection |
| **Looseness** | Frequency Sidebands | Spectral Analysis |
| **Imbalance** | Large 1× shaft peak | RMS Gate |

**Privacy by Design:** By filtering out the 80Hz–3kHz range (Human Voice) *before* the AI layer, we ensure no worker conversations are ever processed or recorded.

---

## 🚀 Getting Started

### Prerequisites

* Docker & Docker Compose
* AMD Ryzen AI Driver (for NPU acceleration)
* Piezoelectric Sensor (or standard mic for testing)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/HSKCTA/Resonance.git
cd Resonance

```


2. **Launch the Stack**
```bash
docker-compose up --build

```


* *The C++ Engine starts listening on the default audio device.*
* *The Dashboard launches at `http://localhost:3000`.*



---

## 👥 The Team

* **Hitesh Khare:** Systems Engineering (C++ / DSP Core)
* **Tanmay Bhole:** AI/ML Architect (Model Quantization & GenAI)
* **Gaurav Shelke:** Full Stack & Integration (Dashboard & Docker)

---

*Built for the AMD Slingshot Hackathon 2026.*
