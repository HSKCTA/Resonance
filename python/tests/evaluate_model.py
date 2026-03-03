#!/usr/bin/env python3
"""Evaluate the ONNX autoencoder against healthy and fault vibration data.

Outputs:
  - Healthy mean MSE
  - Fault mean MSE
  - Recommended threshold
  - Confusion matrix

Usage:
    python tests/evaluate_model.py
    python tests/evaluate_model.py --data-dir ../data/cwru
"""

import sys
import os
import argparse
import json
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import onnxruntime as ort
except ImportError:
    print("Install onnxruntime: pip install onnxruntime")
    sys.exit(1)


# ─── Paths ───────────────────────────────────────────────
ROOT = os.path.join(os.path.dirname(__file__), "..")
MODEL_PATH = os.path.join(ROOT, "onnx", "autoencoder.onnx")
STATS_PATH = os.path.join(ROOT, "weights", "norm_stats.json")


def load_model():
    """Load ONNX model and normalization stats."""
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}")
        sys.exit(1)

    session = ort.InferenceSession(MODEL_PATH)

    norm_min, norm_max = 0.0, 1.0
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH) as f:
            stats = json.load(f)
        norm_min = stats["global_min"]
        norm_max = stats["global_max"]
        print(f"Norm stats: min={norm_min:.4f}, max={norm_max:.4f}")

    return session, norm_min, norm_max


def compute_mse(session, data, norm_min, norm_max):
    """Run inference and compute MSE for each sample."""
    mse_values = []
    for sample in data:
        tensor = sample.reshape(1, 1024, 64).astype(np.float32)

        # Normalize
        r = norm_max - norm_min
        if r > 0:
            tensor = (tensor - norm_min) / r
        tensor = np.clip(tensor, 0.0, 1.0)

        # Add batch dim → (1, 1, 1024, 64)
        tensor = np.expand_dims(tensor, axis=0)

        inp_name = session.get_inputs()[0].name
        reconstruction = session.run(None, {inp_name: tensor})[0]
        mse = float(np.mean((tensor - reconstruction) ** 2))
        mse_values.append(mse)

    return np.array(mse_values)


def generate_synthetic_data(n_healthy=50, n_fault=50):
    """Generate synthetic test data when real data isn't available."""
    print("No real data provided — using synthetic test data.\n")

    # Healthy: low-amplitude, smooth patterns
    healthy = []
    for _ in range(n_healthy):
        s = np.random.randn(1024, 64).astype(np.float32) * 0.1
        healthy.append(s)

    # Fault: high-amplitude, spiky patterns
    fault = []
    for _ in range(n_fault):
        s = np.random.randn(1024, 64).astype(np.float32) * 0.5
        # Add random spikes
        n_spikes = np.random.randint(5, 20)
        for _ in range(n_spikes):
            r, c = np.random.randint(0, 1024), np.random.randint(0, 64)
            s[r, c] += np.random.randn() * 3.0
        fault.append(s)

    return np.array(healthy), np.array(fault)


def confusion_matrix(healthy_mse, fault_mse, threshold):
    """Compute and print confusion matrix at given threshold."""
    tp = np.sum(fault_mse > threshold)      # Fault detected as fault
    fn = np.sum(fault_mse <= threshold)     # Fault missed (false negative)
    fp = np.sum(healthy_mse > threshold)    # Healthy flagged as fault
    tn = np.sum(healthy_mse <= threshold)   # Healthy correctly normal

    total = tp + fn + fp + tn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0

    print("=" * 50)
    print("CONFUSION MATRIX")
    print("=" * 50)
    print(f"                  Predicted")
    print(f"                  Fault    Normal")
    print(f"  Actual Fault    {tp:5d}    {fn:5d}")
    print(f"  Actual Normal   {fp:5d}    {tn:5d}")
    print()
    print(f"  Accuracy:   {accuracy:.3f}")
    print(f"  Precision:  {precision:.3f}")
    print(f"  Recall:     {recall:.3f}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Resonance autoencoder")
    parser.add_argument("--data-dir", help="Directory with .npy healthy/fault files")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Override anomaly threshold")
    args = parser.parse_args()

    session, norm_min, norm_max = load_model()

    # Load data
    if args.data_dir and os.path.isdir(args.data_dir):
        healthy_path = os.path.join(args.data_dir, "healthy.npy")
        fault_path = os.path.join(args.data_dir, "fault.npy")
        if os.path.exists(healthy_path) and os.path.exists(fault_path):
            healthy_data = np.load(healthy_path)
            fault_data = np.load(fault_path)
            print(f"Loaded {len(healthy_data)} healthy + {len(fault_data)} fault samples")
        else:
            print(f"Expected healthy.npy and fault.npy in {args.data_dir}")
            healthy_data, fault_data = generate_synthetic_data()
    else:
        healthy_data, fault_data = generate_synthetic_data()

    # Compute MSE
    print("Running inference...")
    healthy_mse = compute_mse(session, healthy_data, norm_min, norm_max)
    fault_mse = compute_mse(session, fault_data, norm_min, norm_max)

    # Statistics
    print()
    print("=" * 50)
    print("MODEL EVALUATION RESULTS")
    print("=" * 50)
    print(f"  Healthy samples:   {len(healthy_mse)}")
    print(f"  Healthy mean MSE:  {healthy_mse.mean():.6f}")
    print(f"  Healthy std MSE:   {healthy_mse.std():.6f}")
    print(f"  Healthy max MSE:   {healthy_mse.max():.6f}")
    print()
    print(f"  Fault samples:     {len(fault_mse)}")
    print(f"  Fault mean MSE:    {fault_mse.mean():.6f}")
    print(f"  Fault std MSE:     {fault_mse.std():.6f}")
    print(f"  Fault min MSE:     {fault_mse.min():.6f}")
    print()

    # Threshold
    threshold = args.threshold
    if threshold is None:
        # Midpoint between healthy max and fault min
        threshold = (healthy_mse.max() + fault_mse.min()) / 2
    print(f"  Threshold:         {threshold:.6f}")

    separation = fault_mse.mean() - healthy_mse.mean()
    print(f"  Separation:        {separation:.6f}")
    print("=" * 50)
    print()

    # Confusion matrix
    confusion_matrix(healthy_mse, fault_mse, threshold)


if __name__ == "__main__":
    main()
