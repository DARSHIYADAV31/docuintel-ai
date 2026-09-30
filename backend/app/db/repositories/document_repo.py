from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document


def create(db: Session, owner_id: int, filename: str, stored_path: str,
           handwritten: bool) -> Document:
    doc = Document(owner_id=owner_id, filename=filename, stored_path=stored_path,
                   handwritten=handwritten, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get(db: Session, document_id: int) -> Document | None:
    return db.get(Document, document_id)


def get_owned(db: Session, document_id: int, owner_id: int) -> Document | None:
    doc = db.get(Document, document_id)
    return doc if doc and doc.owner_id == owner_id else None


def list_owned(db: Session, owner_id: int) -> list[Document]:
    query = select(Document).where(Document.owner_id == owner_id)
    return list(db.scalars(query.order_by(Document.id.desc())))


def update(db: Session, doc: Document, **values) -> Document:
    for name, value in values.items():
        setattr(doc, name, value)
    db.commit()
    return doc


def fail_interrupted(db: Session) -> int:
    """After a restart no job is running, so anything still 'processing' is dead."""
    stuck = list(db.scalars(select(Document).where(Document.status == "processing")))
    for doc in stuck:
        doc.status = "failed"
        doc.error_message = "Processing was interrupted by a server restart; please upload again"
    db.commit()
    return len(stuck)
