import zmq
import time
import numpy as np
import json
import logging

def mock_node_a():
    logging.basicConfig(level=logging.INFO)
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5555")
    
    logging.info("Mock Node A started. Publishing to tcp://*:5555")
    
    try:
        while True:
            # Simulate processing time
            time.sleep(1.0) 
            
            # Generate fake spectrogram
            # Shape: (1024, 64)
            # Create some "structure" so it's not just white noise
            t = np.linspace(0, 1, 64)
            f = np.linspace(0, 1, 1024).reshape(-1, 1)
            spectrogram = np.sin(2 * np.pi * 5 * t) * np.exp(-f) # Dummy pattern
            spectrogram = spectrogram + 0.1 * np.random.randn(1024, 64) # Add noise
            spectrogram = spectrogram.astype(np.float32)
            
            # Create metadata
            metadata = {
                "timestamp": time.time(),
                "source": "MockSensor",
                "shape": [1024, 64],
                "dtype": "float32"
            }
            
            # Send multipart
            socket.send_json(metadata, flags=zmq.SNDMORE)
            socket.send(spectrogram.tobytes())
            
            logging.info("Published spectrogram data.")
            
    except KeyboardInterrupt:
        logging.info("Stopping Mock Node A...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    mock_node_a()
