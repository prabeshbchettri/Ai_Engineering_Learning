# Store configuration in one place

from pathlib import Path # for working with file and folder


BASE_DIR = Path(__file__).resolve().parent.parent # for finding the project root directory

DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "qwen2.5:3b"

COLLECTION_NAME = "simple_rag"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
TOP_K = 4

DATA_DIR.mkdir(parents=True, exist_ok=True)
