from pathlib import Path

import numpy as np
from PIL import Image


def load_page_images(path: Path) -> list[np.ndarray]:
    """Return each page as an RGB array; PDFs are rendered at 200 DPI."""
    if path.suffix.lower() != ".pdf":
        return [np.array(Image.open(path).convert("RGB"))]
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(path))
    pages = [pdf[i].render(scale=200 / 72).to_pil() for i in range(len(pdf))]
    return [np.array(page.convert("RGB")) for page in pages]
