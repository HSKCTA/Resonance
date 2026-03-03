# Resonance — Tier 2: Inference Node

AI-powered vibration anomaly detection with multilingual fault alerts.

## Architecture

```
Node A (C++)                    Node B (Python)                Dashboard
┌──────────────┐   ZMQ 5555   ┌──────────────────┐  ZMQ 5557  ┌──────────┐
│ CM108 Sensor │──────────────│ ONNX Autoencoder │────────────│ Vite App │
│ 44.1kHz ADC  │  1024×64     │ + LLM Alerts     │  JSON      │ :5173    │
│ FFT + Window │  float32     │ + TTS (gTTS)     │            │          │
└──────────────┘              └──────────────────┘            └──────────┘
```

## Structure

```
python/
├── inference/
│   └── main.py              # Node B runtime loop
├── llm/
│   └── handler.py           # LLMProvider → LocalLLM → LLMHandler
├── training/                # Model definition + training scripts
├── utils/
│   ├── config.py            # Thresholds, ZMQ endpoints
│   ├── zmq_receiver.py      # ZMQ subscriber
│   └── rms_monitor.py       # Standalone RMS visualizer
├── tests/
│   ├── mock_node_a.py       # Simulate Node A without hardware
│   └── evaluate_model.py    # Model metrics (MSE, confusion matrix)
├── onnx/
│   ├── autoencoder.onnx     # Exported ONNX model
│   └── model_hash.txt       # SHA-256 integrity hash
├── weights/
│   ├── autoencoder.pth      # PyTorch checkpoint
│   └── norm_stats.json      # Min/max normalization stats
├── run_inference.py         # ← Entry point
├── requirements.txt
└── README.md
```

## Requirements

```bash
pip install -r requirements.txt
```

## Run

```bash
# Start inference (Node A must be running on tcp://localhost:5555)
python run_inference.py
```

### With LLM alerts (optional)

Start a local LLM server, then run:

```bash
# Ollama example
ollama serve &
ollama pull llama3

# Or override endpoint
export LLM_URL="http://localhost:11434/v1/chat/completions"
export LLM_MODEL="mistral:7b"

python run_inference.py
```

## Expected Input

**ZMQ multipart message** on `tcp://localhost:5555`:

| Frame | Content |
|-------|---------|
| 0 | JSON metadata: `{"rms": 0.303, ...}` |
| 1 | Raw bytes: `1024 × 64` float32 spectrogram tensor |

## Output

**ZMQ JSON** published on `tcp://*:5557`:

```json
{
  "timestamp": 1709312345.678,
  "mse": 0.0182,
  "rms": 0.303,
  "severity": "HIGH",
  "alert": "Check motor bearings for wear — shaft imbalance detected."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `mse` | float | Reconstruction error (healthy ≈ 0.0009) |
| `severity` | string | `NORMAL` / `LOW` / `MEDIUM` / `HIGH` |
| `alert` | string \| null | LLM-generated fault diagnosis (when severity ≥ MEDIUM) |

## Thresholds

Edit `utils/config.py`:

| Level | MSE Threshold |
|-------|--------------|
| LOW | > 0.002 |
| MEDIUM | > 0.005 |
| HIGH | > 0.01 |

> **Threshold:** 0.180 (calibrated on healthy baseline data)

## Evaluate Model

```bash
python tests/evaluate_model.py
```

Outputs healthy/fault mean MSE, threshold, and confusion matrix.

## Testing Without Hardware

```bash
python tests/mock_node_a.py   # Simulates Node A
python run_inference.py       # In another terminal
```

## Run with Docker (LLM optional)

1. Start Node A on host:
   ```bash
   ./build/resonance_node_a
   ```

2. Start containers:
   ```bash
   docker compose up --build
   ```

3. Open dashboard:
   ```
   http://localhost:3001
   ```

> **Note:** Local LLM requires model pull (not required for core anomaly detection):
> ```bash
> docker exec -it resonance_ollama ollama pull mistral:7b
> ```
