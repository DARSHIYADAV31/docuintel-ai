"""Renders eval/dataset/*.png and labels.json from samples.py.

Run: python eval/generate_samples.py
Synthetic and clean, so scores here are optimistic; add real documents to
eval/dataset/ (and their labels) to measure real-world accuracy.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from samples import SAMPLES

DATASET = Path(__file__).parent / "dataset"
FONT_SIZE, LINE_HEIGHT, MARGIN = 26, 42, 60


def render(lines: list[str], path: Path) -> None:
    height = MARGIN * 2 + LINE_HEIGHT * len(lines)
    image = Image.new("RGB", (1300, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=FONT_SIZE)
    for row, text in enumerate(lines):
        draw.text((MARGIN, MARGIN + row * LINE_HEIGHT), text, fill="black", font=font)
    image.save(path)


def main() -> None:
    DATASET.mkdir(exist_ok=True)
    cases = []
    for sample in SAMPLES:
        render(sample["lines"], DATASET / sample["file"])
        keys = ("file", "doc_type", "line_item_count", "fields")
        cases.append({**{k: sample[k] for k in keys}, "handwritten": False})
    (DATASET / "labels.json").write_text(json.dumps({"cases": cases}, indent=2))
    print(f"wrote {len(cases)} documents to {DATASET}")


if __name__ == "__main__":
    main()
