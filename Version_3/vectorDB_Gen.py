from chromadb.errors import InvalidCollectionException
from text_preprocessing import text_formatting
import chromadb

VECTORDB_COLLECTION_NAME = "university_wiki_test"
VECTORDB_PERSIST_PATH = "vectorDB_Data"

def _get_chroma_client(use_persistent_DB):
    if use_persistent_DB:
        return chromadb.PersistentClient(path=VECTORDB_PERSIST_PATH)
    else:
        return chromadb.Client()

def _get_collection(chroma_client, create_if_missing=True):
    try:
        collection = chroma_client.get_collection(name=VECTORDB_COLLECTION_NAME)
        print(f"Nutze existierende Kollektion: '{VECTORDB_COLLECTION_NAME}'")
        return collection
    except InvalidCollectionException:
        if create_if_missing:
            print(f"Kollektion '{VECTORDB_COLLECTION_NAME}' nicht gefunden. Erstelle neue Kollektion.")
            return chroma_client.create_collection(VECTORDB_COLLECTION_NAME)
        else:
            raise

def reindex_single_file(embedding_model, use_persistent_DB, filepath):
    documents, metadatas, ids = text_formatting([filepath])
    if not documents:
        print(f"Datei: {filepath} ist leer.")
        return

    chroma_client = _get_chroma_client(use_persistent_DB)
    collection = _get_collection(chroma_client)

    document_embeddings = embedding_model.encode(documents)
    collection.update(ids=ids, embeddings=document_embeddings.tolist(), metadatas=metadatas, documents=documents) # Use update instead of add
    print(f"Datei: '{filepath}' updated in Kollektion: '{VECTORDB_COLLECTION_NAME}'")

def reindex_entire_database(embedding_model, use_persistent_DB, filepaths):
    documents, metadatas, ids = text_formatting(filepaths)

    chroma_client = _get_chroma_client(use_persistent_DB)

    try:
        chroma_client.delete_collection(VECTORDB_COLLECTION_NAME)
        print(f"Lösche existierende Kollektion: '{VECTORDB_COLLECTION_NAME}'")
    except ValueError:
        print(f"Keine existierende Kollektion '{VECTORDB_COLLECTION_NAME}' zum löschen vorhanden.")

    collection = chroma_client.create_collection(VECTORDB_COLLECTION_NAME)
    document_embeddings = embedding_model.encode(documents)
    collection.add(embeddings=document_embeddings.tolist(), metadatas=metadatas, ids=ids, documents=documents)
    print(f"Datenbank neu indexiert:'{VECTORDB_COLLECTION_NAME}'")

    return collection


def load_existing_collection(embedding_model, use_persistent_DB, filepaths):
    chroma_client = _get_chroma_client(use_persistent_DB)
    try:
        collection = _get_collection(chroma_client, create_if_missing=False)
        print(f"Kollektion geladen: '{VECTORDB_COLLECTION_NAME}'.")
        return collection
    except InvalidCollectionException:
        print(f"Neue Kollektion erstellen: '{VECTORDB_COLLECTION_NAME}'")
        return reindex_entire_database(embedding_model, use_persistent_DB, filepaths)


def text_embedding(embedding_model, use_persistent_DB, filepaths):
    return load_existing_collection(embedding_model, use_persistent_DB, filepaths)