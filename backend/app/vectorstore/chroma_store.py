from pathlib import Path

import chromadb
import numpy as np

from app.vectorstore.base import VectorStore
from app.vectorstore.types import Chunk, Hit


class ChromaStore(VectorStore):
    def __init__(self, root: Path):
        client = chromadb.PersistentClient(path=str(root))
        self.collection = client.get_or_create_collection(
            "chunks", metadata={"hnsw:space": "cosine"})

    def add(self, document_id: int, chunks: list[Chunk], vectors: np.ndarray) -> None:
        self.collection.add(
            ids=[f"{document_id}:{c.index}" for c in chunks],
            embeddings=vectors.tolist(),
            documents=[c.text for c in chunks],
            metadatas=[{"document_id": document_id, "chunk_index": c.index} for c in chunks],
        )

    def search(self, document_id: int, query: np.ndarray, k: int) -> list[Hit]:
        found = self.collection.query(
            query_embeddings=[query.tolist()], n_results=k,
            where={"document_id": document_id})
        rows = zip(found["metadatas"][0], found["documents"][0], found["distances"][0])
        # cosine distance -> similarity, to match the FAISS scores
        return [Hit(int(m["chunk_index"]), text, 1.0 - dist) for m, text, dist in rows]

    def delete(self, document_id: int) -> None:
        self.collection.delete(where={"document_id": document_id})
