import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using CUDA GPU: {torch.cuda.get_device_name(0)}") # Print GPU name
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using MPS GPU (Apple Silicon)")
else:
    device = torch.device("cpu")
    print("Using CPU (No GPU detected)")

print(f"Device in use: {device}")