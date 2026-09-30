import json

import pytest

from app.errors import DocuIntelError
from app.evaluation.comparer import compare_fields, describe_mismatches
from app.evaluation.labels import load_cases
from app.evaluation.metrics import aggregate
from app.evaluation.report import write_report
from app.evaluation.types import CaseResult


def _result(field_ok, status="completed", doc_type_ok=True, items_ok=True):
    return CaseResult("a.png", status, doc_type_ok, field_ok, items_ok, 0.9, 0.01, 1.0)


def test_amounts_and_dates_match_after_normalization():
    expected = {"total": "1000.00", "invoice_date": "2024-03-05", "vendor_name": "Acme Ltd"}
    actual = {"total": "1,000", "invoice_date": "March 5, 2024", "vendor_name": "acme  ltd"}
    assert all(compare_fields(expected, actual).values())


def test_wrong_and_missing_values_do_not_match():
    result = compare_fields({"total": "100", "tax": "5"}, {"total": "101"})
    assert result == {"total": False, "tax": False}


def test_sensitive_values_hidden_in_mismatch_report():
    expected, actual = {"bank_account": "DE89"}, {"bank_account": "DE00"}
    found = describe_mismatches(expected, actual, compare_fields(expected, actual))
    assert found["bank_account"] == {"expected": "<hidden>", "actual": "<hidden>"}


def test_aggregate_computes_accuracy_per_field_and_overall():
    results = [_result({"total": True, "tax": False}),
               _result({"total": True, "tax": True}, doc_type_ok=False)]
    summary = aggregate(results)
    assert summary["overall_accuracy"] == 0.75
    assert summary["per_field_accuracy"] == {"tax": 0.5, "total": 1.0}
    assert summary["doc_type_accuracy"] == 0.5


def test_failed_document_counted():
    assert aggregate([_result({"total": False}, status="failed")])["failed_documents"] == 1


def test_labels_loader_reports_missing_files(tmp_path):
    entry = {"file": "gone.png", "doc_type": "invoice", "fields": {}}
    (tmp_path / "labels.json").write_text(json.dumps({"cases": [entry]}))
    with pytest.raises(DocuIntelError):
        load_cases(tmp_path)


def test_report_written_with_latest_copy(tmp_path):
    report = {"created_at": "2024-01-01T10:00:00+00:00", "summary": {}, "cases": []}
    path = write_report(report, tmp_path)
    assert path.exists() and (tmp_path / "latest.json").exists()
