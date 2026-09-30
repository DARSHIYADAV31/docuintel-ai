from app.errors import VectorStoreError
from app.logging_setup import get_logger
from app.vectorstore import embedder
from app.vectorstore.base import VectorStore
from app.vectorstore.chunker import chunk_text

log = get_logger(__name__)


def index_document(store: VectorStore, document_id: int, text: str) -> int:
    """Chunk, embed and store a document; returns the chunk count."""
    chunks = chunk_text(text)
    if not chunks:
        raise VectorStoreError("Document has no text to index")
    try:
        vectors = embedder.embed_texts([c.text for c in chunks])
        store.delete(document_id)  # re-indexing must not leave stale chunks
        store.add(document_id, chunks, vectors)
    except VectorStoreError:
        raise
    except Exception as exc:
        raise VectorStoreError("Indexing failed") from exc
    log.info("indexed document_id=%d chunks=%d", document_id, len(chunks))
    return len(chunks)
