from app.extraction.normalizers import AMOUNT_FIELDS, DATE_FIELDS, is_well_formed
from app.validation.issue import Issue

TYPED_FIELDS = (AMOUNT_FIELDS | DATE_FIELDS) - {"unit_price", "amount"}


def check_formats(fields: dict) -> list[Issue]:
    issues = []
    for name, field in fields.items():
        if name in TYPED_FIELDS and field.value and not is_well_formed(name, field.value):
            issues.append(Issue(name, "format", "error", "Value could not be parsed"))
    return issues
