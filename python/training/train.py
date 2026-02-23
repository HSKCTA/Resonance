import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import os
import numpy as np

# Adjust path to import model
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from training.model import ConvAutoencoder

# Dummy Dataset class since we don't have CWRU data
class DummyDataset(Dataset):
    def __init__(self, size=100):
        self.size = size

    def __len__(self):
        return self.size

    def __getitem__(self, idx):
        # Generate random spectrogram-like data
        # Valid range [0, 1] for Sigmoid output
        return torch.rand(1, 1024, 64).float()

def train():
    # settings
    BATCH_SIZE = 4
    EPOCHS = 1 # Keep it short for demo
    LR = 1e-3
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Check paths
    weights_dir = os.path.join(os.path.dirname(__file__), "..", "weights")
    os.makedirs(weights_dir, exist_ok=True)
    
    # Data
    print("Initializing dataset...")
    # Try to load real data
    try:
        from training.dataset import CWRUDataset
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "cwru")
        train_dataset = CWRUDataset(data_dir)
        if len(train_dataset) == 0:
            print("Warning: No real data found. Using dummy data for demonstration.")
            train_dataset = DummyDataset()
    except Exception as e:
        print(f"Error loading real data: {e}. Using dummy data.")
        train_dataset = DummyDataset()
        
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    # Model
    model = ConvAutoencoder().to(DEVICE)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    
    # Loop
    print(f"Starting training on {DEVICE} with {len(train_dataset)} samples...")
    model.train()
    for epoch in range(EPOCHS):
        total_loss = 0
        batch_count = 0
        for batch_idx, data in enumerate(train_loader):
            data = data.to(DEVICE)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, data)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            batch_count += 1
            
        avg_loss = total_loss/batch_count if batch_count > 0 else 0
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {avg_loss:.6f}")
        
    # Save
    save_path = os.path.join(weights_dir, "autoencoder.pth")
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    train()
