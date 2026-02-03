import os
import sys
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from scipy.io import loadmat

# Allow imports from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from utils.spectrogram import vibration_to_spectrogram
from training.autoencoder import ConvAutoencoder


# =============================
# Dataset Loader
# =============================
def load_normal_dataset(data_dir="cwru"):
    specs = []

    for file in os.listdir(data_dir):
        if not file.startswith("Normal"):
            continue

        print(f"[INFO] Loading {file}")

        data = loadmat(os.path.join(data_dir, file))
        signal_key = [k for k in data.keys() if k.endswith("_DE_time")][0]
        signal = data[signal_key]

        spec = vibration_to_spectrogram(signal)
        specs.append(spec)

    if len(specs) == 0:
        raise RuntimeError("No Normal_*.mat files found!")

    X = np.stack(specs, axis=0)  # (N, 1, 1024, 64)
    return torch.tensor(X, dtype=torch.float32)


# =============================
# Training Loop
# =============================
def train():
    print("[INFO] Loading dataset...")
    X = load_normal_dataset("cwru")
    print("[INFO] Dataset shape:", X.shape)

    dataset = TensorDataset(X)
    loader = DataLoader(dataset, batch_size=2, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("[INFO] Using device:", device)

    model = ConvAutoencoder().to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    epochs = 20
    model.train()

    print("[INFO] Starting training...")
    for epoch in range(epochs):
        total_loss = 0.0

        for (x,) in loader:
            x = x.to(device)

            optimizer.zero_grad()
            recon = model(x)
            loss = criterion(recon, x)

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        print(f"[Epoch {epoch+1:02d}/{epochs}] Loss: {avg_loss:.6f}")

    # Save model
    os.makedirs("weights", exist_ok=True)
    save_path = os.path.join("weights", "autoencoder.pth")
    torch.save(model.state_dict(), save_path)

    print(f"[INFO] Model saved to {save_path}")


if __name__ == "__main__":
    train()
