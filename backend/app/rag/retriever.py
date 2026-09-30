from app.errors import VectorStoreError
from app.vectorstore import embedder
from app.vectorstore.base import VectorStore
from app.vectorstore.types import Hit

TOP_K = 4


def retrieve(store: VectorStore, document_id: int, question: str, k: int = TOP_K) -> list[Hit]:
    try:
        query = embedder.embed_texts([question])[0]
        return store.search(document_id, query, k)
    except VectorStoreError:
        raise
    except Exception as exc:
        raise VectorStoreError("Retrieval failed") from exc
