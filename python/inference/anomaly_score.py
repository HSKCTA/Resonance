import numpy as np
from utils.config import ANOMALY_THRESHOLD


class AnomalyScorer:
    """
    Handles anomaly scoring and severity classification
    """

    def __init__(self, threshold=ANOMALY_THRESHOLD):
        self.threshold = threshold

    def reconstruction_error(self, original: np.ndarray, reconstructed: np.ndarray) -> float:
        """
        Mean Squared Error between original and reconstructed spectrogram
        """
        return float(np.mean((original - reconstructed) ** 2))

    def is_anomaly(self, score: float) -> bool:
        """
        Decide if anomaly based on threshold
        """
        return score > self.threshold

    def severity(self, score: float) -> str:
        """
        Convert anomaly score to human-readable severity
        """
        if score < self.threshold:
            return "Normal"
        elif score < self.threshold * 2:
            return "Low"
        elif score < self.threshold * 4:
            return "Medium"
        else:
            return "High"
