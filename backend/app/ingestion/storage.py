import uuid
from pathlib import Path

UPLOAD_DIR = Path("uploads")


def save_upload(data: bytes, kind: str) -> Path:
    """Store under a random name so user-supplied filenames never touch the disk."""
    UPLOAD_DIR.mkdir(exist_ok=True)
    ext = "jpg" if kind == "jpeg" else kind
    path = UPLOAD_DIR / f"{uuid.uuid4().hex}.{ext}"
    path.write_bytes(data)
    return path
