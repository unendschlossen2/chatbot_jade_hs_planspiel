from sentence_transformers import SentenceTransformer
from older_Versions.Version_2.gpu_Load import gpu_load
from older_Versions.Version_2.model_Load import model_load
from older_Versions.Version_2.rag_answer_gen import rag_chatbot_answer
from older_Versions.Version_2.text_Handler import text_formatting
from older_Versions.Version_2.vectorDB_Gen_Mem import text_embedding_mem
from older_Versions.Version_2.vectorDB_Gen_Pers import text_embedding_perst


def inital_loadup(embedding_model, llm_model_name, quantized, filepaths, use_persistent_DB, force_new_collection):

    #-----------------------------GPU-Modell laden--------------------------------
    device = gpu_load()
    if device is not None:
        print("GPU-Modell erfolgreich geladen.")
    else:
        print("Fehler beim Laden des GPU-Modells.")

    #-----------------------------Texte formatieren--------------------------------
    documents, metadatas, ids = text_formatting(filepaths)
    if documents and metadatas and ids is not None:
        print("Texte formatiert.")

    #-----------------------------Collection erstellen--------------------------------
    if use_persistent_DB:
        collection = text_embedding_perst(embedding_model, force_new_collection, documents, metadatas, ids)
        print("Persistent-Collection erstellt/geladen.")
    else:
        collection = text_embedding_mem(embedding_model, documents, metadatas, ids)
        print("Memory-Collection erstellt/geladen.")
    if collection is not None:
        print("Collection erfolgreich erstellt/geladen.")
    else:
        print("Fehler beim Erstellen/Laden der Collection.")

    #-----------------------------LLM-Modell laden--------------------------------
    model, tokenizer = model_load(llm_model_name, quantized)
    if model and tokenizer is not None:
        print("LLM-Modell erfolgreich geladen.")
    else:
        print("Fehler beim Laden des LLM-Modells.")

    return collection, model, tokenizer, device

#-----------------------------Mainloop--------------------------------

def start_main_loop(collection, model, tokenizer, device):
    while True:
        user_question = input("Du: ")
        response = rag_chatbot_answer(user_question, collection, model, tokenizer, device, embedding_model)
        print("Chatbot:", response)

#-----------------------------Konfiguration--------------------------------

use_persistent_DB = True
force_new_collection = False
filepaths = ["wiki_Data/campus_Card.txt", "wiki_Data/videokonferenz.txt"]
embedding_model = SentenceTransformer('all-mpnet-base-v2')
llm_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
quantized = True

#-----------------------------Programmstart--------------------------------

collection, model, tokenizer, device = inital_loadup(embedding_model, llm_model_name, quantized, filepaths, use_persistent_DB, force_new_collection)
start_main_loop(collection, model, tokenizer, device)