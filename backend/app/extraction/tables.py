from decimal import Decimal

from app.extraction.normalizers import normalize_amount, normalize_value


def clean_rows(rows) -> list[dict]:
    return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []


def _signature(rows: list[dict]) -> list[tuple]:
    return [(normalize_value("description", r.get("description")),
             normalize_amount(r.get("amount"))) for r in rows]


def _rows_total(rows: list[dict]) -> Decimal | None:
    amounts = [normalize_amount(r.get("amount")) for r in rows]
    if not rows or None in amounts:
        return None
    return sum(Decimal(a) for a in amounts)


def _matches(rows: list[dict], subtotal: str | None) -> bool:
    total, target = _rows_total(rows), normalize_amount(subtotal)
    return total is not None and target is not None and total == Decimal(target)


def reconcile_line_items(gemini: list[dict] | None, mistral: list[dict] | None,
                         subtotal: str | None) -> tuple[list[dict], bool]:
    """Returns (rows, needs_review)."""
    if gemini is None or mistral is None:
        return (gemini if gemini is not None else mistral) or [], False
    if _signature(gemini) == _signature(mistral):
        return gemini, False
    gemini_ok, mistral_ok = _matches(gemini, subtotal), _matches(mistral, subtotal)
    if mistral_ok and not gemini_ok:
        return mistral, True
    return gemini, True
