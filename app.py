import streamlit as st
from dotenv import load_dotenv
import os
from user_management import UserManager
from document_processing import DocumentProcessor
from rag_utils import RAGQueryEngine

load_dotenv()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    st.title("Document Q&A System")

    user_manager = UserManager()
    doc_processor = DocumentProcessor()
    rag_engine = RAGQueryEngine()

    # Sidebar for user management
    with st.sidebar:
        if st.session_state.user:
            st.write(f"Logged in as: {st.session_state.user}")
            if st.button("Logout"):
                st.session_state.user = None
        else:
            choice = st.radio("Login/Signup", ["Login", "Sign Up"])
            if choice == "Sign Up":
                with st.form("signup_form"):
                    new_user = st.text_input("Username")
                    new_pass = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign Up"):
                        if user_manager.create_user(new_user, new_pass):
                            st.success("User created successfully!")
                        else:
                            st.error("Username already exists!")
            else:
                with st.form("login_form"):
                    user = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        if user_manager.verify_user(user, password):
                            st.session_state.user = user
                            st.experimental_rerun()
                        else:
                            st.error("Invalid username or password")

    # Main app logic
    if st.session_state.user:
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            if st.button("Process Document"):
                doc_processor.process_document(uploaded_file, st.session_state.user)
                st.success("Document processed successfully!")

        query = st.text_input("Enter your question about the documents")
        if query:
            if st.button("Ask"):
                response = rag_engine.query(query, st.session_state.user)
                st.write("Answer:", response)

if __name__ == "__main__":
    main()