import os

# ZeroMQ Settings
# In Docker, use "tcp://host.docker.internal:5555" to connect to host
ZMQ_ENDPOINT = os.environ.get("ZMQ_ENDPOINT", "tcp://localhost:5555")

# Model Settings
INPUT_SHAPE = (1, 1024, 64)  # C, H, W (Channels, Frequency Bins, Time Frames)
LATENT_DIM = 128
MODEL_PATH_PTH = os.path.join(os.path.dirname(__file__), "..", "weights", "autoencoder.pth")
MODEL_PATH_ONNX = os.path.join(os.path.dirname(__file__), "..", "onnx", "autoencoder.onnx")

# Anomaly Detection
# These thresholds should be calibrated based on normal operating data
THRESHOLD_LOW = float(os.environ.get("THRESHOLD_LOW", 0.05))
THRESHOLD_MEDIUM = float(os.environ.get("THRESHOLD_MEDIUM", 0.10))
THRESHOLD_HIGH = float(os.environ.get("THRESHOLD_HIGH", 0.20))

# LLM Settings
# In Docker, use "http://host.docker.internal:11434/api/generate"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
# OLLAMA_MODEL = "phi3" 
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")

# System
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
