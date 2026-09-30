import json

import pytest

from app.classification.classifier import classify_document
from app.errors import DocuIntelError, ModelUnavailableError, TransientError
from app.extraction.key_values import extract_document
from app.extraction.normalizers import normalize_value
from app.extraction.reconcile import reconcile_fields
from app.extraction.tables import reconcile_line_items
from app.llm.types import LLMResult


class FakeRouter:
    def __init__(self, gemini=None, mistral=None, generate_reply=""):
        self.replies = {"gemini": gemini, "mistral": mistral}
        self.generate_reply = generate_reply

    def call_single(self, name, prompt, json_mode=False):
        reply = self.replies[name]
        if reply is None:
            raise TransientError("down")
        return LLMResult(json.dumps(reply), name, 1, 1)

    def generate(self, prompt, json_mode=False):
        return LLMResult(self.generate_reply, "gemini", 1, 1)


def _reply(total="100.00", items=None):
    return {"fields": {"invoice_number": "INV-1", "total": total},
            "line_items": items or []}


def test_amount_and_date_normalization():
    assert normalize_value("total", "$1,234.5") == "1234.50"
    assert normalize_value("invoice_date", "March 5, 2024") == "2024-03-05"
    assert normalize_value("total", "abc") is None


def test_agreeing_models_give_high_confidence():
    result = reconcile_fields(["total"], {"total": "1,000.00"}, {"total": "1000"})
    assert result["total"].confidence >= 0.9 and not result["total"].flagged


def test_disagreement_is_flagged_and_prefers_gemini():
    result = reconcile_fields(["total"], {"total": "100"}, {"total": "900"})
    assert result["total"].value == "100" and result["total"].flagged


def test_well_formed_mistral_beats_malformed_gemini():
    result = reconcile_fields(["total"], {"total": "one hundred"}, {"total": "100"})
    assert result["total"].value == "100"


def test_single_model_caps_confidence():
    result = reconcile_fields(["total"], {"total": "100"}, None)
    assert result["total"].confidence <= 0.7


def test_line_items_pick_set_matching_subtotal():
    good = [{"description": "A", "amount": "60"}, {"description": "B", "amount": "40"}]
    bad = [{"description": "A", "amount": "60"}]
    rows, flagged = reconcile_line_items(bad, good, "100")
    assert rows == good and flagged


def test_extract_document_reconciles_both_models():
    router = FakeRouter(gemini=_reply("100.00"), mistral=_reply("100"))
    result = extract_document(router, "text", "invoice")
    assert result.fields["total"].confidence >= 0.9


def test_extract_survives_one_model_down():
    result = extract_document(FakeRouter(gemini=_reply()), "text", "invoice")
    assert result.fields["total"].value == "100.00"


def test_extract_fails_loudly_when_both_down():
    with pytest.raises(ModelUnavailableError):
        extract_document(FakeRouter(), "text", "invoice")


def test_unsupported_doc_type_rejected():
    with pytest.raises(DocuIntelError):
        extract_document(FakeRouter(gemini=_reply()), "text", "unknown")


def test_classification_parses_reply():
    router = FakeRouter(generate_reply='{"doc_type": "PO", "confidence": 0.9}')
    assert classify_document(router, "text").doc_type == "po"


def test_classification_bad_reply_becomes_unknown():
    router = FakeRouter(generate_reply="I think it is an invoice")
    assert classify_document(router, "text").doc_type == "unknown"


def test_json_wrapped_in_commentary_still_parses():
    from app.llm.json_utils import parse_json_object

    reply = 'Sure! Here you go:\n```json\n{"fields": {"total": "5"}}\n```\nHope that helps.'
    assert parse_json_object(reply)["fields"]["total"] == "5"


def test_low_confidence_classification_becomes_unknown():
    router = FakeRouter(generate_reply='{"doc_type": "invoice", "confidence": 0.2}')
    assert classify_document(router, "payslip text").doc_type == "unknown"


def test_other_document_type_becomes_unknown():
    router = FakeRouter(generate_reply='{"doc_type": "other", "confidence": 0.95}')
    assert classify_document(router, "payslip text").doc_type == "unknown"


def test_invalid_json_is_asked_again_once():
    class Flaky(FakeRouter):
        calls = 0

        def call_single(self, name, prompt, json_mode=False):
            Flaky.calls += name == "gemini"
            if name == "gemini" and Flaky.calls == 1:
                return LLMResult("not json at all", name, 1, 1)
            return super().call_single(name, prompt, json_mode)

    result = extract_document(Flaky(gemini=_reply(), mistral=None), "text", "invoice")
    assert Flaky.calls == 2 and result.fields["total"].value == "100.00"


def test_model_outage_during_classification_is_not_reported_as_unknown_type():
    class Down(FakeRouter):
        def generate(self, prompt, json_mode=False):
            raise ModelUnavailableError("down")

    with pytest.raises(ModelUnavailableError):
        classify_document(Down(), "text")
