import time

import numpy as np

from app.config import get_settings
from app.errors import VectorStoreError
from app.retry import call_with_retry
from app.vectorstore import gemini_embedder, local_embedder

COOLDOWN_SECONDS = 300
NOT_INSTALLED = ("The embedding model is not installed on the server. "
                 "An administrator must run: python download_models.py")
_state = {"failed_at": None}


def _is_local() -> bool:
    return get_settings().embedding_backend.lower() == "local"


def _encode(texts: list[str]):
    return (local_embedder if _is_local() else gemini_embedder).encode(texts)


def _cooling_down() -> bool:
    failed_at = _state["failed_at"]
    return failed_at is not None and time.monotonic() - failed_at < COOLDOWN_SECONDS


def _failure_message(exc: Exception) -> str:
    if _is_local():
        return NOT_INSTALLED if isinstance(exc, OSError) else "Embedding failed"
    return "The embedding service failed; please try again"


def embed_texts(texts: list[str]) -> np.ndarray:
    """Unit-length float32 vectors, so inner product equals cosine similarity."""
    local, settings = _is_local(), get_settings()
    if local and _cooling_down():  # model recently missing: fail fast, not after a long wait
        raise VectorStoreError(NOT_INSTALLED)
    timeout = settings.embedding_timeout_seconds if local else settings.llm_timeout_seconds
    try:
        vectors = call_with_retry(lambda: _encode(texts), name="embedding", timeout=timeout,
                                  attempts=1 if local else 3)
    except Exception as exc:
        if local and not local_embedder.is_loaded():
            _state["failed_at"] = time.monotonic()
        raise VectorStoreError(_failure_message(exc)) from exc
    _state["failed_at"] = None
    return np.asarray(vectors, dtype="float32")
