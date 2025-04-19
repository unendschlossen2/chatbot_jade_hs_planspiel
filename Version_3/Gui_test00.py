from vectorDB_Gen import text_embedding, reindex_entire_database, reindex_single_file
from rag_answer_gen import rag_chatbot_answer
from llm_Load import model_load
from gpu_Load import gpu_load

from sentence_transformers import SentenceTransformer
from tkinter import ttk
import tkinter as tk
import os

# --- Globale Variablen ---
device = None
model = None
tokenizer = None
collection = None
filepath = "wiki_Data"
llm_model_name = "mistralai/Mistral-7B-Instruct-v0.3"
embedding_model_name = "all-mpnet-base-v2"

# --- Funktionen ---
def load_filepaths():
    print("Dateipfade laden")
    global filepath_list
    filepath_list = os.listdir(filepath)
    filepath_list = [str(filepath + "/" + file) for file in filepath_list] # Correct path joining
    return filepath_list

def generate_ui():
    user_input = input_window.get("1.0", tk.END).strip()
    print(f"Generation gestartet mit Input: '{user_input}' und Context-dokumente: {scalevar_document_number.get()}")
    generated_answer, context_text, reranked_context_text = rag_chatbot_answer(user_input, collection, model, tokenizer, device, embedding_model, int(get_document_slider.get()), scalevar_output_length.get()*75+250, scalevar_output_length.get())
    document_ui(context_text) # Update original context window
    reranked_document_ui(reranked_context_text)
    reranked_document_ui("") # Placeholder for reranked context - will be empty for now

    output_window.config(state=tk.NORMAL)
    output_window.delete("1.0", tk.END)
    output_window.insert(tk.END, generated_answer)
    output_window.config(state=tk.DISABLED)

def document_ui(context_text): # Renamed for clarity - original context
    output_window2.config(state=tk.NORMAL)
    output_window2.delete("1.0", tk.END)
    output_window2.insert(tk.END, context_text)
    output_window2.config(state=tk.DISABLED)

def reranked_document_ui(reranked_context_text): # New function for reranked context
    output_window3.config(state=tk.NORMAL)
    output_window3.delete("1.0", tk.END)
    output_window3.insert(tk.END, reranked_context_text)
    output_window3.config(state=tk.DISABLED)


def open_filepath_popup():
    popup = tk.Toplevel(root)
    popup.title("Dateien-Verwaltung")

    # --- Filepath List Display Section ---
    filepaths_frame = ttk.Frame(popup)
    filepaths_frame.pack(pady=5, padx=10, fill=tk.X)

    filepath_label = ttk.Label(filepaths_frame, text="Dateipfade:")
    filepath_label.pack(pady=5, padx=10, anchor=tk.W)

    filepath_labels_frame = ttk.Frame(filepaths_frame)
    filepath_labels_frame.pack(fill=tk.X)

    def reload_file(filepath_to_reindex): # Renamed parameter for clarity
        print(f"Datei neu indexieren: {filepath_to_reindex}")
        reindex_single_file(embedding_model, database_var.get(), filepath_to_reindex) # Use parameter

    def update_filepath_display():
        for widget in filepath_labels_frame.winfo_children():
            widget.destroy()

        for filepath_item in filepath_list: # Renamed variable for clarity
            file_frame = ttk.Frame(filepath_labels_frame)
            file_frame.pack(fill=tk.X, pady=2)

            file_label = ttk.Label(file_frame, text=filepath_item, width=40, anchor=tk.W) # Use filepath_item
            file_label.pack(side=tk.LEFT, padx=(0, 5))

            reload_button = ttk.Button(file_frame, text="Neu laden", width=10, command=lambda fp=filepath_item: reload_file(fp)) # Use filepath_item in lambda
            reload_button.pack(side=tk.LEFT, padx=2)

    update_filepath_display()


    # --- Reload Database Button ---
    def reload_database_popup():
        global collection
        print("Datenbank komplett neu laden (Popup)")
        collection = reindex_entire_database(embedding_model, database_var.get(), filepath_list)

    reload_db_button = ttk.Button(popup, text="Datenbank komplett neu laden", command=reload_database_popup)
    reload_db_button.pack(pady=10, padx=10)

    # --- Reload Filepaths Button ---
    def reload_filepaths_popup():
        global filepath_list
        print("Dateipfade neu laden (Popup)")
        filepath_list = load_filepaths()
        update_filepath_display() # Just update display, no need to destroy and recreate popup


    reload_filepaths_button = ttk.Button(popup, text="Dateipfade neu Laden", command=reload_filepaths_popup)
    reload_filepaths_button.pack(pady=5, padx=10)

def reload_db_ui():
    global collection
    print("Datenbank komplett neu laden (Main)")
    collection = reindex_entire_database(embedding_model, database_var.get(), filepath_list)


def reload_models_ui():
    global model, tokenizer
    print("Modelle neu laden")
    model, tokenizer = model_load(llm_model_name, quantized_var.get())


# --- Main Window ---
root = tk.Tk()
root.title("Chatbot-MainWindow")

# --- Settings Frame ---
settings_frame = ttk.Frame(root, padding="10")
settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.N))

database_var = tk.BooleanVar(value=False)
database_switch = ttk.Checkbutton(settings_frame, text="Persistente DB verwenden", variable=database_var)
database_switch.pack(pady=5, padx=10, anchor=tk.W)

quantized_var = tk.BooleanVar(value=True)
quantized_switch = ttk.Checkbutton(settings_frame, text="Quantisiert", variable=quantized_var)
quantized_switch.pack(pady=5, padx=10, anchor=tk.W)

# --- Sliders Frame (moved to the left) ---
sliders_frame = ttk.Frame(root, padding="10")
sliders_frame.grid(row=1, column=0, sticky=(tk.W, tk.N))

# --- Approximate-Output-Length Slider---
scalevar_output_length = tk.IntVar()
scalevar_output_length.set(1) # Default to "Mittel" which is index 1 (0=Kurz, 1=Mittel, 2=Lang)
output_length_slider = tk.Scale(sliders_frame, from_=0, to=2, orient="horizontal", variable=scalevar_output_length, tickinterval=1, label="Ausgabelänge (0=Kurz, 1=Mittel, 2=Lang)")
output_length_slider.pack(pady=5, padx=10, anchor=tk.W)

# --- Context-Document-Number Slider ---
scalevar_document_number = tk.IntVar()
scalevar_document_number.set(2)
get_document_slider = tk.Scale(sliders_frame, from_=0, to=5, orient="horizontal", variable=scalevar_document_number, tickinterval=1, label="Anzahl Kontext-Dokumente")
get_document_slider.pack(pady=5, padx=10, anchor=tk.W)


# --- Buttons Frame ---
buttons_frame = ttk.Frame(root, padding="10")
buttons_frame.grid(row=2, column=0, sticky=(tk.W, tk.N))

filepath_button = ttk.Button(buttons_frame, text="Dateipfade verwalten", command=open_filepath_popup, width=20)
filepath_button.pack(pady=5, padx=10, anchor=tk.W)

reload_db_button_main = ttk.Button(buttons_frame, text="DB neu einbetten", command=reload_db_ui, width=20)
reload_db_button_main.pack(pady=5, padx=10, anchor=tk.W)

reload_models_button_main = ttk.Button(buttons_frame, text="Modelle neu laden", command=reload_models_ui, width=20) # Added button for reload models
reload_models_button_main.pack(pady=5, padx=10, anchor=tk.W)

generate_button = ttk.Button(buttons_frame, text="Generieren", command=generate_ui, width=20)
generate_button.pack(pady=5, padx=10, anchor=tk.W)


# --- Chat Window Frame (moved to the right) ---
chat_frame = ttk.Frame(root, padding="10")
chat_frame.grid(row=0, column=1, rowspan=3, sticky=(tk.N, tk.E, tk.S, tk.W))

input_label = ttk.Label(chat_frame, text="Eingabe:")
input_label.pack(pady=5, padx=10, anchor=tk.W)
input_window = tk.Text(chat_frame, height=10, width=100)
input_window.pack(pady=5, padx=10)

output_label = ttk.Label(chat_frame, text="Ausgabe:")
output_label.pack(pady=5, padx=10, anchor=tk.W)
output_window = tk.Text(chat_frame, height=20, width=100, state=tk.DISABLED)
output_window.pack(pady=5, padx=10)


# --- Debug Windows Frame (added to the left) ---
debug_frame = ttk.Frame(root, padding="10")
debug_frame.grid(row=0, column=2, rowspan=3, sticky=(tk.N, tk.S, tk.E, tk.W)) # Placed to the left of chat frame

output_label2 = ttk.Label(debug_frame, text="Original-Dokumente:") # Renamed label
output_label2.pack(pady=5, padx=10, anchor=tk.W)
output_window2 = tk.Text(debug_frame, height=10, width=70, state=tk.DISABLED) # Reduced width, height
output_window2.pack(pady=5, padx=10)

output_label3 = ttk.Label(debug_frame, text="Re-Ranked-Dokumente:") # New label for reranked documents
output_label3.pack(pady=5, padx=10, anchor=tk.W)
output_window3 = tk.Text(debug_frame, height=10, width=70, state=tk.DISABLED) # New text widget for reranked documents
output_window3.pack(pady=5, padx=10)


# --- Modelle festlegen ---
# -------------------------------------------------------------------
embedding_model_to_use = embedding_model_name # Use variable for embedding model name

# --- Variablen definieren ---
filepath_list = load_filepaths()
embedding_model = SentenceTransformer(embedding_model_to_use)
try:
    embedding_model.to("cpu") # Load embedding model to CPU as requested
except Exception as e:
    print(f"Ein Fehler ist aufgetreten {e}")

# --- Initialisierung ---
collection = text_embedding(embedding_model, database_var.get(), filepath_list)
device = gpu_load()
model, tokenizer = model_load(llm_model_name, quantized_var.get())

root.mainloop()