from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

def load_model_nvidia_quantized(llm_name):
    quantization_config_4bit = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(llm_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            quantization_config=quantization_config_4bit,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{llm_name}' loaded (NVIDIA, 4-bit quantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading quantized model (NVIDIA): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading quantized model (NVIDIA): {e}")
        return None, None
    return model, tokenizer

def load_model_nvidia_unquantized(llm_name):
    tokenizer = AutoTokenizer.from_pretrained(llm_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{llm_name}' loaded (NVIDIA, unquantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading unquantized model (NVIDIA): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading unquantized model (NVIDIA): {e}")
        return None, None
    return model, tokenizer

def load_model_nvidia(llm_name, quantized):
    if quantized:
        return load_model_nvidia_quantized(llm_name)
    else:
        return load_model_nvidia_unquantized(llm_name)