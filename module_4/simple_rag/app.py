
import os
import streamlit as st
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

DATA_DIR = Path("data")
DB_DIR = "chroma_db"

st.set_page_config(page_title="Simple RAG", page_icon="📚")
st.title("Simple RAG Document Assistant")

DATA_DIR.mkdir(exist_ok=True)

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def load_documents():
    documents = []

    for file in DATA_DIR.iterdir():
        if file.suffix.lower() == ".pdf":
            loader = PyPDFLoader(str(file))
            pages = loader.load()
        elif file.suffix.lower() == ".txt":
            loader = TextLoader(str(file), encoding="utf-8")
            pages = loader.load()
        else:
            continue

        for page in pages:
            page.metadata["source"] = file.name

        documents.extend(pages)

    return documents

def build_vector_store():
    documents = load_documents()

    if not documents:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120
    )

    chunks = splitter.split_documents(documents)

    return Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=DB_DIR
    )

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

with st.sidebar:
    st.header("Document controls")

    uploaded_files = st.file_uploader(
        "Upload PDF or TXT files",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )

    if st.button("Index documents", type="primary"):
        if uploaded_files:
            for uploaded in uploaded_files:
                safe_name = Path(uploaded.name).name
                (DATA_DIR / safe_name).write_bytes(uploaded.getvalue())

        with st.spinner("Loading, splitting and indexing documents..."):
            try:
                st.session_state.vector_store = build_vector_store()
                if st.session_state.vector_store:
                    st.success("Documents indexed successfully.")
                else:
                    st.warning("Put PDF or TXT documents in the data folder.")
            except Exception as error:
                st.error(f"Indexing failed: {error}")

if st.session_state.vector_store is None:
    if Path(DB_DIR).exists():
        try:
            st.session_state.vector_store = Chroma(
                persist_directory=DB_DIR,
                embedding_function=get_embeddings()
            )
        except Exception:
            pass

question = st.text_input("Ask a question about your documents")

if st.button("Ask") and question.strip():
    store = st.session_state.vector_store

    if store is None:
        st.warning("Upload and index documents first.")
    else:
        with st.spinner("Searching documents and generating an answer..."):
            try:
                results = store.similarity_search_with_score(
                    question,
                    k=4
                )

                if not results:
                    st.warning("No relevant passages found.")
                else:
                    passages = [
                        doc for doc, score in results
                        if score < 1.2
                    ]

                    if not passages:
                        st.warning(
                            "No sufficiently relevant passages found. "
                            "Try rephrasing your question."
                        )
                    else:
                        context = "\n\n".join(
                            f"Source: {doc.metadata.get('source', 'Unknown')}, "
                            f"Page: {doc.metadata.get('page', 'N/A')}\n"
                            f"{doc.page_content}"
                            for doc in passages
                        )

                        prompt = ChatPromptTemplate.from_messages([
                            (
                                "system",
                                "Answer only using the provided context. "
                                "If the context does not contain the answer, "
                                "say you do not know based on these documents. "
                                "Do not invent facts."
                            ),
                            (
                                "human",
                                "Context:\n{context}\n\n"
                                "Question: {question}"
                            )
                        ])

                        model = ChatOllama(
                            model="qwen2.5:3b",
                            temperature=0
                        )

                        chain = prompt | model
                        response = chain.invoke({
                            "context": context,
                            "question": question
                        })

                        st.subheader("Answer")
                        st.write(response.content)

                        st.subheader("Retrieved sources")

                        for doc in passages:
                            source = doc.metadata.get("source", "Unknown")
                            page = doc.metadata.get("page", None)

                            if page is not None:
                                st.markdown(
                                    f"- **{source}**, page {page + 1}"
                                )
                            else:
                                st.markdown(f"- **{source}**")

                            st.caption(doc.page_content)

            except Exception as error:
                st.error(f"Question answering failed: {error}")
