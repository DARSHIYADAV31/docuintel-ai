from abc import ABC, abstractmethod

import numpy as np

from app.vectorstore.types import Chunk, Hit


class VectorStore(ABC):
    """Every operation is scoped to one document so answers never mix documents."""

    @abstractmethod
    def add(self, document_id: int, chunks: list[Chunk], vectors: np.ndarray) -> None: ...

    @abstractmethod
    def search(self, document_id: int, query: np.ndarray, k: int) -> list[Hit]: ...

    @abstractmethod
    def delete(self, document_id: int) -> None: ...
