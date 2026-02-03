# training/autoencoder.py

import torch
import torch.nn as nn


class ConvAutoencoder(nn.Module):
    """
    Convolutional Autoencoder for Spectrogram Anomaly Detection
    Input shape  : (B, 1, 1024, 64)
    Output shape : (B, 1, 1024, 64)
    """

    def __init__(self):
        super().__init__()

        # -------------------------
        # Encoder
        # -------------------------
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1),   # (16, 512, 32)
            nn.ReLU(),

            nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1),  # (32, 256, 16)
            nn.ReLU(),

            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),  # (64, 128, 8)
            nn.ReLU(),
        )

        # -------------------------
        # Decoder
        # -------------------------
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(
                64, 32, kernel_size=3, stride=2, padding=1, output_padding=1
            ),  # (32, 256, 16)
            nn.ReLU(),

            nn.ConvTranspose2d(
                32, 16, kernel_size=3, stride=2, padding=1, output_padding=1
            ),  # (16, 512, 32)
            nn.ReLU(),

            nn.ConvTranspose2d(
                16, 1, kernel_size=3, stride=2, padding=1, output_padding=1
            ),  # (1, 1024, 64)
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out
