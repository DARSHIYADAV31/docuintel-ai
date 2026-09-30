from functools import lru_cache
from pathlib import Path

from app.ocr.page_images import load_page_images
from app.ocr.types import OCRResult


@lru_cache
def _get_engine():
    from paddleocr import PaddleOCR

    # oneDNN is disabled: it crashes on Paddle 3.x with Windows CPU
    return PaddleOCR(lang="en", use_doc_orientation_classify=False,
                     use_doc_unwarping=False, enable_mkldnn=False)


def _page_lines(engine, image) -> tuple[list[str], list[float]]:
    lines, scores = [], []
    for res in engine.predict(image):
        lines += res["rec_texts"]
        scores += [float(s) for s in res["rec_scores"]]
    return lines, scores


def run_paddle(path: Path) -> OCRResult:
    engine = _get_engine()
    all_lines, all_scores = [], []
    for image in load_page_images(path):
        lines, scores = _page_lines(engine, image)
        all_lines += lines
        all_scores += scores
    confidence = sum(all_scores) / len(all_scores) if all_scores else 0.0
    return OCRResult("\n".join(all_lines), "paddleocr", round(confidence, 3))
