class DocuIntelError(Exception):
    """Base class for all expected application errors."""


class TransientError(DocuIntelError):
    """Temporary failure (timeout, rate limit, 5xx) that is safe to retry."""


class ModelUnavailableError(DocuIntelError):
    """Every configured model failed after retries."""


class OCRError(DocuIntelError):
    """Text extraction failed."""


class InvalidTokenError(DocuIntelError):
    """JWT is missing, malformed, expired, or of the wrong type."""


class FileValidationError(DocuIntelError):
    """Uploaded file is not an accepted type or size."""


class LLMOutputError(DocuIntelError):
    """Model reply was not the JSON we asked for."""


class VectorStoreError(DocuIntelError):
    """Embedding, indexing, or retrieval failed."""
