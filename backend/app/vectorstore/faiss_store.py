import json
from pathlib import Path

import faiss
import numpy as np

from app.vectorstore.base import VectorStore
from app.vectorstore.types import Chunk, Hit


class FaissStore(VectorStore):
    """One flat index per document, saved as <id>.index plus <id>.json (chunk texts)."""

    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def _paths(self, document_id: int) -> tuple[Path, Path]:
        return self.root / f"{document_id}.index", self.root / f"{document_id}.json"

    def add(self, document_id: int, chunks: list[Chunk], vectors: np.ndarray) -> None:
        index_path, texts_path = self._paths(document_id)
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, str(index_path))
        texts_path.write_text(json.dumps([c.text for c in chunks]), encoding="utf-8")

    def search(self, document_id: int, query: np.ndarray, k: int) -> list[Hit]:
        index_path, texts_path = self._paths(document_id)
        if not index_path.exists():
            return []
        texts = json.loads(texts_path.read_text(encoding="utf-8"))
        index = faiss.read_index(str(index_path))
        scores, ids = index.search(query.reshape(1, -1), min(k, len(texts)))
        return [Hit(int(i), texts[i], float(s)) for i, s in zip(ids[0], scores[0]) if i >= 0]

    def delete(self, document_id: int) -> None:
        for path in self._paths(document_id):
            path.unlink(missing_ok=True)
