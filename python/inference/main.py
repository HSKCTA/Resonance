import sys
import os
import time
import logging
import numpy as np
import zmq
import json
import base64
import onnxruntime as ort

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.zmq_receiver import ZMQSubscriber
from llm.handler import LLMHandler
from utils import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NodeB")


class ZMQPublisher:
    def __init__(self, endpoint="tcp://*:5557"):
        self.context = zmq.Context()
        self.socket  = self.context.socket(zmq.PUB)
        self.socket.bind(endpoint)
        logger.info(f"Node B Publisher bound to {endpoint}")

    def publish(self, data):
        try:
            self.socket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to publish: {e}")


class InferenceNode:
    def __init__(self):
        self.receiver  = ZMQSubscriber(config.ZMQ_ENDPOINT)
        self.publisher = ZMQPublisher(endpoint="tcp://*:5557")

        # Load ONNX model
        self.ort_session = None
        try:
            if not os.path.exists(config.MODEL_PATH_ONNX):
                logger.error(f"ONNX model not found at {config.MODEL_PATH_ONNX}")
            else:
                logger.info(f"Loading ONNX model from {config.MODEL_PATH_ONNX}")
                self.ort_session = ort.InferenceSession(config.MODEL_PATH_ONNX)
        except Exception as e:
            logger.error(f"Error loading model: {e}")

        # Load normalization stats saved during training
        stats_path = os.path.join(os.path.dirname(config.MODEL_PATH_ONNX),
                                  "..", "weights", "norm_stats.json")
        self.norm_min = 0.0
        self.norm_max = 1.0
        try:
            with open(os.path.abspath(stats_path)) as f:
                stats = json.load(f)
            self.norm_min = stats["global_min"]
            self.norm_max = stats["global_max"]
            logger.info(f"Norm stats loaded: min={self.norm_min:.4f} max={self.norm_max:.4f}")
        except Exception as e:
            logger.warning(f"Could not load norm stats: {e} — using raw values")

        # LLM handler (local endpoint — set LLM_URL / LLM_MODEL env vars)
        self.llm           = LLMHandler()
        self.llm_available = self.llm.check_connection()
        if self.llm_available:
            self.llm.warmup()

    def preprocess(self, tensor_data):
        try:
            data = tensor_data.reshape(1, 1024, 64).astype(np.float32)

            # Apply same normalization used during training
            r = self.norm_max - self.norm_min
            if r > 0:
                data = (data - self.norm_min) / r
            data = np.clip(data, 0.0, 1.0)

            data = np.expand_dims(data, axis=0)  # (1, 1, 1024, 64)
            return data
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return None

    def run(self):
        logger.info("Node B inference started.")
        if self.ort_session is None:
            logger.warning("No model loaded — publishing raw RMS only, MSE will be 0.")

        try:
            while True:
                metadata, raw_data = self.receiver.receive()

                if raw_data is None:
                    time.sleep(0.01)
                    continue

                # Extract RMS from header — published by Node A broadcaster
                rms      = float(metadata.get("rms", 0.0))
                mse      = 0.0
                severity = "NORMAL"

                # Inference
                if self.ort_session is not None:
                    input_tensor = self.preprocess(raw_data)
                    if input_tensor is not None:
                        ort_inputs = {
                            self.ort_session.get_inputs()[0].name: input_tensor
                        }
                        ort_outs      = self.ort_session.run(None, ort_inputs)
                        reconstruction = ort_outs[0]
                        mse = float(np.mean((input_tensor - reconstruction) ** 2))

                # Severity classification
                if mse > config.THRESHOLD_HIGH:
                    severity = "HIGH"
                elif mse > config.THRESHOLD_MEDIUM:
                    severity = "MEDIUM"
                elif mse > config.THRESHOLD_LOW:
                    severity = "LOW"

                # LLM alert + TTS
                alert_text = None
                if severity in ["HIGH", "MEDIUM"]:
                    logger.info(f"Anomaly detected — MSE: {mse:.4f} | Severity: {severity}")
                    if self.llm_available:
                        # generate_alert handles TTS internally (rotates en/hi/mr)
                        alert_text = self.llm.generate_alert(
                            mse, {"severity": severity, "rms": rms}
                        )
                    else:
                        alert_text = (
                            f"Warning: {severity} severity anomaly detected. "
                            f"Check machine components."
                        )

                # Encode spectrogram for dashboard
                spectrogram_b64 = base64.b64encode(raw_data.tobytes()).decode("utf-8")

                # Publish — rms MUST be in payload for dashboard spectrogram
                result_payload = {
                    "timestamp":   time.time(),
                    "mse":         mse,
                    "rms":         rms,          # ← dashboard spectrogram uses this
                    "severity":    severity,
                    "alert":       alert_text,
                    "spectrogram": spectrogram_b64,
                }
                self.publisher.publish(result_payload)

        except KeyboardInterrupt:
            logger.info("Node B stopping...")
        finally:
            self.receiver.close()


if __name__ == "__main__":
    try:
        logger.info("=== Node B starting ===")
        node = InferenceNode()
        logger.info("=== Node B init complete, entering run loop ===")
        node.run()
    except BaseException as e:
        logger.error(f"Node B fatal: {type(e).__name__}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)