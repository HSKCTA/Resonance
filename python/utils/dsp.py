import numpy as np
import scipy.signal

def compute_spectrogram(signal, fs=12000, n_fft=2048, hop_length=512, n_mels=None):
    """
    Computes spectrogram as per Node A specs:
    - FFT (1024 bins) -> n_fft=2048 gives 1025 bins, we crop to 1024.
    - Log-magnitude
    - Power spectral density
    """
    
    # STFT
    f, t, Zxx = scipy.signal.stft(signal, fs=fs, nperseg=n_fft, noverlap=n_fft-hop_length)
    
    # Magnitude
    mag = np.abs(Zxx)
    
    # Crop to 1024 bins (remove DC or Nyquist if needed, or just slice)
    # n_fft=2048 -> 1025 freq bins. 
    # We take the first 1024.
    mag = mag[:1024, :]
    
    # Log-magnitude (Log10)
    # Add epsilon for numerical stability
    mag = np.log10(mag + 1e-6)
    
    # Ensure 64 frames
    # If we have more, crop. If less, pad?
    # For training, we should slice the input signal to ensure we get >= 64 frames.
    if mag.shape[1] < 64:
        # Pad replication
        pad_width = 64 - mag.shape[1]
        mag = np.pad(mag, ((0, 0), (0, pad_width)), mode='edge')
    
    return mag[:, :64]

def normalize_spectrogram(spec):
    """
    Normalize spectrogram to [0, 1] range based on global stats (estimated)
    or per-sample min/max.
    Prompt says: "Normalization".
    We'll use min-max per sample for now, or robust scaler.
    """
    min_val = spec.min()
    max_val = spec.max()
    if max_val - min_val < 1e-6:
        return spec - min_val
        
    return (spec - min_val) / (max_val - min_val)
