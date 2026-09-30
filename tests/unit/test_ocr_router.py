from pathlib import Path

import pytest

from app.errors import OCRError
from app.ocr import docling_engine, paddle_engine
from app.ocr.router import extract_text
from app.ocr.types import OCRResult

LONG_TEXT = "Invoice number 1234 total 500.00 USD"


def _docling_ok(path):
    return OCRResult(LONG_TEXT, "docling")


def _boom(path):
    raise RuntimeError("engine crashed")


def _paddle_ok(path):
    return OCRResult(LONG_TEXT, "paddleocr", 0.9)


def test_docling_used_for_normal_documents(monkeypatch):
    monkeypatch.setattr(docling_engine, "run_docling", _docling_ok)
    monkeypatch.setattr(paddle_engine, "run_paddle", lambda p: pytest.fail("called"))
    assert extract_text(Path("x.pdf")).engine == "docling"


def test_handwritten_goes_straight_to_paddle(monkeypatch):
    monkeypatch.setattr(docling_engine, "run_docling", lambda p: pytest.fail("called"))
    monkeypatch.setattr(paddle_engine, "run_paddle", _paddle_ok)
    assert extract_text(Path("x.png"), handwritten=True).engine == "paddleocr"


def test_docling_failure_falls_back_to_paddle(monkeypatch):
    monkeypatch.setattr(docling_engine, "run_docling", _boom)
    monkeypatch.setattr(paddle_engine, "run_paddle", _paddle_ok)
    assert extract_text(Path("x.pdf")).engine == "paddleocr"


def test_docling_empty_output_falls_back_to_paddle(monkeypatch):
    monkeypatch.setattr(docling_engine, "run_docling",
                        lambda p: OCRResult("  ", "docling"))
    monkeypatch.setattr(paddle_engine, "run_paddle", _paddle_ok)
    assert extract_text(Path("x.pdf")).engine == "paddleocr"


def test_all_engines_failing_raises_ocr_error(monkeypatch):
    monkeypatch.setattr(docling_engine, "run_docling", _boom)
    monkeypatch.setattr(paddle_engine, "run_paddle", _boom)
    with pytest.raises(OCRError):
        extract_text(Path("x.pdf"))
