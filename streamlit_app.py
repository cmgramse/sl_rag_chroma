import streamlit as st
import tempfile
import os
from rag_utils import ingest_pdf, search_rag

st.title("Streamlit RAG App with Unstructured PDF Processing")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    if st.button("Ingest PDF"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        ingest_pdf(tmp_file_path)
        os.unlink(tmp_file_path)  # Remove the temporary file
        st.success("PDF ingested successfully!")

query = st.text_input("Enter your question")
if st.button("Search"):
    if query:
        result = search_rag(query)
        st.subheader("Result:")
        st.write(result)
    else:
        st.error("Please enter a question to search.")