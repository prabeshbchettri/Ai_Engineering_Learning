# Read files and attach source metadata


from langchain_community.document_loaders import PyPDFLoader, TextLoader
from rag.config import DATA_DIR


def load_documents():
    documents = []

    for file_path in DATA_DIR.iterdir():
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix == ".txt":
            loader = TextLoader(
                str(file_path),
                encoding="utf-8"
            )
        else:
            continue

        pages = loader.load()

        for page in pages:
            page.metadata["source"] = file_path.name

        documents.extend(pages)

    return documents
