from functools import lru_cache
from pathlib import Path

from app.ocr.types import OCRResult


@lru_cache
def _converter():
    # building it loads the layout/OCR models, so do it once and reuse it
    from docling.document_converter import DocumentConverter

    return DocumentConverter()


def run_docling(path: Path) -> OCRResult:
    result = _converter().convert(str(path))
    # markdown keeps tables as pipe tables, which the extractor can read
    text = result.document.export_to_markdown()
    return OCRResult(text=text, engine="docling")
