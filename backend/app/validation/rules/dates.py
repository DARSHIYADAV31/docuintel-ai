from app.validation.issue import Issue
from app.validation.rules.values import field_date

ORDERED_PAIRS = {
    "invoice": [("invoice_date", "due_date")],
    "contract": [("effective_date", "end_date")],
}


def check_date_order(doc_type: str, fields: dict) -> list[Issue]:
    issues = []
    for first, second in ORDERED_PAIRS.get(doc_type, []):
        start, end = field_date(fields, first), field_date(fields, second)
        if start and end and end < start:
            message = f"{second} is earlier than {first}"
            issues.append(Issue(second, "date_order", "error", message))
    return issues
