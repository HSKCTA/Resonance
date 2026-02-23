# Resonance Node B

AI Inference & Worker Communication Module for Resonance Industrial Monitoring System.

## Overview
Node B receives processed spectrograms from Node A (C++), performs anomaly detection using a Convolutional Autoencoder, and generates worker-friendly alerts via a local LLM (Ollama).

## Structure
- `python/inference/`: Main runtime loop and inference logic.
- `python/training/`: Model definition and training scripts.
- `python/llm/`: Interface for local LLM communication.
- `python/utils/`: Configuration and helper utilities (ZMQ).
- `python/weights/`: PyTorch model checkpoints.
- `python/onnx/`: Exported ONNX models for deployment.
- `python/data/`: CWRU bearing dataset (for training).

## Prerequisites
1. **Python 3.8+**: Ensure Python is installed.
2. **Ollama**: Must be running locally (default: `http://localhost:11434`) with a language model:
   ```bash
   ollama run llama3
   ```
3. **Node A (Signal Engine)**: The C++ signal processing node must be running and publishing to `tcp://localhost:5555`.

## Quick Start for Deployment

1. **Install Dependencies**:
   ```bash
   pip install -r python/requirements.txt
   ```

2. **Verify ONNX Model**:
   Ensure `python/onnx/autoencoder.onnx` exists. If not, see Training section below.

3. **Run Node B**:
   This starts the ZeroMQ subscriber and AI inference engine.
   ```bash
   python python/inference/main.py
   ```
   Node B will now wait for incoming spectrograms from Node A.

## Training (Offline Only)
If you need to retrain the model:
1. Place CWRU `.mat` files in `python/data/cwru/`.
2. Run training script:
   ```bash
   python python/training/train.py
   ```
3. Export new ONNX model:
   ```bash
   python python/training/export_onnx.py
   ```

## Configuration
Edit `python/utils/config.py` to adjust:
- `ZMQ_ENDPOINT`: Address of Node A.
- `THRESHOLD_*`: Anomaly detection sensitivity.
- `OLLAMA_MODEL`: LLM model name (e.g., `llama3`, `phi3`).

## Testing with Simulator
If Node A is not available, run the mock simulator:
```bash
python python/tests/mock_node_a.py
```
Then run Node B in a separate terminal.

## Docker Deployment

### Build
```bash
docker build -t resonance-node-b .
```

### Run
Requires Node A and Ollama running on the host machine.
```bash
docker run -it --rm \
  --add-host=host.docker.internal:host-gateway \
  -e ZMQ_ENDPOINT="tcp://host.docker.internal:5555" \
  -e OLLAMA_URL="http://host.docker.internal:11434/api/generate" \
  resonance-node-b
```
Note: `--add-host` is essential for the container to access services running on `localhost` of the host machine.
