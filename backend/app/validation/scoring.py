from app.extraction.schemas import ExtractionResult
from app.validation.issue import Issue

ERROR_PENALTY = 0.1


def overall_confidence(result: ExtractionResult, issues: list[Issue]) -> float:
    """Mean confidence of the fields found, reduced for each rule error."""
    found = [f.confidence for f in result.fields.values() if f.value]
    if not found:
        return 0.0
    errors = sum(1 for i in issues if i.severity == "error")
    return round(max(sum(found) / len(found) - ERROR_PENALTY * errors, 0.0), 3)
