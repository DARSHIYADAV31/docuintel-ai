from dataclasses import dataclass


@dataclass
class OCRResult:
    text: str
    engine: str
    confidence: float | None = None


@dataclass
class LayoutInfo:
    page_count: int
    has_text_layer: bool
    is_scanned: bool
