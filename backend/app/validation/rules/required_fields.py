from app.validation.issue import Issue

REQUIRED = {
    "invoice": ["invoice_number", "vendor_name", "invoice_date", "total"],
    "po": ["po_number", "vendor_name", "total"],
    "contract": ["party_a", "party_b", "effective_date"],
}


def check_required(doc_type: str, fields: dict) -> list[Issue]:
    missing = [n for n in REQUIRED.get(doc_type, [])
               if n not in fields or not fields[n].value]
    return [Issue(n, "required", "error", "Required field is missing") for n in missing]
