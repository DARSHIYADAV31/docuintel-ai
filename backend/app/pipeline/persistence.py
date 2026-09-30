from app.db.repositories import document_repo, results_repo


def _needs_review(issues) -> bool:
    return any(i.severity == "error" or i.rule == "model_disagreement" for i in issues)


def save_results(db, doc, classification, extraction, issues, confidence, summary):
    results_repo.replace_fields(db, doc.id, extraction.fields)
    results_repo.replace_issues(db, doc.id, issues)
    status = "needs_review" if _needs_review(issues) else "completed"
    document_repo.update(
        db, doc, status=status, doc_type=classification.doc_type,
        classification_confidence=classification.confidence, confidence=confidence,
        line_items=extraction.line_items, processing_summary=summary, error_message=None)


def save_unknown_type(db, doc, classification, issues, summary):
    results_repo.replace_issues(db, doc.id, issues)
    document_repo.update(
        db, doc, status="needs_review", doc_type="unknown",
        classification_confidence=classification.confidence,
        processing_summary=summary, error_message="Could not determine document type")


def save_failure(db, doc, message: str, summary: dict):
    document_repo.update(db, doc, status="failed", error_message=message,
                         processing_summary=summary)
