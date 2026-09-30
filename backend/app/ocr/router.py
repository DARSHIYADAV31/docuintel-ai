from pathlib import Path

from app.config import get_settings
from app.errors import OCRError
from app.logging_setup import get_logger
from app.ocr import docling_engine, paddle_engine
from app.ocr.types import OCRResult
from app.retry import call_with_retry

log = get_logger(__name__)
MIN_USABLE_CHARS = 20


def _run(name: str, engine_fn, path: Path) -> OCRResult:
    timeout = get_settings().ocr_timeout_seconds
    result = call_with_retry(lambda: engine_fn(path), name=name, timeout=timeout)
    log.info("%s finished chars=%d", name, len(result.text))
    return result


def _usable(result: OCRResult) -> bool:
    return len(result.text.strip()) >= MIN_USABLE_CHARS


def _paddle_or_raise(path: Path) -> OCRResult:
    try:
        return _run("paddleocr", paddle_engine.run_paddle, path)
    except Exception as exc:
        raise OCRError("All OCR engines failed") from exc


def extract_text(path: Path, handwritten: bool = False) -> OCRResult:
    if handwritten:
        log.info("handwritten document, routing to paddleocr")
        return _paddle_or_raise(path)
    try:
        result = _run("docling", docling_engine.run_docling, path)
        if _usable(result):
            return result
        log.warning("docling returned too little text, falling back")
    except Exception:
        log.warning("docling failed, falling back to paddleocr")
    return _paddle_or_raise(path)
