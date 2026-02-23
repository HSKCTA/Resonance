import torch
import torch.onnx
import os
import sys

# Adjust path to import model
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from training.model import ConvAutoencoder

def export():
    # Paths
    weights_path = os.path.join(os.path.dirname(__file__), "..", "weights", "autoencoder.pth")
    onnx_dir = os.path.join(os.path.dirname(__file__), "..", "onnx")
    os.makedirs(onnx_dir, exist_ok=True)
    onnx_path = os.path.join(onnx_dir, "autoencoder.onnx")
    
    # Load Model
    model = ConvAutoencoder()
    if os.path.exists(weights_path):
        print(f"Loading weights from {weights_path}")
        model.load_state_dict(torch.load(weights_path))
    else:
        print(f"Warning: No weights found at {weights_path}. Exporting random initialized model.")
    
    model.eval()
    
    # Dummy input for tracing
    dummy_input = torch.randn(1, 1, 1024, 64)
    
    # Export
    print(f"Exporting to {onnx_path}...")
    try:
        torch.onnx.export(
            model,
            dummy_input,
            onnx_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
        )
        print("Export complete.")
    except Exception as e:
        print(f"EXPORT FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        export()
    except Exception as e:
        print(f"SCRIPT FAILED: {e}")
        import traceback
        traceback.print_exc()
