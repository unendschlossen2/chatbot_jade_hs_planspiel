import streamlit as st

def generate_window():
    st.title("Planspiel Chatbot")
    st.write("Willkommen zum Planspiel Chatbot!")

    user_question = st.text_input("Bitte geben Sie Ihre Frage ein:")

    if st.button("Bestätigen"):
        if user_question:
            generated_answer = "PLATZHALTER FÜR DIE GENERIERTE ANTWORT"

            st.write("Antwort:")
            st.write(generated_answer)
        else:
            st.warning("Bitte Frage eingeben.")