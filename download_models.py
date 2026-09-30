"""Only needed when EMBEDDING_BACKEND=local: downloads the Sentence Transformers model.

Run: python download_models.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.config import get_settings  # noqa: E402


def main() -> int:
    from sentence_transformers import SentenceTransformer

    name = get_settings().embedding_model
    print(f"Downloading {name} ... (about 90 MB)")
    SentenceTransformer(name)
    print("Done. Restart the backend to enable the Ask page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
