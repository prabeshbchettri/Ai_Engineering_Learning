
from app.config import (
    PROJECT_ROOT,
    DOCUMENTS_DIR,
    PROCESSED_DIR,
    VECTOR_STORE_DIR,
)


def test_project_paths():
    assert PROJECT_ROOT.name == "advanced-rag"
    assert DOCUMENTS_DIR == PROJECT_ROOT / "data" / "documents"
    assert PROCESSED_DIR == PROJECT_ROOT / "data" / "processed"
    assert VECTOR_STORE_DIR == PROJECT_ROOT / "data" / "vector_store"
