from app.validation.issue import Issue
from app.validation.rules.values import amount_of, field_amount, is_close


def check_total(fields: dict) -> list[Issue]:
    subtotal, tax, total = (field_amount(fields, n) for n in ("subtotal", "tax", "total"))
    if None in (subtotal, tax, total) or is_close(subtotal + tax, total):
        return []
    message = f"Subtotal + tax ({subtotal + tax}) does not equal total ({total})"
    return [Issue("total", "total_math", "error", message)]


def check_items_sum(fields: dict, items: list[dict]) -> list[Issue]:
    subtotal = field_amount(fields, "subtotal")
    amounts = [amount_of(row.get("amount")) for row in items]
    if subtotal is None or not items or None in amounts:
        return []
    if is_close(sum(amounts), subtotal):
        return []
    message = f"Line items add up to {sum(amounts)}, subtotal says {subtotal}"
    return [Issue("line_items", "items_sum", "error", message)]
