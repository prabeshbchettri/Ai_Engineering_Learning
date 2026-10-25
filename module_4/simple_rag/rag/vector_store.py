# Create embeddings, index documents and retrieve passages


from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from rag.config import (
    DB_DIR,
    EMBEDDING_MODEL,
    COLLECTION_NAME
)


@lru_cache(maxsize=1) # Initialize the embedding model
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def get_vector_store(): # Connect to ChromaDB
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=get_embeddings()
    )


def build_vector_store(chunks):# Build the vector store
    if not chunks:
        return None

    store = get_vector_store()
    existing_ids = store.get()["ids"]

    if existing_ids:
        store.delete(ids=existing_ids)

    store.add_documents(chunks)

    return store


def load_vector_store():# Load an existing vector store
    store = get_vector_store()

    if not store.get()["ids"]:
        return None

    return store
