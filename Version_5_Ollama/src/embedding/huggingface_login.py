from huggingface_hub import login

def huggingface_hub_login(token: str):
    login(token)
    print("Logged in to Hugging Face Hub successfully.")
    return True