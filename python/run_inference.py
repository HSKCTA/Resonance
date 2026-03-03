#!/usr/bin/env python3
"""Resonance Node B — Entry Point.

Starts the inference node which:
  1. Subscribes to Node A spectrograms via ZMQ (tcp://localhost:5555)
  2. Runs ONNX autoencoder for anomaly detection
  3. Generates LLM fault alerts with TTS (when severity >= MEDIUM)
  4. Publishes results via ZMQ (tcp://*:5557)
"""

import sys
import os

# Ensure python/ is on the path so imports work from project root
sys.path.insert(0, os.path.dirname(__file__))

from inference.main import InferenceNode
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Resonance")


def main():
    try:
        logger.info("=== Resonance Node B starting ===")
        node = InferenceNode()
        logger.info("=== Node B init complete, entering run loop ===")
        node.run()
    except KeyboardInterrupt:
        logger.info("Node B stopped by user.")
    except BaseException as e:
        logger.error(f"Node B fatal: {type(e).__name__}: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
