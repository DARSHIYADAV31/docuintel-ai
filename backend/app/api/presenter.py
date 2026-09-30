from sqlalchemy.orm import Session

from app.api.schemas import DocumentDetail, FieldOut, IssueOut
from app.db.models import Document
from app.db.repositories import results_repo
from app.extraction.schemas import SENSITIVE_FIELDS
from app.logging_setup import get_logger

log = get_logger(__name__)
VISIBLE_DIGITS = 4


def mask_value(name: str, value: str | None) -> str | None:
    if name not in SENSITIVE_FIELDS or not value:
        return value
    return "*" * max(len(value) - VISIBLE_DIGITS, 0) + value[-VISIBLE_DIGITS:]


def build_detail(db: Session, doc: Document, reveal: bool, user_id: int) -> DocumentDetail:
    if reveal:  # audit trail: who saw sensitive data, never the data itself
        log.info("sensitive fields revealed document_id=%d user_id=%d", doc.id, user_id)
    fields = [FieldOut(name=f.name, value=f.value if reveal else mask_value(f.name, f.value),
                       confidence=f.confidence, flagged=f.flagged)
              for f in results_repo.get_fields(db, doc.id)]
    issues = [IssueOut.model_validate(i) for i in results_repo.get_issues(db, doc.id)]
    base = {c: getattr(doc, c) for c in ("id", "filename", "status", "doc_type", "confidence",
            "created_at", "error_message", "ocr_engine", "handwritten", "processing_summary")}
    return DocumentDetail(**base, line_items=doc.line_items or [], fields=fields, issues=issues)
