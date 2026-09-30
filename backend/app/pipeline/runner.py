from app.llm.router import LLMRouter
from app.logging_setup import get_logger
from app.pipeline.orchestrator import process_document
from app.vectorstore.factory import get_store

log = get_logger(__name__)


def run_pipeline_task(session_factory, document_id: int) -> None:
    """Background entry point: own DB session, never lets an exception escape."""
    db = session_factory()
    try:
        process_document(db, document_id, LLMRouter(), get_store())
    except Exception as exc:
        log.error("pipeline task crashed document_id=%d error=%s",
                  document_id, type(exc).__name__)
    finally:
        db.close()
