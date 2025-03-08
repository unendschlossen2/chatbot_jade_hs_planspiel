import torch

# Defines device as NVIDIA / AMD GPU, Apple MPS, or CPU

def gpu_load():
    if torch.cuda.is_available():
        try:
            device_name = torch.cuda.get_device_name(0)
            if "AMD" in device_name or "Radeon" in device_name:
                print(f"Using AMD ROCm GPU: {device_name}")
            else:
                print(f"Using NVIDIA CUDA GPU: {device_name}")
        except RuntimeError as e:
            print(f"CUDA GPU detected, but error getting device name: {e}")
            print("Falling back to CPU.")
            return torch.device("cpu")
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        print("Using MPS GPU (Apple Silicon)")
        return torch.device("mps")
    else:
        print("Using CPU (No GPU detected)")
        return torch.device("cpu")