from app.extraction.schemas import ExtractionResult, FieldValue
from app.validation.agent import validate_extraction
from app.validation.scoring import overall_confidence


def _fields(**values):
    return {k: FieldValue(v, 0.95, False) for k, v in values.items()}


GOOD = dict(invoice_number="INV-1", vendor_name="Acme", invoice_date="2024-01-10",
            due_date="2024-02-10", subtotal="100", tax="10", total="110")
ITEMS = [{"description": "A", "quantity": "2", "unit_price": "30", "amount": "60"},
         {"description": "B", "quantity": "1", "unit_price": "40", "amount": "40"}]


def _rules(fields, items=None, doc_type="invoice"):
    result = ExtractionResult(_fields(**fields), items or [])
    return {i.rule for i in validate_extraction(doc_type, result)}


def test_clean_invoice_has_no_issues():
    assert _rules(GOOD, ITEMS) == set()


def test_missing_required_field_flagged():
    assert "required" in _rules({**GOOD, "invoice_number": None})


def test_total_mismatch_flagged():
    assert "total_math" in _rules({**GOOD, "total": "999"})


def test_line_items_not_matching_subtotal_flagged():
    assert "items_sum" in _rules({**GOOD, "subtotal": "500", "total": "510"}, ITEMS)


def test_row_math_mismatch_flagged():
    bad = [{"description": "A", "quantity": "2", "unit_price": "30", "amount": "99"}]
    assert "row_math" in _rules(GOOD, bad)


def test_due_date_before_invoice_date_flagged():
    assert "date_order" in _rules({**GOOD, "due_date": "2023-12-01"})


def test_unparseable_amount_flagged():
    assert "format" in _rules({**GOOD, "total": "abc"})


def test_flagged_model_disagreement_surfaces_as_issue():
    fields = _fields(**GOOD)
    fields["total"].flagged = True
    issues = validate_extraction("invoice", ExtractionResult(fields, []))
    assert any(i.rule == "model_disagreement" for i in issues)


def test_small_rounding_difference_is_tolerated():
    assert "total_math" not in _rules({**GOOD, "total": "110.01"})


def test_confidence_drops_with_errors():
    result = ExtractionResult(_fields(**GOOD), [])
    clean = overall_confidence(result, [])
    bad = validate_extraction("invoice", ExtractionResult(_fields(**{**GOOD, "total": "9"}), []))
    assert overall_confidence(result, bad) < clean
