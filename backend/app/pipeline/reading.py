from dataclasses import dataclass
from pathlib import Path

from app.db.repositories import document_repo
from app.ocr.layout import analyze_layout
from app.ocr.router import extract_text
from app.ocr.types import LayoutInfo


@dataclass
class ReadResult:
    text: str
    layout: LayoutInfo
    engine: str


def read_document(db, doc, stages) -> ReadResult:
    """Layout analysis first, then OCR routed by the handwritten flag."""
    path = Path(doc.stored_path)
    kind = "pdf" if path.suffix == ".pdf" else "image"
    layout = stages.run("layout", analyze_layout, path, kind)
    ocr = stages.run("ocr", extract_text, path, doc.handwritten)
    document_repo.update(db, doc, ocr_engine=ocr.engine)
    return ReadResult(ocr.text, layout, ocr.engine)
