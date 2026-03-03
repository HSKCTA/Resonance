#!/usr/bin/env python3
"""
dataset.py — Resonance Real Motor Dataset
Loads .npy spectrogram files saved by collect_data.py
Place this in python/training/dataset.py
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset


class MotorDataset(Dataset):
    """
    Loads healthy motor spectrogram tensors from a directory of .npy files.
    Each .npy file contains one spectrogram of shape (1, 1024, 64).
    Normalizes to [0, 1] range to match the Sigmoid output of the decoder.
    """

    def __init__(self, data_dir: str):
        self.files = sorted([
            os.path.join(data_dir, f)
            for f in os.listdir(data_dir)
            if f.endswith(".npy")
        ])

        if len(self.files) == 0:
            raise RuntimeError(
                f"No .npy files found in {data_dir}\n"
                f"Run collect_data.py first to capture healthy motor data."
            )

        print(f"[Dataset] Loaded {len(self.files)} samples from {data_dir}")

        # Compute global min/max for normalization across entire dataset
        print("[Dataset] Computing normalization stats...")
        all_data = [np.load(f) for f in self.files]
        stacked  = np.concatenate(all_data, axis=0)
        self.global_min = float(stacked.min())
        self.global_max = float(stacked.max())
        print(f"[Dataset] Range: [{self.global_min:.4f}, {self.global_max:.4f}]")

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        data = np.load(self.files[idx]).astype(np.float32)

        # Normalize to [0, 1] — required for Sigmoid decoder output
        r = self.global_max - self.global_min
        if r > 0:
            data = (data - self.global_min) / r
        data = np.clip(data, 0.0, 1.0)

        return torch.from_numpy(data)