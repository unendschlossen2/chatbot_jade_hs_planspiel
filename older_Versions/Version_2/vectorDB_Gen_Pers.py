from chromadb.errors import InvalidCollectionException
import chromadb

def text_embedding_perst(embedding_model, force_new_collection, documents, metadatas, ids):
    collection_name = "university_wiki_test"
    persist_path = "vectorDB_Data"
    chroma_client = chromadb.PersistentClient(path=persist_path)

    if force_new_collection:
        chroma_client.delete_collection(collection_name)
        print(f"Force new collection requested. Creating new collection: '{collection_name}'")
        collection = chroma_client.create_collection(collection_name)

        document_embeddings = embedding_model.encode(documents)
        collection.add(embeddings=document_embeddings.tolist(), metadatas=metadatas, ids=ids, documents=documents)

        print(f"Data indexed and added to collection: '{collection_name}'")

    else:
        try:
            collection = chroma_client.get_collection(name=collection_name)
            print(f"Using existing collection: '{collection_name}'")
        except InvalidCollectionException: # Collection does not exist
            print(f"Collection '{collection_name}' not found. Creating new collection and indexing data.")
            collection = chroma_client.create_collection(collection_name)

            document_embeddings = embedding_model.encode(documents)
            collection.add(embeddings=document_embeddings.tolist(), metadatas=metadatas, ids=ids, documents=documents)
            print(f"Data indexed and added to new collection: '{collection_name}'")

    return collection