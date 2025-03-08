from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_model_amd(LLM_name):
    tokenizer = AutoTokenizer.from_pretrained(LLM_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            LLM_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{LLM_name}' loaded (AMD unquantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading model (AMD): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading model (AMD): {e}")
        return None, None
    return model, tokenizer