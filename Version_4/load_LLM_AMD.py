from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def load_model_amd(llm_name):
    tokenizer = AutoTokenizer.from_pretrained(llm_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(
            llm_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print(f"Model '{llm_name}' loaded (AMD/CPU, unquantized)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError loading model (AMD/CPU, unquantized): {e}")
        return None, None
    except Exception as e:
        print(f"Error loading model (AMD/CPU, unquantized): {e}")
        return None, None
    return model, tokenizer