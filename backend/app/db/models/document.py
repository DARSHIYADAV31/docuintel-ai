from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    """status: uploaded | processing | completed | needs_review | failed"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str]
    stored_path: Mapped[str | None]
    handwritten: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(default="uploaded")
    doc_type: Mapped[str | None]
    classification_confidence: Mapped[float | None]
    confidence: Mapped[float | None]
    ocr_engine: Mapped[str | None]
    error_message: Mapped[str | None]
    line_items: Mapped[list | None] = mapped_column(JSON)
    processing_summary: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
