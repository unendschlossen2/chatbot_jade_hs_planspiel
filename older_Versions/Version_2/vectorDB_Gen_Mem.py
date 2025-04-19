import chromadb

def text_embedding_mem(embedding_model, documents, metadatas, ids):
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="university_wiki_test")

    document_embeddings = embedding_model.encode(documents)
    collection.add(embeddings=document_embeddings.tolist(), metadatas=metadatas, ids=ids, documents=documents)

    return collection