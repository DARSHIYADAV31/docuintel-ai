from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas import AskRequest, AskResponse, CitationOut
from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.repositories import document_repo, results_repo
from app.db.session import get_db
from app.llm.router import LLMRouter
from app.logging_setup import get_logger
from app.rag.answerer import answer_question
from app.vectorstore.factory import get_store

router = APIRouter(prefix="/documents", tags=["qa"])
log = get_logger(__name__)
READY = {"completed", "needs_review"}


@router.post("/{document_id}/ask")
def ask(document_id: int, body: AskRequest, user: User = Depends(get_current_user),
        db: Session = Depends(get_db)) -> AskResponse:
    doc = document_repo.get_owned(db, document_id, user.id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    if doc.status not in READY:
        raise HTTPException(status.HTTP_409_CONFLICT, "Document is not ready for questions")
    if any(i.rule == "indexing" for i in results_repo.get_issues(db, doc.id)):
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "This document was not indexed for questions. Please upload it again.")
    llm = LLMRouter()
    answer = answer_question(llm, get_store(), doc.id, body.question)
    log.info("qa document_id=%d cost=%s", doc.id, llm.tracker.summary())
    return AskResponse(answer=answer.text, grounded=answer.grounded,
                       citations=[CitationOut(**vars(c)) for c in answer.citations])
