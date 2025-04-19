import chromadb
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"Using CUDA GPU: {torch.cuda.get_device_name(0)}")  # Print GPU name
elif torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Using MPS GPU (Apple Silicon)")
else:
    device = torch.device("cpu")
    print("Using CPU (No GPU detected)")


# --------------------------------------------

def load_plain_text_data(filepath="example_data_txt.txt"):
    documents = []
    metadatas = []
    ids = []
    doc_id = 0
    current_doc_text = ""  # Now just accumulate text directly
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == "---":
                if current_doc_text:  # If we have accumulated some text
                    documents.append(current_doc_text.strip())
                    # Create simple metadata - you can customize this
                    metadata = {"source": "wiki",
                                "title": current_doc_text.split('\n')[0][:50] + "..." if current_doc_text.split('\n')[
                                    0] else "Document"}  # Basic title from first line
                    metadatas.append(metadata)
                    ids.append(f"doc_{doc_id}")
                    doc_id += 1
                    current_doc_text = ""  # Reset for next document
            else:
                current_doc_text += line + "\n"  # Accumulate text

        # Handle the last document after the loop (if any text remaining)
        if current_doc_text:
            documents.append(current_doc_text.strip())
            metadata = {"source": "wiki",
                        "title": current_doc_text.split('\n')[0][:50] + "..." if current_doc_text.split('\n')[
                            0] else "Document"}  # Basic title from first line
            metadatas.append(metadata)
            ids.append(f"doc_{doc_id}")

    return documents, metadatas, ids


documents, metadatas, ids = load_plain_text_data()

# --------------------------------------------

embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Choose embedding model
chroma_client = chromadb.Client()  # In-memory ChromaDB for local testing
collection = chroma_client.create_collection(name="university_wiki_test")

# 3. Embed and Add Documents to Vector Database
document_embeddings = embedding_model.encode(documents)
collection.add(embeddings=document_embeddings.tolist(), metadatas=metadatas, ids=ids, documents=documents)

# --------------------------------------------

model_name = "mistralai/Mistral-7B-Instruct-v0.3"  # Or "distilgpt2" for smaller test
tokenizer = AutoTokenizer.from_pretrained(model_name)  # Load tokenizer separately

quantization_config_4bit = BitsAndBytesConfig(  # If using quantization
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)  # If no quantization, comment out this block

try:  # Use try-except to catch OOM more gracefully
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config_4bit,  # Or remove if no quantization
        device_map="auto",  # Let transformers handle device placement
        torch_dtype=torch.float16  # Keep dtype explicit
    )
    print("Model loaded successfully (potentially with quantization)")  # Success message
except torch.cuda.OutOfMemoryError as e:
    print(f"OutOfMemoryError during direct model loading: {e}")  # More specific error message
    exit()  # Exit if OOM

print("Tokenizer loaded.")  # Print after tokenizer loads
print("Device map:", model.hf_device_map)  # Print device map to see where layers are placed


# --------------------------------------------

def rag_chatbot_answer(user_question, collection, llm_pipeline, embedding_model):
    query_embedding = embedding_model.encode(user_question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)  # Get top 2 most relevant documents

    contexts = results['documents'][0]  # Documents is a list of lists, take the first (and only) list

    if not contexts:  # No relevant context found
        return "I'm sorry, I couldn't find information related to your question in the wiki."

    # Combine contexts (you can refine this, e.g., take only top context, concatenate, etc.)
    context_text = "\n\n".join(contexts)

    # 6. Construct Prompt for LLM
    prompt = f"""Answer the question based on the context below. If the context doesn't contain the answer, say you don't know.

    Context:
    {context_text}

    Question: {user_question}
    Answer: """

    # 7. Generate Answer using LLM (Corrected llm_pipeline call)
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)  # Encode prompt
    attention_mask = torch.ones_like(input_ids).to(device)  # Create attention mask

    try:  # Use try-except for potential generation errors
        with torch.amp.autocast('cuda'):
            # Corrected llm_output call - pass input_ids directly to model.generate, not pipeline
            llm_output = model.generate(
                input_ids=input_ids,  # Use input_ids as keyword argument
                attention_mask=attention_mask,  # Pass attention_mask
                max_new_tokens=150,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1
            )

        generated_answer = tokenizer.decode(llm_output[0], skip_special_tokens=True)
        generated_answer = generated_answer.split("Answer:")[1].strip()  # Extract answer part

    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError during answer generation in rag_chatbot_answer: {e}")
        return "I'm experiencing memory issues and cannot answer right now. Please try again later."  # User-friendly OOM message
    except Exception as e:
        print(f"Error during answer generation in rag_chatbot_answer: {e}")
        return "I encountered an error while trying to answer. Please try again or ask a different question."  # User-friendly error message

    return generated_answer


# --------------------------------------------

while True:
    user_question = input("You: ")
    response = rag_chatbot_answer(user_question, collection, model, embedding_model)
    print("Chatbot:", response)
