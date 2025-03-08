import torch

# Funktion definiert "device" als GPU, MPS oder CPU

def gpu_load():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Nutze CUDA GPU: {torch.cuda.get_device_name(0)}") # Print GPU name
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Nutze MPS GPU (Apple Silicon)")
    else:
        device = torch.device("cpu")
        print("Nutze CPU-(No GPU detected)")

    return device