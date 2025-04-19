import torch

# defines device as GPU, MPS or CPU --- AMD/ROCm or NVIDIA --- OBSOLETE ---

def gpu_load():
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        if "AMD" in device_name or "Radeon" in device_name:
            device = torch.device("cuda")
            print(f"Using AMD ROCm GPU: {device_name}")
        else:
            device = torch.device("cuda")
            print(f"Using CUDA GPU: {device_name}")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using MPS GPU (Apple Silicon)")
    else:
        device = torch.device("cpu")
        print("Using CPU-(No GPU detected)")

    return device