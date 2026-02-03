import os
import sys
import numpy as np
import onnxruntime as ort

# Allow imports from project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)


class AutoencoderInference:
    """
    Autoencoder inference using ONNX Runtime (CPU fallback)
    """

    def __init__(self, onnx_model_path="onnx/autoencoder.onnx"):
        if not os.path.exists(onnx_model_path):
            raise FileNotFoundError(f"ONNX model not found: {onnx_model_path}")

        self.session = ort.InferenceSession(
            onnx_model_path,
            providers=["CPUExecutionProvider"]
        )

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        print("[INFO] Autoencoder ONNX model loaded")

    def reconstruct(self, spec: np.ndarray) -> np.ndarray:
        """
        Reconstruct input spectrogram

        Parameters
        ----------
        spec : np.ndarray
            Shape (1, 1024, 64)

        Returns
        -------
        np.ndarray
            Reconstructed spectrogram (1, 1024, 64)
        """
        if spec.ndim != 3:
            raise ValueError("Input spectrogram must have shape (1, 1024, 64)")

        spec = spec.astype(np.float32)

        output = self.session.run(
            [self.output_name],
            {self.input_name: spec}
        )

        return output[0]
