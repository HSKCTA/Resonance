import sys
import os
import time
import logging
import numpy as np
import zmq
import json
import base64
import onnxruntime as ort

# Add parent dir to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.zmq_receiver import ZMQSubscriber
from llm.handler import LLMHandler
from utils import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NodeB")

class ZMQPublisher:
    def __init__(self, endpoint="tcp://*:5556"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(endpoint)
        logger.info(f"Node B Results Publisher bound to {endpoint}")

    def publish(self, data):
        try:
            self.socket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to publish results: {e}")

class InferenceNode:
    def __init__(self):
        self.receiver = ZMQSubscriber(config.ZMQ_ENDPOINT)
        self.publisher = ZMQPublisher(endpoint="tcp://*:5557")
        
        # Load ONNX Model
        try:
            if not os.path.exists(config.MODEL_PATH_ONNX):
                logger.error(f"ONNX model not found at {config.MODEL_PATH_ONNX}")
            else:
                logger.info(f"Loading model from {config.MODEL_PATH_ONNX}")
                self.ort_session = ort.InferenceSession(config.MODEL_PATH_ONNX)
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.ort_session = None

        # LLM Handler
        self.llm = LLMHandler(url=config.OLLAMA_URL, model=config.OLLAMA_MODEL)
        self.llm_available = self.llm.check_connection()
        
    def preprocess(self, tensor_data):
        try:
            data = tensor_data.reshape(1, 1024, 64)
            data = np.expand_dims(data, axis=0)
            return data
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return None

    def run(self):
        logger.info("Starting Inference Node...")
        if self.ort_session is None:
             logger.warning("No model loaded. Running in pass-through mode (no inference).")

        try:
            while True:
                # Receive data from Node A
                metadata, raw_data = self.receiver.receive()
                
                if raw_data is None:
                    time.sleep(0.01)
                    continue
                
                mse = 0.0
                severity = "NORMAL"
                spectrogram_b64 = ""

                # Preprocess & Inference
                if self.ort_session:
                    input_tensor = self.preprocess(raw_data)
                    if input_tensor is not None:
                        ort_inputs = {self.ort_session.get_inputs()[0].name: input_tensor}
                        ort_outs = self.ort_session.run(None, ort_inputs)
                        reconstruction = ort_outs[0]
                        mse = float(np.mean((input_tensor - reconstruction) ** 2))
                
                # Check Thresholds
                if mse > config.THRESHOLD_HIGH:
                    severity = "HIGH"
                elif mse > config.THRESHOLD_MEDIUM:
                    severity = "MEDIUM"
                elif mse > config.THRESHOLD_LOW:
                    severity = "LOW"
                
                # Encode spectrogram for visualization
                # Using 1024x64 float32 is heavy, but we'll send it for the modern dashboard
                spectrogram_b64 = base64.b64encode(raw_data.tobytes()).decode('utf-8')

                # Handle Anomaly & Alerts
                alert_text = None
                if severity != "NORMAL":
                     logger.info(f"Anomaly Detected! MSE: {mse:.4f} | Severity: {severity}")
                     if self.llm_available and severity in ["HIGH", "MEDIUM"]:
                         # Rate limit or logic here
                         alert_text = f"Warning: {severity} severity anomaly detected. Check machine components."

                # Publish Results to Dashboard (Node.js)
                result_payload = {
                    "timestamp": time.time(),
                    "mse": mse,
                    "severity": severity,
                    "alert": alert_text,
                    "spectrogram": spectrogram_b64
                }
                self.publisher.publish(result_payload)
                
        except KeyboardInterrupt:
            logger.info("Stopping Node B...")
        finally:
            self.receiver.close()

if __name__ == "__main__":
    node = InferenceNode()
    node.run()
