import io

import pytest
from PIL import Image
from pypdf import PdfWriter

from app.errors import FileValidationError
from app.ingestion.file_validator import validate_upload


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buf, format="PNG")
    return buf.getvalue()


def _pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_valid_pdf_and_png_accepted():
    assert validate_upload(_pdf()).kind == "pdf"
    assert validate_upload(_png()).kind == "png"


def test_empty_file_rejected():
    with pytest.raises(FileValidationError):
        validate_upload(b"")


def test_fake_pdf_rejected():
    with pytest.raises(FileValidationError):
        validate_upload(b"%PDF-1.4 this is not really a pdf")


def test_non_document_rejected():
    with pytest.raises(FileValidationError):
        validate_upload(b"MZ\x90\x00 executable renamed to invoice.pdf")


def test_truncated_image_rejected():
    with pytest.raises(FileValidationError):
        validate_upload(_png()[:30])


def test_oversized_file_rejected(monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_MB", "0")
    with pytest.raises(FileValidationError):
        validate_upload(_pdf())
