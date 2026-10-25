# Display the UI, accept uploads and show answers

import streamlit as st
from rag.config import DATA_DIR
from rag.document_loader import load_documents
from rag.text_splitter import split_documents
from rag.vector_store import build_vector_store, load_vector_store
from rag.rag_chain import answer_question

st.title("Simple RAG Document Assistant")

uploaded_files = st.file_uploader(
    "Upload PDF or TXT files",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if st.button("Index documents"):
    for uploaded_file in uploaded_files or []:
        (DATA_DIR / uploaded_file.name).write_bytes(uploaded_file.getbuffer())

    documents = load_documents()
    chunks = split_documents(documents)
    build_vector_store(chunks)
    st.success("Documents indexed successfully")

question = st.text_input("Ask a question")

if st.button("Ask") and question:
    store = load_vector_store()

    if store is None:
        st.warning("No documents indexed yet. Click 'Index documents' first.")
    else:
        result = answer_question(question, store)
        st.write(result["answer"])
        st.write(result["sources"])