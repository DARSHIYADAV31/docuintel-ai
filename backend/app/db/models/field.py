from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExtractedField(Base):
    """Sensitive values live here only; never write them to logs."""

    __tablename__ = "extracted_fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)
    name: Mapped[str]
    value: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(default=0.0)
    flagged: Mapped[bool] = mapped_column(default=False)
