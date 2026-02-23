import zmq
import numpy as np
import json
import logging

class ZMQSubscriber:
    def __init__(self, endpoint="tcp://localhost:5555"):
        self.endpoint = endpoint
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.endpoint)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "") # Subscribe to all topics
        logging.info(f"Connected to ZMQ endpoint: {self.endpoint}")

    def receive(self):
        try:
            # Receive multipart message
            # Frame 0: JSON Metadata
            # Frame 1: Raw Bytes
            message = self.socket.recv_multipart(flags=zmq.NOBLOCK)
            
            if len(message) < 2:
                logging.warning("Received incomplete message")
                return None, None

            metadata_json = message[0].decode('utf-8')
            metadata = json.loads(metadata_json)
            
            raw_bytes = message[1]
            # Assumes float32 data
            tensor_data = np.frombuffer(raw_bytes, dtype=np.float32)
            
            # Reshape based on valid shape
            # Metadata might contain shape info, but we enforce (1024, 64) for now based on spec
            # Input to model expects (1, 1024, 64), so specific reshaping might be done here or in main
            
            return metadata, tensor_data

        except zmq.Again:
            # No message received
            return None, None
        except Exception as e:
            logging.error(f"Error receiving ZMQ message: {e}")
            return None, None

    def close(self):
        self.socket.close()
        self.context.term()
