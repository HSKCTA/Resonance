import os
import glob
import numpy as np
import scipy.io
from torch.utils.data import Dataset
import logging

# Add parent dir to path to allow imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import dsp

class CWRUDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.files = glob.glob(os.path.join(data_dir, "Normal_*.mat"))
        self.samples = []
        self.transform = transform
        
        if not self.files:
            logging.warning(f"No Normal_*.mat files found in {data_dir}")
        else:
            self._load_data()

    def _load_data(self):
        logging.info(f"Loading data from {len(self.files)} files...")
        
        for fpath in self.files:
            try:
                mat = scipy.io.loadmat(fpath)
                
                # Find time series key (DE or FE)
                key = None
                for k in mat.keys():
                    if k.endswith("_DE_time"):
                        key = k
                        break
                    elif k.endswith("_FE_time"):
                        key = k # Fallback
                
                if key is None:
                    # Fallback for weirdly named files (like raw arrays)
                    # Use largest array?
                    # Or specific to Normal_*.mat if they are custom.
                    # Let's inspect shapes.
                    for k in mat.keys():
                        if not k.startswith("__") and isinstance(mat[k], np.ndarray):
                            if mat[k].ndim == 2 and (mat[k].shape[0] > 10000 or mat[k].shape[1] > 10000):
                                key = k
                                break
                
                if key:
                    signal = mat[key].flatten()
                    self._process_signal(signal)
                else:
                    logging.warning(f"Could not find time-series data in {fpath}")

            except Exception as e:
                logging.error(f"Error loading {fpath}: {e}")
        
        logging.info(f"Loaded {len(self.samples)} samples.")

    def _process_signal(self, signal):
        # We need chunks that produce (1024, 64) spectrograms.
        # DSP uses n_fft=2048, hop=512.
        # (64 frames) * 512 hop + (2048 - 512) = 32768 + 1536 = 34304 samples approx?
        # Let's verify: 
        # t = (N_frames - 1) * hop + n_fft
        # Samples needed = (64 - 1) * 512 + 2048 = 32256 + 2048 = 34304.
        
        chunk_size = 34304
        stride = 16384 # 50% overlap for data augmentation
        
        for i in range(0, len(signal) - chunk_size, stride):
            chunk = signal[i:i+chunk_size]
            
            # Generate Spectrogram
            spec = dsp.compute_spectrogram(chunk, fs=12000, n_fft=2048, hop_length=512)
            
            # Normalize
            spec = dsp.normalize_spectrogram(spec)
            
            # Check shape (should be 1024, 64)
            if spec.shape == (1024, 64):
                self.samples.append(spec)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        # Returns (1, 1024, 64) tensor
        spec = self.samples[idx]
        return np.expand_dims(spec, axis=0).astype(np.float32)

if __name__=="__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    ds = CWRUDataset("python/data/cwru")
    if len(ds) > 0:
        print(f"Sample shape: {ds[0].shape}")
    else:
        print("No samples loaded.")
