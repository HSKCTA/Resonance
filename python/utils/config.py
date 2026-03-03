import os

# ZeroMQ Settings
# Local: tcp://localhost:5555 | Docker: tcp://host.docker.internal:5555
ZMQ_ENDPOINT = os.environ.get("ZMQ_ENDPOINT", "tcp://host.docker.internal:5555")

# Model Settings
INPUT_SHAPE = (1, 1024, 64)  # C, H, W (Channels, Frequency Bins, Time Frames)
LATENT_DIM = 128
MODEL_PATH_PTH = os.path.join(os.path.dirname(__file__), "..", "weights", "autoencoder.pth")
MODEL_PATH_ONNX = os.path.join(os.path.dirname(__file__), "..", "onnx", "autoencoder.onnx")

# Anomaly Detection
# Calibrated from healthy motor baseline: MSE mean=0.000908, max=0.000923
THRESHOLD_LOW = float(os.environ.get("THRESHOLD_LOW", 0.002))     # ~2x healthy ceiling
THRESHOLD_MEDIUM = float(os.environ.get("THRESHOLD_MEDIUM", 0.005))
THRESHOLD_HIGH = float(os.environ.get("THRESHOLD_HIGH", 0.01))

# LLM Settings (handler.py reads these env vars directly)
LLM_URL = os.environ.get("LLM_URL", "http://localhost:11434/v1/chat/completions")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama-3.1-8b")

# System
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
