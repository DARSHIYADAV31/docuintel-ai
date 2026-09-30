from dataclasses import dataclass


@dataclass
class Chunk:
    index: int
    text: str


@dataclass
class Hit:
    chunk_index: int
    text: str
    score: float
