from app.vectorstore.types import Chunk

CHUNK_SIZE = 800
OVERLAP = 100


def _break_point(text: str, start: int, end: int) -> int:
    """Prefer cutting at a line break, then a space, in the second half of the window."""
    midpoint = (start + end) // 2
    for separator in ("\n", " "):
        cut = text.rfind(separator, midpoint, end)
        if cut != -1:
            return cut
    return end


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[Chunk]:
    text = text.strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            end = _break_point(text, start, end)
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(len(chunks), piece))
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks
