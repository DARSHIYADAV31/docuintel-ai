import re

from app.rag.types import Citation
from app.vectorstore.types import Hit

MARKER = re.compile(r"\[(\d+)\]")
SNIPPET_CHARS = 200


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _snippet(chunk_text: str, quote: str) -> str:
    """The model's quote if it really appears in the chunk, else the chunk's start."""
    if quote.strip() and _normalize(quote) in _normalize(chunk_text):
        return quote.strip()
    return chunk_text[:SNIPPET_CHARS]


def build_citations(numbers: list[int], quote: str, hits: list[Hit]) -> list[Citation]:
    """Valid source numbers only, in order, no repeats."""
    seen: list[int] = []
    for number in numbers:
        if 1 <= number <= len(hits) and number not in seen:
            seen.append(number)
    return [Citation(hits[n - 1].chunk_index, _snippet(hits[n - 1].text, quote),
                     hits[n - 1].score) for n in seen]


def extract_citations(answer: str, hits: list[Hit]) -> list[Citation]:
    """Fallback for plain-text replies: map [n] markers back to the chunks."""
    return build_citations([int(n) for n in MARKER.findall(answer)], "", hits)
