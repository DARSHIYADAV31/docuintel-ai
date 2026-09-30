import re
from datetime import date
from decimal import Decimal, InvalidOperation

from dateutil import parser as date_parser

AMOUNT_FIELDS = {"subtotal", "tax", "total", "contract_value", "unit_price", "amount"}
DATE_FIELDS = {"invoice_date", "due_date", "order_date", "effective_date", "end_date"}


def normalize_amount(value) -> str | None:
    cleaned = re.sub(r"[^\d.\-]", "", str(value).replace(",", ""))
    try:
        return str(Decimal(cleaned).quantize(Decimal("0.01")))
    except InvalidOperation:
        return None


def normalize_date(value) -> str | None:
    try:
        parsed: date = date_parser.parse(str(value)).date()
    except (ValueError, OverflowError):
        return None
    return parsed.isoformat()


def normalize_value(name: str, value) -> str | None:
    """Canonical form for comparing two models' answers; None if empty/unparseable."""
    if value is None or not str(value).strip():
        return None
    if name in AMOUNT_FIELDS:
        return normalize_amount(value)
    if name in DATE_FIELDS:
        return normalize_date(value)
    return " ".join(str(value).lower().split())


def is_well_formed(name: str, value) -> bool:
    return normalize_value(name, value) is not None
