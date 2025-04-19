import torch

def rag_chatbot_answer(user_question, collection, model, tokenizer, device, embedding_model):
    query_embedding = embedding_model.encode(user_question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=2)  # Die 2 relevantesten Dokumente abrufen

    contexts = results['documents'][0]  # Dokumente sind eine Liste von Listen, die erste (und einzige) Liste nehmen

    if not contexts:  # No relevant context found
        return "Es tut mir leid, aber ich konnte keine relevante Antwort auf deine Frage finden."

    # context kombinieren (Subjekt für Änderungen, z. B. nur den obersten Kontext nehmen, verketten usw.)
    context_text = "\n\n".join(contexts)

    # System Prompt
    prompt = f"""
    Answer the question in German, based on the context below. 
    Try to provide general information or an overview if available.
    Keep the answer concise and informative.
    If the context doesn't contain the answer, say you don't know.

    Context:
    {context_text}

    Question: {user_question}
    Answer: """

    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)  # prompt encodieren
    attention_mask = torch.ones_like(input_ids).to(device)  # attention mask erstellen

    try:
        with torch.amp.autocast('cuda'):
            llm_output = model.generate(
                input_ids=input_ids,  # input_ids als keyword argument verwenden
                attention_mask=attention_mask,  # attention_mask übergeben
                max_new_tokens=150,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1
            )

        generated_answer = tokenizer.decode(llm_output[0], skip_special_tokens=True)
        generated_answer = generated_answer.split("Answer:")[1].strip()  # Extract answer part

    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError bei der Antwortgenerierung!: {e}")
        return "Please try again later. / Bitte versuchen Sie es später erneut."
    except Exception as e:
        print(f"Fehler bei der Antwortgenerierung! {e}")
        return "Please try again later. / Bitte versuchen Sie es später erneut."

    return generated_answer