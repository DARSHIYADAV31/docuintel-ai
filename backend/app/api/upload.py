import os

from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form, HTTPException,
                     UploadFile, status)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import get_settings
from app.db.models import User
from app.db.repositories import document_repo
from app.db.session import get_db, get_session_factory
from app.errors import FileValidationError
from app.ingestion.file_validator import validate_upload
from app.ingestion.storage import save_upload
from app.logging_setup import get_logger
from app.pipeline.runner import run_pipeline_task

router = APIRouter(prefix="/documents", tags=["documents"])
log = get_logger(__name__)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    handwritten: bool = Form(False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
) -> dict:
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(max_bytes + 1)  # +1 so oversize files are detected, not truncated
    try:
        validated = validate_upload(data)
    except FileValidationError as exc:
        log.warning("upload rejected user_id=%d reason=%s", user.id, exc)
        raise HTTPException(422, str(exc))
    stored = save_upload(data, validated.kind)
    name = os.path.basename(file.filename or "upload")[:255]
    doc = document_repo.create(db, user.id, name, str(stored), handwritten)
    background.add_task(run_pipeline_task, session_factory, doc.id)
    log.info("upload accepted document_id=%d kind=%s", doc.id, validated.kind)
    return {"id": doc.id, "status": doc.status}
