from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.presenter import build_detail
from app.api.schemas import DocumentDetail, DocumentSummary
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.repositories import document_repo
from app.db.session import get_db

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)) -> list[DocumentSummary]:
    return [DocumentSummary.model_validate(d) for d in document_repo.list_owned(db, user.id)]


@router.get("/{document_id}")
def get_document(document_id: int, reveal_sensitive: bool = False,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)) -> DocumentDetail:
    doc = document_repo.get_owned(db, document_id, user.id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return build_detail(db, doc, reveal_sensitive, user.id)
