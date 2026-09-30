import time
from datetime import datetime, timezone

from app.db.repositories import document_repo, results_repo
from app.evaluation.comparer import compare_fields, describe_mismatches
from app.evaluation.metrics import aggregate
from app.evaluation.sandbox import eval_sandbox
from app.evaluation.types import Case, CaseResult
from app.logging_setup import get_logger
from app.pipeline.orchestrator import process_document

log = get_logger(__name__)


def run_case(case: Case, db, owner_id: int, router, store) -> CaseResult:
    started = time.perf_counter()
    doc = document_repo.create(db, owner_id, case.path.name, str(case.path), case.handwritten)
    process_document(db, doc.id, router, store)
    db.refresh(doc)
    actual = {f.name: f.value for f in results_repo.get_fields(db, doc.id)}
    field_ok = compare_fields(case.fields, actual)
    items_ok = None
    if case.line_item_count is not None:
        items_ok = len(doc.line_items or []) == case.line_item_count
    return CaseResult(
        file=case.path.name, status=doc.status, doc_type_ok=doc.doc_type == case.doc_type,
        field_ok=field_ok, items_ok=items_ok, confidence=doc.confidence,
        cost_usd=router.tracker.summary()["estimated_usd"],
        seconds=round(time.perf_counter() - started, 1),
        mismatches=describe_mismatches(case.fields, actual, field_ok))


def evaluate(cases: list[Case], router_factory) -> dict:
    """Runs every case through the real pipeline and returns the full report."""
    results = []
    with eval_sandbox() as (session_factory, store, owner_id):
        for case in cases:
            db = session_factory()
            try:
                results.append(run_case(case, db, owner_id, router_factory(), store))
            finally:
                db.close()
            log.info("evaluated %s status=%s", case.path.name, results[-1].status)
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "summary": aggregate(results),
        "cases": [vars(r) for r in results],
    }
