
def text_formatting(filepaths):
    documents = []
    metadatas = []
    ids = []
    doc_id = 0

    for filepath in filepaths: # Iterate through the list of filepaths
        current_doc_text = ""
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line == "---":
                    if current_doc_text:
                        documents.append(current_doc_text.strip())
                        metadata = {"source": filepath, "title": current_doc_text.split('\n')[0][:50] + "..." if current_doc_text.split('\n')[0] else "Document"}
                        metadatas.append(metadata)
                        ids.append(f"doc_{doc_id}")
                        doc_id += 1
                        current_doc_text = ""
                else:
                    current_doc_text += line + "\n"

    return documents, metadatas, ids