🔊 Resonance – Node BAI Inference & Worker Communication EngineResonance is an advanced industrial acoustic anomaly detection system. Node B serves as the "Intelligence Layer," transforming raw processed audio data into actionable insights and multilingual worker alerts.📖 OverviewNode B is the edge-deployed inference engine responsible for identifying mechanical irregularities without requiring a predefined dataset of "faulty" sounds.Core Responsibilities:Data Consumption: Receives preprocessed spectrogram tensors from Node A via ZeroMQ.Anomaly Detection: Utilizes an Unsupervised Convolutional Autoencoder to detect deviations from "normal" machine behavior.Severity Scoring: Calculates fault intensity based on Reconstruction Error (MSE).GenAI Alerts: Employs a Local LLM to generate offline, multilingual warnings for factory floor workers.🏗️ System ArchitectureNode B acts as the bridge between raw signal processing and the end-user.Full System IntegrationCode snippetflowchart LR
    A[Machine Sensor] --> B[Node A<br/>C++ DSP + Spectrogram]
    B -->|ZeroMQ Stream| C[Node B<br/>Python AI Inference]
    C --> D[Anomaly Score]
    C --> E[Worker Alert<br/>Local LLM]
    D --> F[Dashboard / UI]
    E --> F
Internal Logic FlowCode snippetflowchart TD
    Z[ZeroMQ Listener] --> I[ONNX Autoencoder Inference]
    I --> R[Reconstruction Error (MSE)]
    R --> T[Threshold Logic]
    T -->|Normal| N[No Alert]
    T -->|Anomaly| S[Severity Level]
    S --> L[Local LLM Translator]
    L --> W[Worker Warning Message]
🧠 AI Model DesignWe employ a Zero-Shot Anomaly Detection strategy, meaning the system can detect faults it has never seen before by learning what "healthy" sounds like.Model Type: Convolutional Autoencoder (Unsupervised).Input Representation: Log-magnitude spectrogram tensors ($1 \times 1024 \times 64$).Dataset: Trained on the CWRU Bearing Dataset (Normal baseline samples only).Inference Runtime: Optimized using ONNX Runtime for edge hardware compatibility.📁 Project StructurePlaintextpython/
├── inference/          # Core engine: main.py, zmq_listener.py
├── training/           # PyTorch training scripts & ONNX export logic
├── llm/                # Local LLM integration & prompt engineering
├── utils/              # Spectrogram handling & config
├── weights/            # Saved PyTorch (.pth) models
└── onnx/               # Optimized production-ready models
🚀 Getting Started1. InstallationClone the repo and install the required Python environment:Bashpip install -r requirements.txt
2. Running the EngineLaunch the AI Inference Engine to begin listening for Node A:Bashcd python
python inference/main.py
Expected Console Output:Bash[INFO] Autoencoder ONNX model loaded
[NODE B] Resonance AI Inference Started
Listening on tcp://localhost:5555...
📡 Communication Contract (Node A ↔ Node B)Node B expects data in the following format via ZeroMQ (PUB/SUB):ParameterValueProtocolZeroMQEndpointtcp://localhost:5555Frame 0JSON MetadataFrame 1Float32 Spectrogram (Shape: $1 \times 1024 \times 64$)⚡ Engineering HighlightsFully Offline: Operates without cloud dependency, ensuring industrial data privacy.Edge Optimized: High-throughput inference designed for localized hardware.Zero-Shot Capability: Detects unseen mechanical faults by modeling the "Normal Manifold."Modular MLOps: Clean separation between training (Colab/GPU) and deployment (Edge/Python).🚧 Roadmap[ ] Hardware Acceleration: Porting to AMD Ryzen AI NPU using Vitis AI.[ ] Dynamic Thresholding: Implementing data-driven calibration for different machine types.[ ] Containerization: Dockerizing Node B for rapid industrial deployment.Resonance Team | Bridging Industrial Sound and Intelligence.
