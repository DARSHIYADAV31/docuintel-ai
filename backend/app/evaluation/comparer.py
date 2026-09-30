from app.extraction.normalizers import normalize_value
from app.extraction.schemas import SENSITIVE_FIELDS


def field_matches(name: str, expected, actual) -> bool:
    """Compare after normalizing, so '1,000' equals '1000.00' and dates match by day."""
    wanted = normalize_value(name, expected)
    return wanted is not None and wanted == normalize_value(name, actual)


def compare_fields(expected: dict, actual: dict) -> dict[str, bool]:
    return {name: field_matches(name, value, actual.get(name))
            for name, value in expected.items()}


def describe_mismatches(expected: dict, actual: dict, results: dict[str, bool]) -> dict:
    """Wrong fields with both values; sensitive values are never written out."""
    hide = lambda name, value: "<hidden>" if name in SENSITIVE_FIELDS else value
    return {name: {"expected": hide(name, expected[name]),
                   "actual": hide(name, actual.get(name))}
            for name, ok in results.items() if not ok}
