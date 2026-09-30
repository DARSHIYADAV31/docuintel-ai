from functools import lru_cache

from app.config import get_settings


@lru_cache
def _model():
    from sentence_transformers import SentenceTransformer

    # never download while serving a request: a blocked network would hang the upload.
    # Run `python download_models.py` once to fetch the model instead.
    return SentenceTransformer(get_settings().embedding_model, local_files_only=True)


def encode(texts: list[str]):
    return _model().encode(texts, normalize_embeddings=True)


def is_loaded() -> bool:
    return _model.cache_info().currsize > 0
