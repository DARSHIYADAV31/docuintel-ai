from pathlib import Path

from pypdf import PdfReader

from app.ocr.types import LayoutInfo

MIN_TEXT_CHARS = 20


def analyze_layout(path: Path, kind: str) -> LayoutInfo:
    """Cheap pre-check that tells us whether OCR is really needed."""
    if kind != "pdf":
        return LayoutInfo(page_count=1, has_text_layer=False, is_scanned=True)
    pages = PdfReader(str(path)).pages
    text_chars = sum(len(page.extract_text() or "") for page in pages)
    has_text = text_chars >= MIN_TEXT_CHARS
    return LayoutInfo(len(pages), has_text, is_scanned=not has_text)
