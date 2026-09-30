from pathlib import Path

from app.config import get_settings
from app.vectorstore.base import VectorStore

DATA_DIR = Path("vector_data")


def get_store() -> VectorStore:
    """FAISS by default; set VECTOR_STORE=chroma to use Chroma instead."""
    if get_settings().vector_store.lower() == "chroma":
        from app.vectorstore.chroma_store import ChromaStore

        return ChromaStore(DATA_DIR / "chroma")
    from app.vectorstore.faiss_store import FaissStore

    return FaissStore(DATA_DIR / "faiss")
