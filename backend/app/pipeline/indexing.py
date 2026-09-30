from app.validation.issue import Issue
from app.vectorstore.indexer import index_document

NO_QA = Issue("document", "indexing", "warning", "Q&A is unavailable for this document")


def try_index(stages, store, document_id: int, text: str) -> list[Issue]:
    """Indexing failure must not lose the extraction, so it becomes a warning."""
    try:
        stages.run("index", index_document, store, document_id, text)
        return []
    except Exception:
        return [NO_QA]
