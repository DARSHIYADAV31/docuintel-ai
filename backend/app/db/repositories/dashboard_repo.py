from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Document, ValidationIssue


def status_counts(db: Session, owner_id: int) -> dict[str, int]:
    query = (select(Document.status, func.count())
             .where(Document.owner_id == owner_id).group_by(Document.status))
    return {status: count for status, count in db.execute(query)}


def average_confidence(db: Session, owner_id: int) -> float | None:
    query = select(func.avg(Document.confidence)).where(
        Document.owner_id == owner_id, Document.confidence.is_not(None))
    value = db.scalar(query)
    return round(value, 3) if value is not None else None


def issue_counts(db: Session, owner_id: int) -> dict[str, int]:
    query = (select(ValidationIssue.severity, func.count())
             .join(Document, Document.id == ValidationIssue.document_id)
             .where(Document.owner_id == owner_id).group_by(ValidationIssue.severity))
    return {severity: count for severity, count in db.execute(query)}


def flagged_documents(db: Session, owner_id: int, limit: int = 10) -> list[Document]:
    query = (select(Document)
             .where(Document.owner_id == owner_id,
                    Document.status.in_(["needs_review", "failed"]))
             .order_by(Document.id.desc()).limit(limit))
    return list(db.scalars(query))
