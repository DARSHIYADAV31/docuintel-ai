from datetime import date
from decimal import Decimal

from app.extraction.normalizers import normalize_amount, normalize_date

TOLERANCE = Decimal("0.01")


def amount_of(raw) -> Decimal | None:
    normalized = normalize_amount(raw) if raw not in (None, "") else None
    return Decimal(normalized) if normalized else None


def date_of(raw) -> date | None:
    normalized = normalize_date(raw) if raw not in (None, "") else None
    return date.fromisoformat(normalized) if normalized else None


def field_amount(fields: dict, name: str) -> Decimal | None:
    return amount_of(fields[name].value) if name in fields else None


def field_date(fields: dict, name: str) -> date | None:
    return date_of(fields[name].value) if name in fields else None


def is_close(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= TOLERANCE
