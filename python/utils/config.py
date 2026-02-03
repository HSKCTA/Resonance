# utils/config.py

# =============================
# Spectrogram parameters
# =============================

WINDOW_SIZE = 4096          # Samples per FFT window
FFT_BINS = 1024             # Frequency bins kept
FRAMES = 64                 # Time frames per spectrogram

INPUT_SHAPE = (1, FFT_BINS, FRAMES)


# =============================
# Anomaly Detection
# =============================

# Initial threshold for reconstruction error
# (will be tuned later using validation data)
ANOMALY_THRESHOLD = 0.08


# =============================
# Runtime / Performance
# =============================

DTYPE = "float32"
