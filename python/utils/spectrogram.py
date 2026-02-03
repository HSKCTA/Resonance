# utils/spectrogram.py

import numpy as np


def vibration_to_spectrogram(
    signal,
    window_size=4096,
    fft_bins=1024,
    frames=64
):
    """
    Convert raw vibration signal into a spectrogram tensor
    of shape (1, 1024, 64)

    Parameters
    ----------
    signal : np.ndarray
        Raw vibration signal (1D or 2D from .mat file)
    window_size : int
        Number of samples per FFT window
    fft_bins : int
        Number of frequency bins to keep
    frames : int
        Number of time frames in spectrogram

    Returns
    -------
    np.ndarray
        Spectrogram of shape (1, fft_bins, frames)
    """

    # Ensure 1D signal
    signal = np.asarray(signal).flatten()

    hop = window_size
    spec_frames = []

    for i in range(frames):
        start = i * hop
        end = start + window_size

        if end > len(signal):
            break

        window = signal[start:end]

        # FFT
        fft_vals = np.fft.fft(window)
        fft_mag = np.abs(fft_vals[: window_size // 2])

        # Keep only required frequency bins
        fft_mag = fft_mag[:fft_bins]

        spec_frames.append(fft_mag)

    if len(spec_frames) == 0:
        raise ValueError("Signal too short to create spectrogram")

    # Stack into (freq, time)
    spec = np.stack(spec_frames, axis=1)

    # Normalize (zero mean, unit variance)
    spec = spec.astype(np.float32)
    spec = (spec - spec.mean()) / (spec.std() + 1e-8)

    # Pad time axis if needed
    if spec.shape[1] < frames:
        pad_amount = frames - spec.shape[1]
        spec = np.pad(spec, ((0, 0), (0, pad_amount)), mode="constant")

    # Add channel dimension -> (1, 1024, 64)
    spec = np.expand_dims(spec, axis=0)

    return spec
