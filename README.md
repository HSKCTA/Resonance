
# 🏗️ **Resonance**

### Industrial-Grade Edge AI for Mechanical Fault Detection

**Resonance** is a **physics-first, offline edge-AI system** for detecting mechanical faults in motors, pumps, and rotating machinery using **structure-borne vibration and acoustic signals**.

Unlike chatbot-style AI projects, Resonance is built as a **real-time signal processing system** that uses **deterministic DSP, spectral analysis, and unsupervised anomaly detection** to identify faults that are invisible to human hearing.

The system is designed to run on **AMD Ryzen AI edge hardware** and in **air-gapped industrial environments**.

---

## 🔬 What Problem Does Resonance Solve?

Mechanical failures such as:

* bearing wear
* shaft misalignment
* cavitation
* imbalance
* looseness

all produce **distinct spectral signatures** in vibration and acoustic data long before catastrophic failure occurs.

Traditional monitoring systems are expensive and closed.
Resonance is an **open, software-defined vibration intelligence system** that performs the same analysis using:

* contact microphones (piezo sensors)
* real-time DSP
* AI trained only on healthy machine behavior

---

## 🧠 Core Engineering Philosophy

Resonance is built on four non-negotiable system principles:

### 1️⃣ Physics-First Signal Processing

Raw sensor data is cleaned using **high-pass (≈100–150 Hz)** and **low-pass (≈10–12 kHz)** filters before any AI is applied.
This removes DC drift, mains hum, speech, and environmental noise.

AI never sees unfiltered audio.

---

### 2️⃣ Deterministic Safety Layer

Before FFT or AI, Resonance computes **real-time RMS vibration energy** in C++.

If vibration exceeds a hard-coded safety threshold:

```
→ An alarm is triggered  
→ AI is bypassed  
→ The event is logged
```

This ensures the system is **fail-safe** and cannot miss critical faults.

---

### 3️⃣ Read-Only Doctrine

Resonance never controls machinery.

It acts as a **Digital Stethoscope**:

> It listens, analyzes, and advises — but never actuates.

This guarantees zero risk to plant operations.

---

### 4️⃣ Edge-Native Architecture

All DSP, FFT, AI inference, and language generation run **locally on AMD silicon**.

No cloud inference.
No internet dependency.
No data exfiltration.

---

## 🧩 System Architecture

Resonance is a **distributed real-time edge system** connected by **ZeroMQ**.

```
[ Sensor ]
     ↓
[ Node A – DSP Engine (C++) ]
     ↓
[ Node B – AI Brain (Python + ONNX) ]
     ↓
[ Node C – Dashboard / HMI ]
```

---

## 🔵 Node A — **The Ear** (C++ DSP Core)

**Role:**
Real-time signal acquisition, filtering, spectral analysis, and safety enforcement.

**Tech Stack**

* C++17
* PortAudio
* FFTW3
* ZeroMQ

**Pipeline**

```
Piezo Sensor / Mic
 → High-Pass + Low-Pass filters
 → RMS Safety Gate
 → 2048-point FFT (75% overlap)
 → Log-magnitude Spectrogram (1024 × 64)
 → ZeroMQ PUB
```

This produces an AI-ready tensor that encodes **nearly one second of machine vibration** in the frequency domain.

---

## 🧠 Node B — **The Brain** (Anomaly Detection)

**Role:**
Detect faults and explain them to humans.

**Tech Stack**

* PyTorch
* ONNX Runtime
* Vitis AI (Ryzen AI NPU support)
* Ollama (local LLM)

**Model**

* Convolutional Autoencoder
* Trained only on **healthy vibration data**
* Learns what “normal” looks like
* Flags anything that deviates from it

**Inference Flow**

```
Spectrogram
 → Autoencoder
 → Reconstruction Error (MSE)
 → Severity Score
```

When an anomaly is detected, a **local language model** converts it into a **human-readable explanation** in:

* English
* Hindi
* Marathi

The LLM is used **only for explanation**, not for detection.

---

## 🟢 Node C — **The Face** (Dashboard)

**Role:**
Visualization and situational awareness.

**Features**

* Live waterfall spectrogram
* RMS vibration history
* Fault alerts and severity
* Worker-friendly interface

Runs locally in Docker.

---

## 📡 Interface Contract (Node A → Node B)

All data is sent using **ZeroMQ PUB/SUB** on port `5555`.

**Format: multipart**

* Frame 0 → JSON metadata
* Frame 1 → raw float32 tensor

**Tensor shape**

```
(1 × 1024 × 64)
```

This represents a rolling log-spectrogram of machine vibration.

---

## 🔍 Why Resonance Works

Mechanical faults do not sound like speech.
They appear as **spectral patterns**:

| Fault        | Spectral Signature                 |
| ------------ | ---------------------------------- |
| Bearing wear | High-frequency harmonics           |
| Misalignment | Strong 2× and 3× shaft frequencies |
| Imbalance    | Large 1× shaft peak                |
| Looseness    | Sidebands and modulation           |

Resonance detects these patterns using **physics + AI**, not guesswork.

---

## 🧪 Privacy by Design

Human speech lies between **80 Hz – 3 kHz**.
Resonance filters this out **before** the AI layer.

No conversations are ever recorded or processed.

---

## 🚀 Deployment

Resonance is designed for:

* AMD Ryzen AI laptops
* Industrial PCs
* AMD cloud edge clusters

The same stack runs everywhere.

---

## 👥 Team

* **Hitesh Khare** — Systems Engineering (C++ DSP Core)
* **Tanmay Bhole** — AI Architecture & Model Deployment
* **Gaurav Shelke** — Dashboard & Integration

---

**Built for AMD Slingshot Hackathon 2026**
*Real-time physics. Real machines. Real AI.*
