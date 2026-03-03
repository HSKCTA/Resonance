#!/usr/bin/env python3
"""
train.py — Resonance Autoencoder Training
==========================================
Trains the ConvAutoencoder on real healthy motor data collected by collect_data.py
Saves weights to python/weights/autoencoder.pth

Usage:
    python train.py
    python train.py --epochs 20 --batch 8
"""

import os
import sys
import json
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from training.model   import ConvAutoencoder
from training.dataset import MotorDataset


def train(epochs: int, batch_size: int, lr: float, data_dir: str):
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[Train] Device     : {DEVICE}")
    print(f"[Train] Epochs     : {epochs}")
    print(f"[Train] Batch size : {batch_size}")
    print(f"[Train] Data dir   : {data_dir}\n")

    # ── Dataset ──────────────────────────────────────────────────────────────
    dataset = MotorDataset(data_dir)

    if len(dataset) < 10:
        print("[ERROR] Need at least 10 samples. Collect more data first.")
        sys.exit(1)

    # 90/10 train/val split
    val_size   = max(1, int(0.1 * len(dataset)))
    train_size = len(dataset) - val_size
    train_ds, val_ds = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,  num_workers=0)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"[Train] Training samples   : {train_size}")
    print(f"[Train] Validation samples : {val_size}\n")

    # ── Model ─────────────────────────────────────────────────────────────────
    model     = ConvAutoencoder().to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)

    weights_dir = os.path.join(os.path.dirname(__file__), "..", "weights")
    os.makedirs(weights_dir, exist_ok=True)
    save_path = os.path.join(weights_dir, "autoencoder.pth")

    best_val_loss = float("inf")

    # ── Training Loop ─────────────────────────────────────────────────────────
    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            batch = batch.to(DEVICE)
            optimizer.zero_grad()
            output = model(batch)
            loss   = criterion(output, batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        train_loss /= len(train_loader)

        # Validate
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                batch  = batch.to(DEVICE)
                output = model(batch)
                val_loss += criterion(output, batch).item()
        val_loss /= len(val_loader)

        scheduler.step(val_loss)

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), save_path)
            saved_marker = " ← saved"
        else:
            saved_marker = ""

        print(f"Epoch {epoch:3d}/{epochs}  "
              f"train_loss={train_loss:.6f}  "
              f"val_loss={val_loss:.6f}{saved_marker}")

    # Save normalization stats for inference
    stats_path = os.path.join(weights_dir, "norm_stats.json")
    stats = {
        "global_min": dataset.global_min,
        "global_max": dataset.global_max
    }
    with open(stats_path, "w") as f:
        json.dump(stats, f)
    print(f"\n[Train] Norm stats saved to  : {stats_path}")

    print(f"[Train] Best validation loss : {best_val_loss:.6f}")
    print(f"[Train] Weights saved to     : {save_path}")
    print(f"\n[Train] Next step: run export_onnx.py to export for inference")
    print(f"        python export_onnx.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",    type=int,   default=15)
    parser.add_argument("--batch",     type=int,   default=4)
    parser.add_argument("--lr",        type=float, default=1e-3)
    parser.add_argument("--data_dir",  default=os.path.join(
        os.path.dirname(__file__), "..", "data", "train"))
    args = parser.parse_args()
    train(args.epochs, args.batch, args.lr, os.path.abspath(args.data_dir))