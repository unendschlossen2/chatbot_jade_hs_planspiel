from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

def model_load(llm_model_name, quantized):
    tokenizer = AutoTokenizer.from_pretrained(llm_model_name) # Tokenizer laden

    if not quantized:
        model = model_load_unquantized(llm_model_name)
    else:
        model = model_load_quantized(llm_model_name)

    return model, tokenizer

def model_load_unquantized(llm_model_name):

    try:
        model = AutoModelForCausalLM.from_pretrained(
            llm_model_name,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print("Modell erfolgreich geladen!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError beim Laden des Modells: {e}")
        exit()

    return model

def model_load_quantized(llm_model_name):

    quantization_config_4bit = BitsAndBytesConfig(  # If using quantization
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    try:
        model = AutoModelForCausalLM.from_pretrained(
            llm_model_name,
            quantization_config=quantization_config_4bit,
            device_map="auto",
            torch_dtype=torch.float16
        )
        print("Modell erfolgreich geladen (potenziell quantisiert)!")
    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError beim Laden des Modells: {e}")
        exit()

    return model