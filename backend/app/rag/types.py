from dataclasses import dataclass, field


@dataclass
class Citation:
    chunk_index: int
    snippet: str
    score: float


@dataclass
class Answer:
    text: str
    citations: list[Citation] = field(default_factory=list)
    grounded: bool = False
