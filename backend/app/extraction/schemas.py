from dataclasses import dataclass, field

FIELDS = {
    "invoice": ["invoice_number", "vendor_name", "invoice_date", "due_date",
                "currency", "subtotal", "tax", "total", "bank_account"],
    "po": ["po_number", "vendor_name", "order_date", "currency", "subtotal",
           "tax", "total"],
    "contract": ["contract_title", "party_a", "party_b", "effective_date",
                 "end_date", "contract_value", "governing_law", "payment_terms"],
}
HAS_LINE_ITEMS = {"invoice", "po"}
SENSITIVE_FIELDS = {"bank_account"}


@dataclass
class FieldValue:
    value: str | None
    confidence: float
    flagged: bool


@dataclass
class ExtractionResult:
    fields: dict[str, FieldValue]
    line_items: list[dict] = field(default_factory=list)
    line_items_flagged: bool = False
