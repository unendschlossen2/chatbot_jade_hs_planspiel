# amd_compatibility_test.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_amd_compatibility(model_name="mistralai/Mistral-7B-Instruct-v0.3"):
    print(f"Teste AMD GPU Kompatibilität mit Modell: {model_name}")

    # --- Geräteerkennung ---
    print("\n--- PyTorch Geräteprüfung ---")
    if torch.cuda.is_available():
        print(f"CUDA ist verfügbar: {torch.cuda.is_available()}")
        print(f"Anzahl CUDA Geräte: {torch.cuda.device_count()}")
        print(f"Aktuelles CUDA Gerät: {torch.cuda.current_device()}")
        print(f"CUDA Gerätename: {torch.cuda.get_device_name(torch.cuda.current_device())}")

        # Überprüfe die ROCm-Unterstützung mit torch.version.hip
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            print("ROCm wurde über torch.version.hip erkannt")
            device = "cuda"  # Verwende 'cuda' für das Gerät, wenn ROCm vorhanden ist
        else:
            print("WARNUNG: ROCm (torch.version.hip) nicht erkannt. Verwende CPU.")
            device = "cpu"  # Fallback auf CPU, wenn ROCm nicht korrekt erkannt wird
    else:
        print("CUDA ist nicht verfügbar. Verwende CPU.")
        device = "cpu"

    # --- Modell- und Tokenizer-Laden ---
    print("\n--- Modell- und Tokenizer-Laden ---")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device,  # Verwende das erkannte Gerät
            torch_dtype=torch.float16,  # Verwende float16
        )
        print(f"Modell '{model_name}' erfolgreich geladen auf Gerät: {device}")
    except Exception as e:
        print(f"FEHLER: Modell konnte nicht geladen werden: {e}")
        return  # Beende, wenn das Laden des Modells fehlschlägt

    # --- Einfacher Test ---
    print("\n--- Einfacher Test ---")

    prompt = "Was ist die Hauptstadt von Frankreich?"  # Testprompt
    inputs = tokenizer(prompt, return_tensors="pt").to(device) # Verschiebe Eingabe auf dasselbe Gerät wie das Modell (hoffentlich GPU)

    try:
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=50, do_sample=True, top_k=50, top_p=0.95)

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Prompt: {prompt}")
        print(f"Generierter Text: {generated_text}")

        if device.startswith("cuda"):
            print("\n--- GPU Speichernutzung (nach der Inferenz) ---")
            print(f"Allozierter Speicher: {torch.cuda.memory_allocated(device) / (1024 ** 3):.2f} GB")
            print(f"Gecachter Speicher: {torch.cuda.memory_reserved(device) / (1024 ** 3):.2f} GB")
            print(f"Maximal allozierter Speicher: {torch.cuda.max_memory_allocated(device) / (1024 ** 3):.2f} GB")

    except Exception as e:
        print(f"FEHLER: Inferenz fehlgeschlagen: {e}")

if __name__ == '__main__':
    test_amd_compatibility()
    test_amd_compatibility("NousResearch/Llama-2-7b-chat-hf")
    test_amd_compatibility("stabilityai/stablelm-3b-4e1t")