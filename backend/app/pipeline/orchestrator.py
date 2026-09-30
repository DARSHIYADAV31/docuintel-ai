from app.classification.classifier import classify_document
from app.db.repositories import document_repo
from app.extraction.key_values import extract_document
from app.logging_setup import get_logger
from app.pipeline import persistence
from app.pipeline.indexing import try_index
from app.pipeline.reading import read_document
from app.pipeline.stages import StageRunner
from app.pipeline.summary import build_summary
from app.validation.agent import validate_extraction
from app.validation.scoring import overall_confidence

log = get_logger(__name__)


class Pipeline:
    def __init__(self, db, doc, router, store):
        self.db, self.doc, self.router, self.store = db, doc, router, store
        self.stages, self.layout, self.ocr_engine = StageRunner(), None, None

    def _summary(self) -> dict:
        return build_summary(self.router.tracker, self.stages.durations,
                             self.layout, self.ocr_engine)

    def _read(self) -> str:
        result = read_document(self.db, self.doc, self.stages)
        self.layout, self.ocr_engine = result.layout, result.engine
        return result.text

    def _analyze(self, text: str) -> None:
        run = self.stages.run
        cls = run("classify", classify_document, self.router, text)
        index_issues = try_index(self.stages, self.store, self.doc.id, text)
        if cls.doc_type == "unknown":
            persistence.save_unknown_type(self.db, self.doc, cls, index_issues, self._summary())
            return
        extraction = run("extract", extract_document, self.router, text, cls.doc_type)
        issues = run("validate", validate_extraction, cls.doc_type, extraction) + index_issues
        confidence = overall_confidence(extraction, issues)
        persistence.save_results(self.db, self.doc, cls, extraction, issues,
                                 confidence, self._summary())

    def run(self) -> None:
        try:
            self._analyze(self._read())
        except Exception as exc:
            log.error("document_id=%d failed", self.doc.id)
            persistence.save_failure(self.db, self.doc, str(exc), self._summary())


def process_document(db, document_id: int, router, store) -> None:
    doc = document_repo.get(db, document_id)
    if doc is None:
        log.error("document_id=%d not found", document_id)
        return
    Pipeline(db, doc, router, store).run()
    log.info("document_id=%d status=%s cost=%s", document_id, doc.status,
             router.tracker.summary())
