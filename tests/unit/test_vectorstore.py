import numpy as np
import pytest

from app.vectorstore.chroma_store import ChromaStore
from app.vectorstore.chunker import chunk_text
from app.vectorstore.faiss_store import FaissStore
from app.vectorstore.types import Chunk


def _unit(*values) -> np.ndarray:
    vec = np.array(values, dtype="float32")
    return vec / np.linalg.norm(vec)


CHUNKS = [Chunk(0, "about payment"), Chunk(1, "about shipping")]
VECTORS = np.stack([_unit(1, 0, 0), _unit(0, 1, 0)])


@pytest.fixture(params=["faiss", "chroma"])
def store(request, tmp_path):
    return FaissStore(tmp_path) if request.param == "faiss" else ChromaStore(tmp_path)


def test_search_returns_closest_chunk_first(store):
    store.add(1, CHUNKS, VECTORS)
    hits = store.search(1, _unit(0.9, 0.1, 0), k=2)
    assert hits[0].text == "about payment"


def test_search_is_scoped_to_document(store):
    store.add(1, CHUNKS, VECTORS)
    assert store.search(2, _unit(1, 0, 0), k=2) == []


def test_delete_removes_document(store):
    store.add(1, CHUNKS, VECTORS)
    store.delete(1)
    assert store.search(1, _unit(1, 0, 0), k=2) == []


def test_chunker_respects_size_and_keeps_all_text():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, size=200, overlap=30)
    assert len(chunks) > 1 and all(len(c.text) <= 200 for c in chunks)
    assert "word0" in chunks[0].text and "word499" in chunks[-1].text


def test_chunker_handles_empty_and_short_text():
    assert chunk_text("   ") == []
    assert len(chunk_text("short invoice text")) == 1


def _use_local_backend(monkeypatch):
    from app.config import get_settings
    from app.vectorstore import embedder

    monkeypatch.setenv("EMBEDDING_BACKEND", "local")
    get_settings.cache_clear()
    monkeypatch.setitem(embedder._state, "failed_at", None)


def test_local_embedding_timeout_becomes_error_then_fails_fast(monkeypatch):
    import time

    from app.errors import VectorStoreError
    from app.vectorstore import embedder

    _use_local_backend(monkeypatch)
    monkeypatch.setenv("EMBEDDING_TIMEOUT_SECONDS", "1")
    from app.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setattr(embedder, "_encode", lambda texts: time.sleep(5))
    with pytest.raises(VectorStoreError):
        embedder.embed_texts(["hello"])
    started = time.monotonic()
    with pytest.raises(VectorStoreError):
        embedder.embed_texts(["hello"])
    assert time.monotonic() - started < 0.5  # second call is instant (cooldown)


def test_local_model_is_never_downloaded_while_serving(monkeypatch):
    import sentence_transformers

    from app.errors import VectorStoreError
    from app.vectorstore import embedder, local_embedder

    _use_local_backend(monkeypatch)
    seen = {}

    def fake_loader(name, **kwargs):
        seen.update(kwargs)
        raise OSError("model not on disk")

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", fake_loader)
    local_embedder._model.cache_clear()
    with pytest.raises(VectorStoreError, match="download_models"):
        embedder.embed_texts(["hello"])
    assert seen["local_files_only"] is True
    local_embedder._model.cache_clear()


def test_gemini_backend_is_default_and_retries_transient_errors(monkeypatch):
    from app.errors import TransientError
    from app.vectorstore import embedder, gemini_embedder

    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = []

    def flaky(texts):
        calls.append(1)
        if len(calls) < 3:
            raise TransientError("rate limited")
        return np.ones((len(texts), 4), dtype="float32")

    monkeypatch.setattr(gemini_embedder, "encode", flaky)
    assert embedder.embed_texts(["a", "b"]).shape == (2, 4)
    assert len(calls) == 3
