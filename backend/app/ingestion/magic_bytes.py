SIGNATURES = {
    b"%PDF-": "pdf",
    b"\x89PNG\r\n\x1a\n": "png",
    b"\xff\xd8\xff": "jpeg",
    b"II*\x00": "tiff",
    b"MM\x00*": "tiff",
}


def detect_kind(data: bytes) -> str | None:
    """Identify type from file content, ignoring extension and client MIME."""
    for signature, kind in SIGNATURES.items():
        if data.startswith(signature):
            return kind
    return None
