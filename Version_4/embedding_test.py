from sentence_transformers import SentenceTransformer
import chromadb
import ollama
from text_processing import process_text

# --- Configuration for Ollama ---
OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"
# --------------------------------

# --- Embedding Model Setup ---
embedding_model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)
# --------------------------------

# --- Text Processing and Vector DB Setup ---
chunks = process_text()
text_chunks = []
metadata = []
ids = []
for chunk in chunks:
    text_chunks.append(chunk.read_text())
    metadata.append(chunk.read_metadata())
    ids.append(str(chunk.chunk_index))
print("Processed chunks: ", len(text_chunks))

chroma_client = chromadb.Client()
VECTORDB_COLLECTION_NAME = "test_collection_ollama_lib"

try:
    chroma_client.delete_collection(VECTORDB_COLLECTION_NAME)
except Exception:
    pass

collection = chroma_client.create_collection(VECTORDB_COLLECTION_NAME)

print("Generating embeddings for text chunks...")
embeddings = embedding_model.encode(text_chunks) #

print("Adding documents to ChromaDB collection...")
collection.add(embeddings=embeddings.tolist(), metadatas=metadata, ids=ids, documents=text_chunks) #
print("Documents added successfully.")
# --------------------------------

# --- Query and Context Retrieval ---
user_question = "Wie erreiche ich eine hohe Leistungsbereitschaft und Motivation bei meinen Fertigungsmitarbeitern?" #

print("Generating embedding for the query...")
query_embedding = embedding_model.encode(user_question).tolist() #

print("Querying ChromaDB...")
results = collection.query(query_embeddings=[query_embedding], n_results=2) #

print("Query results: ", results)

context_text = ""
if results and results.get('documents') and results['documents'][0]:
    for i, context in enumerate(results['documents'][0]):
        context_text += f"Context-Document {i+1}:\n{context}\n\n" # builds context_text
else:
    print("Warning: No relevant documents found.")
# --------------------------------

system_prompt = f"""
    You are a chatbot for students participating in a simulated management game at university.
    Your task is to answer technical questions about the game, the rules, and the procedures based on the provided context.

    *** Instructions ***
    Answer the question based only on the given context.
    Keep the answer concise and informative, except when a long answer is appropriate or asked for.
    Try to provide general information or an overview if available from the context.
    If the context doesn't contain the answer, say you don't know.
    Always answer in German."""


# --- Prompt Construction ---
prompt = f"""
    Context:
    {context_text}

    Question: {user_question}
    Answer: """

print("\n--- Prompt for LLM ---")
print(prompt)
print("----------------------\n")


# --- LLM Interaction ---
print(f"Sending prompt to Ollama model '{OLLAMA_MODEL}' using ollama library...")

generated_answer = None
response_obj = None
try:
    response_obj = ollama.generate(model=OLLAMA_MODEL,
                                   system=system_prompt,
                                   prompt=prompt,
                                   stream=False
                                   # options={
                                   #     'temperature': 0.6,
                                   #     'top_p': 0.95
                                   # }
                                   )
except Exception as e:
    print(f"Error interacting with Ollama via library: {e}")
    # Print the response object if an error occurred, for inspection
    if response_obj is not None:
        print(f"Debug: Response object state during error: {response_obj}")

# --------------------------------

generated_answer = response_obj.get('response')

# --- Output ---
if generated_answer:
    print(f"\nGenerated Answer (from Ollama lib): {generated_answer}")
else:
    print("\nFailed to get an answer from Ollama.")
# --------------------------------
# Cleanup
try:
    chroma_client.delete_collection(VECTORDB_COLLECTION_NAME)
except Exception:
    pass