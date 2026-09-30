import io

from pypdf import PdfReader
from PIL import Image

from app.errors import FileValidationError


def check_pdf(data: bytes) -> None:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise FileValidationError("Encrypted PDFs are not supported")
        if len(reader.pages) == 0:
            raise FileValidationError("PDF has no pages")
    except FileValidationError:
        raise
    except Exception as exc:
        raise FileValidationError("PDF is corrupted or unreadable") from exc


def check_image(data: bytes) -> None:
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as exc:
        raise FileValidationError("Image is corrupted or unreadable") from exc
