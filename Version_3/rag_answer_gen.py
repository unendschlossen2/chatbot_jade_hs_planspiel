import torch

def rag_chatbot_answer(user_question, collection, model, tokenizer, device, embedding_model, get_document_number, output_length_max, output_length_penalty):
    print(output_length_max, output_length_penalty)
    query_embedding = embedding_model.encode(user_question).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=get_document_number)
    contexts_initial = results['documents'][0] # Initial retrieved documents

    # 2. Create dynamic document list string for prompt
    documents_section = ""
    for i, doc_text in enumerate(contexts_initial): # Add each document to the documents_section string
        documents_section += f"--- Document {i+1} ---\n{doc_text}\n" # Changed to English "Document" for consistency

    # 3. Create combined prompt with all documents for relevance rating
    prompt_combined_docs = f"""
    Evaluate the relevance of the following documents for answering the user's question. 
    The documents are seperated by '--- Document ---', the number of ratings should match the number of documents.
    For each document, provide a separate rating on a scale of 1 to 5, where 5 means 'very relevant' and 1 means 'not relevant'.
    Output the ratings as a comma-separated list of numbers, in the same order as the documents.
    Only output the ratings, do not include any other text.

    User question: {user_question}

    Context-documents:
    {documents_section}

    Relevancy-rating(comma-seperated List): """

    # 4. Encode combined prompt and perform single inference for relevance ratings
    input_ids_combined = tokenizer.encode(prompt_combined_docs, return_tensors="pt").to(device)
    attention_mask_combined = torch.ones_like(input_ids_combined).to(device)

    with torch.no_grad(), torch.amp.autocast('cuda'):
        llm_output_combined = model.generate(
            input_ids=input_ids_combined,  # input_ids als keyword argument verwenden
            attention_mask=attention_mask_combined,  # attention_mask übergeben
            pad_token_id=tokenizer.eos_token_id,
            num_return_sequences=1,
            max_new_tokens=output_length_max,
            length_penalty=output_length_penalty,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.6,
            use_cache=True,
            num_beams=5
        )

    decoded_output = tokenizer.decode(llm_output_combined[0], skip_special_tokens=True).strip() # Decode ENTIRE output
    print(f"Raw LLM output for ratings: {decoded_output}") # Print raw output for debugging

    # 5. Robustly Parse ratings from LLM output
    document_relevance_scores = []

    marker_string = "Relevancy-rating(comma-seperated List):" # Define the marker string

    marker_index = decoded_output.find(marker_string) # Find the index of the marker string

    if marker_index != -1: # Marker string found in the output
        ratings_str = decoded_output[marker_index + len(marker_string):].strip() # Extract text AFTER the marker
        print(f"Extracted ratings string: {ratings_str}") # Print extracted ratings string
    else:
        print(f"Warning: Marker string '{marker_string}' not found in LLM output. Cannot parse ratings.")
        print(f"Full LLM output: '{decoded_output}'") # Print full output for debugging
        document_relevance_scores = [{'document': doc_text, 'score': 1} for doc_text in contexts_initial] # Fallback to default ratings, and return early
        return "I'm sorry, there was an issue processing the document ratings. Please try again.", "", "", document_relevance_scores # Return with error message and empty contexts

    try: # Parsing ratings string (same parsing logic as before)
        ratings_list_str = ratings_str.split(',') # Split comma-separated string into list of strings
        ratings = [int(rating_str.strip()) for rating_str in ratings_list_str] # Convert to integers, strip whitespace
        if len(ratings) != len(contexts_initial): # Check if we got the expected number of ratings
            print(f"Warning: Number of ratings ({len(ratings)}) does not match number of documents ({len(contexts_initial)}).")
            ratings = ratings[:len(contexts_initial)] # Truncate to match document count

        for i, document_text in enumerate(contexts_initial):
            relevance_score = ratings[i] if i < len(ratings) else 1 # Default to low score if rating is missing
            relevance_score = max(1, min(relevance_score, 5)) # Clamp to 1-5 range
            document_relevance_scores.append({'document': document_text, 'score': relevance_score})

    except ValueError: # Handle parsing errors
        print(f"Warning: Error parsing ratings list: '{ratings_str}'. Setting all ratings to 1.")
        document_relevance_scores = [{'document': doc_text, 'score': 1} for doc_text in contexts_initial] # Default to low score for all

    # 6. Rerank documents by score (rest of the code remains the same)
    print(document_relevance_scores)
    document_relevance_scores = [item for item in document_relevance_scores if item['score'] > 3]
    print(document_relevance_scores)
    reranked_documents = sorted(document_relevance_scores, key=lambda x: x['score'], reverse=True)
    contexts_reranked = [item['document'] for item in reranked_documents]

    context_text = ""
    for i, context in enumerate(contexts_reranked):
        context_text += f"Context-Document {i+1}:\n{context}\n\n" # Changed to English "Context" for consistency

    # System Prompt - Updated to English and more specific
    prompt = f"""
    You are a chatbot for students participating in a simulated management game at university.
    Your task is to answer technical questions about the game, the rules, and the procedures based on the provided context.

    *** Instructions ***
    Answer the question based only on the given context.
    Keep the answer concise and informative, except when a long answer is appropriate or asked for.
    Try to provide general information or an overview if available from the context.
    If the context doesn't contain the answer, say you don't know.
    Always answer in German.

    Context:
    {context_text}

    Question: {user_question}
    Answer: """

    print(f"\nPrompt für Antwortgenerierung für {len(reranked_documents)} Dokumente: {prompt}")
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)  # prompt encodieren
    attention_mask = torch.ones_like(input_ids).to(device)  # attention mask erstellen

    try:
        with torch.amp.autocast('cuda'):
            llm_output = model.generate(
                input_ids=input_ids,  # input_ids als keyword argument verwenden
                attention_mask=attention_mask,  # attention_mask übergeben
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1,
                max_new_tokens=output_length_max,
                length_penalty=output_length_penalty,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.6,
                use_cache=True,
                num_beams=5
            )

        generated_answer = tokenizer.decode(llm_output[0], skip_special_tokens=True)
        generated_answer = generated_answer.split("Answer:")[1].strip()  # Extract answer part

    except torch.cuda.OutOfMemoryError as e:
        print(f"OutOfMemoryError bei der Antwortgenerierung!: {e}")
        return "Please try again later. / Bitte versuchen Sie es später erneut."
    except Exception as e:
        print(f"Fehler bei der Antwortgenerierung! {e}")
        return "Please try again later. / Bitte versuchen Sie es später erneut."

    return generated_answer, context_text, reranked_documents