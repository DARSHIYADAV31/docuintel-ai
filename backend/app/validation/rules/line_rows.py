from app.validation.issue import Issue
from app.validation.rules.values import amount_of, is_close


def _row_issue(number: int, row: dict) -> Issue | None:
    qty, price, amount = (amount_of(row.get(k)) for k in ("quantity", "unit_price", "amount"))
    if None in (qty, price, amount) or is_close(qty * price, amount):
        return None
    message = f"Line {number}: quantity x unit price does not equal amount"
    return Issue("line_items", "row_math", "warning", message)


def check_rows(items: list[dict]) -> list[Issue]:
    found = (_row_issue(i, row) for i, row in enumerate(items, start=1))
    return [issue for issue in found if issue]
