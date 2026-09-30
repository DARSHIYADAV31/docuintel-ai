from dataclasses import dataclass

from app.config import get_settings
from app.errors import FileValidationError
from app.ingestion.integrity import check_image, check_pdf
from app.ingestion.magic_bytes import detect_kind


@dataclass
class ValidatedFile:
    kind: str
    size_bytes: int


def validate_upload(data: bytes) -> ValidatedFile:
    if not data:
        raise FileValidationError("File is empty")
    max_bytes = get_settings().max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise FileValidationError("File exceeds the maximum allowed size")
    kind = detect_kind(data)
    if kind is None:
        raise FileValidationError("Only PDF, PNG, JPEG and TIFF files are accepted")
    check_pdf(data) if kind == "pdf" else check_image(data)
    return ValidatedFile(kind=kind, size_bytes=len(data))
