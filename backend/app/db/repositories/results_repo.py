from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ExtractedField, ValidationIssue
from app.extraction.schemas import FieldValue
from app.validation.issue import Issue


def replace_fields(db: Session, document_id: int, fields: dict[str, FieldValue]) -> None:
    db.execute(delete(ExtractedField).where(ExtractedField.document_id == document_id))
    db.add_all([ExtractedField(document_id=document_id, name=name, value=f.value,
                               confidence=f.confidence, flagged=f.flagged)
                for name, f in fields.items()])
    db.commit()


def replace_issues(db: Session, document_id: int, issues: list[Issue]) -> None:
    db.execute(delete(ValidationIssue).where(ValidationIssue.document_id == document_id))
    db.add_all([ValidationIssue(document_id=document_id, field_name=i.field, rule=i.rule,
                                severity=i.severity, message=i.message) for i in issues])
    db.commit()


def get_fields(db: Session, document_id: int) -> list[ExtractedField]:
    query = select(ExtractedField).where(ExtractedField.document_id == document_id)
    return list(db.scalars(query.order_by(ExtractedField.id)))


def get_issues(db: Session, document_id: int) -> list[ValidationIssue]:
    query = select(ValidationIssue).where(ValidationIssue.document_id == document_id)
    return list(db.scalars(query.order_by(ValidationIssue.id)))
