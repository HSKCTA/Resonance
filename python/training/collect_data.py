#!/usr/bin/env python3
"""
collect_data.py — Resonance Healthy Baseline Collector
Run this while your 12V motor is running NORMALLY.
Saves spectrogram tensors from Node A to data/train/

Usage:
    python collect_data.py
    python collect_data.py --samples 300
"""

import os
import argparse
import numpy as np
import zmq
import json
import time


def collect(endpoint: str, output_dir: str, target_samples: int):
    os.makedirs(output_dir, exist_ok=True)

    existing = [f for f in os.listdir(output_dir) if f.endswith(".npy")]
    if existing:
        ans = input(f"[Collector] Found {len(existing)} existing samples. Delete and start fresh? (y/n): ")
        if ans.strip().lower() == "y":
            for f in existing:
                os.remove(os.path.join(output_dir, f))
            print(f"[Collector] Cleared {len(existing)} old samples.")

    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(endpoint)
    sock.setsockopt(zmq.SUBSCRIBE, b"")
    sock.setsockopt(zmq.RCVHWM, 10)

    print(f"\n[Collector] Connected to {endpoint}")
    print(f"[Collector] Target : {target_samples} samples")
    print(f"[Collector] Output : {output_dir}")
    print(f"\n  *** Run your 12V motor at NORMAL speed now ***")
    print(f"  *** Do NOT obstruct or touch it during collection ***")
    print(f"  Press Ctrl+C to stop early.\n")

    collected = 0
    start = time.time()

    try:
        while collected < target_samples:
            if not sock.poll(100, zmq.POLLIN):
                continue
            try:
                frames = sock.recv_multipart(zmq.NOBLOCK)
            except zmq.Again:
                continue

            if len(frames) < 2:
                continue

            try:
                header = json.loads(frames[0])
            except json.JSONDecodeError:
                continue

            bins     = header.get("bins", 1024)
            nframes  = header.get("frames", 64)
            n_floats = bins * nframes

            raw = frames[1]
            if len(raw) < n_floats * 4:
                continue

            tensor = np.frombuffer(raw[:n_floats * 4], dtype=np.float32).copy()
            tensor = tensor.reshape(1, bins, nframes)  # (1, 1024, 64)

            fname = os.path.join(output_dir, f"healthy_{collected:05d}.npy")
            np.save(fname, tensor)
            collected += 1

            elapsed = time.time() - start
            bar_len = 30
            filled  = int(bar_len * collected / target_samples)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"\r  [{bar}] {collected}/{target_samples}  {elapsed:.0f}s", end="", flush=True)

    except KeyboardInterrupt:
        print(f"\n\n[Collector] Stopped by user.")
    finally:
        sock.close()
        ctx.term()
        elapsed = time.time() - start
        print(f"\n[Collector] Saved {collected} samples in {elapsed:.1f}s → {output_dir}")
        if collected < 50:
            print("[WARNING] Collect at least 200 samples for reliable training.")
        else:
            print("[OK] Ready to train. Run: python train.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="tcp://127.0.0.1:5555")
    parser.add_argument("--samples",  type=int, default=200)
    parser.add_argument("--output",   default=os.path.join(
        os.path.dirname(__file__), "..", "data", "train"))
    args = parser.parse_args()
    collect(args.endpoint, os.path.abspath(args.output), args.samples)