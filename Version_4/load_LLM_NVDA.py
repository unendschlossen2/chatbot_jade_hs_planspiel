from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

def load_model_nvidia_quantized(LLM_name):
    quantization_config_4bit = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(LLM_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            LLM_name,
            quantization_config=quantization_config_4bit,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{LLM_name}' loaded (NVIDIA, 4-Bit quantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading model (NVIDIA): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading model (NVIDIA): {e}")
        return None, None
    return model, tokenizer

def load_model_nvidia_unquantized(LLM_name):
    tokenizer = AutoTokenizer.from_pretrained(LLM_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            LLM_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{LLM_name}' loaded (NVIDIA unquantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading unquantized model (NVIDIA): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading unquantized model (NVIDIA): {e}")
        return None, None
    return model, tokenizer

def load_model_nvidia(LLM_name, quantized):
    if quantized:
        return load_model_nvidia_quantized(LLM_name)
    else:
        return load_model_nvidia_unquantized(LLM_name)