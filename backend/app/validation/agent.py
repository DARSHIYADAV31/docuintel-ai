from app.extraction.schemas import ExtractionResult
from app.logging_setup import get_logger
from app.validation.issue import Issue
from app.validation.rules.amount_math import check_items_sum, check_total
from app.validation.rules.dates import check_date_order
from app.validation.rules.formats import check_formats
from app.validation.rules.line_rows import check_rows
from app.validation.rules.required_fields import check_required

log = get_logger(__name__)
REVIEW_MESSAGE = "Models disagreed or one returned no value; needs review"


def _model_review_issues(result: ExtractionResult) -> list[Issue]:
    issues = [Issue(name, "model_disagreement", "warning", REVIEW_MESSAGE)
              for name, field in result.fields.items() if field.flagged]
    if result.line_items_flagged:
        issues.append(Issue("line_items", "model_disagreement", "warning", REVIEW_MESSAGE))
    return issues


def validate_extraction(doc_type: str, result: ExtractionResult) -> list[Issue]:
    fields, items = result.fields, result.line_items
    issues = (
        check_required(doc_type, fields)
        + check_formats(fields)
        + check_date_order(doc_type, fields)
        + check_total(fields)
        + check_items_sum(fields, items)
        + check_rows(items)
        + _model_review_issues(result)
    )
    errors = sum(1 for i in issues if i.severity == "error")
    log.info("validation done issues=%d errors=%d", len(issues), errors)
    return issues
