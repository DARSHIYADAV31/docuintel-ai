import io
import json
import logging

import numpy as np
import pytest
from pypdf import PdfWriter

from app.errors import TransientError
from app.ingestion import storage
from app.llm import gemini_client, mistral_client
from app.llm.types import LLMResult
from app.ocr import docling_engine, paddle_engine
from app.ocr.types import OCRResult
from app.vectorstore import embedder, factory

ACCOUNT = "DE89370400440532013000"
OCR_TEXT = "Invoice INV-1 from Acme. Payment is due within 30 days. Total 110 USD."
EXTRACTION = {
    "fields": {"invoice_number": "INV-1", "vendor_name": "Acme", "currency": "USD",
               "invoice_date": "2024-01-10", "due_date": "2024-02-10", "subtotal": "100",
               "tax": "10", "total": "110", "bank_account": ACCOUNT},
    "line_items": [{"description": "A", "quantity": "2", "unit_price": "30", "amount": "60"},
                   {"description": "B", "quantity": "1", "unit_price": "40", "amount": "40"}],
}


def _fake_llm(extraction):
    def generate(prompt, json_mode=False):
        if "You classify" in prompt:
            reply = '{"doc_type": "invoice", "confidence": 0.97}'
        elif "You extract" in prompt:
            reply = json.dumps(extraction)
        else:
            reply = "Payment is due within 30 days [1]."
        return LLMResult(reply, "gemini-2.5-flash", 100, 20)
    return generate


def _fake_embed(texts):
    keywords = ["payment", "days", "invoice", "total"]
    arr = np.array([[t.lower().count(k) + 0.01 for k in keywords] for t in texts], dtype="float32")
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


@pytest.fixture
def backends(monkeypatch, tmp_path):
    monkeypatch.setattr(storage, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(factory, "DATA_DIR", tmp_path / "vectors")
    monkeypatch.setattr(embedder, "embed_texts", _fake_embed)
    monkeypatch.setattr(docling_engine, "run_docling", lambda p: OCRResult(OCR_TEXT, "docling"))
    monkeypatch.setattr(gemini_client, "generate", _fake_llm(EXTRACTION))
    monkeypatch.setattr(mistral_client, "generate", _fake_llm(EXTRACTION))


def _pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _login(client, name="alice") -> dict:
    creds = {"username": name, "password": "s3cret-pass"}
    token = client.post("/auth/register", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _upload(client, headers, data=None, name="inv.pdf", **form):
    files = {"file": (name, data or _pdf(), "application/pdf")}
    return client.post("/documents", files=files, data=form, headers=headers)


def test_full_pipeline_upload_to_answer(client, backends, caplog):
    caplog.set_level(logging.INFO)
    headers = _login(client)
    doc_id = _upload(client, headers).json()["id"]

    detail = client.get(f"/documents/{doc_id}", headers=headers).json()
    assert detail["status"] == "completed" and detail["doc_type"] == "invoice"
    assert detail["confidence"] > 0.9 and detail["issues"] == []
    assert len(detail["line_items"]) == 2
    assert detail["processing_summary"]["llm"]["calls"] >= 3

    fields = {f["name"]: f["value"] for f in detail["fields"]}
    assert fields["total"] == "110" and fields["bank_account"].endswith("3000")
    assert ACCOUNT not in fields["bank_account"]

    ask = client.post(f"/documents/{doc_id}/ask", json={"question": "When is payment due?"},
                      headers=headers).json()
    assert ask["grounded"] and ask["citations"]
    assert ACCOUNT not in caplog.text  # sensitive values never reach the logs


def test_reveal_returns_full_value(client, backends):
    headers = _login(client)
    doc_id = _upload(client, headers).json()["id"]
    url = f"/documents/{doc_id}?reveal_sensitive=true"
    fields = {f["name"]: f["value"] for f in client.get(url, headers=headers).json()["fields"]}
    assert fields["bank_account"] == ACCOUNT


def test_other_users_cannot_see_document(client, backends):
    doc_id = _upload(client, _login(client, "alice")).json()["id"]
    bob = _login(client, "bobby")
    assert client.get(f"/documents/{doc_id}", headers=bob).status_code == 404
    assert client.post(f"/documents/{doc_id}/ask", json={"question": "anything?"},
                       headers=bob).status_code == 404


def test_math_mismatch_marks_document_for_review(client, backends, monkeypatch):
    bad = {**EXTRACTION, "fields": {**EXTRACTION["fields"], "total": "999"}}
    monkeypatch.setattr(gemini_client, "generate", _fake_llm(bad))
    monkeypatch.setattr(mistral_client, "generate", _fake_llm(bad))
    headers = _login(client)
    detail = client.get(f"/documents/{_upload(client, headers).json()['id']}",
                        headers=headers).json()
    assert detail["status"] == "needs_review"
    assert any(i["rule"] == "total_math" for i in detail["issues"])


def test_gemini_outage_still_completes_via_mistral(client, backends, monkeypatch):
    def down(prompt):
        raise TransientError("rate limited")

    monkeypatch.setattr(gemini_client, "generate", down)
    headers = _login(client)
    detail = client.get(f"/documents/{_upload(client, headers).json()['id']}",
                        headers=headers).json()
    assert detail["status"] in ("completed", "needs_review")
    assert detail["fields"]


def test_ocr_failure_reports_failed_status(client, backends, monkeypatch):
    def boom(path):
        raise RuntimeError("engine crashed")

    monkeypatch.setattr(docling_engine, "run_docling", boom)
    monkeypatch.setattr(paddle_engine, "run_paddle", boom)
    headers = _login(client)
    detail = client.get(f"/documents/{_upload(client, headers).json()['id']}",
                        headers=headers).json()
    assert detail["status"] == "failed" and "ocr" in detail["error_message"]


def test_invalid_upload_rejected_before_processing(client, backends):
    headers = _login(client)
    response = _upload(client, headers, data=b"MZ not a document", name="invoice.pdf")
    assert response.status_code == 422
    assert client.get("/documents", headers=headers).json() == []


def test_dashboard_summarizes_documents(client, backends):
    headers = _login(client)
    _upload(client, headers)
    data = client.get("/dashboard", headers=headers).json()
    assert data["total_documents"] == 1 and data["by_status"]["completed"] == 1
    assert data["total_cost_usd"] > 0


def test_endpoints_require_authentication(client):
    assert client.get("/documents").status_code in (401, 403)
    assert client.get("/dashboard").status_code in (401, 403)


def test_ask_on_unindexed_document_explains_instead_of_saying_no_info(client, backends, monkeypatch):
    def no_embedding(texts):
        raise __import__("app.errors", fromlist=["VectorStoreError"]).VectorStoreError("down")

    monkeypatch.setattr(embedder, "embed_texts", no_embedding)
    headers = _login(client)
    doc_id = _upload(client, headers).json()["id"]
    reply = client.post(f"/documents/{doc_id}/ask", json={"question": "Invoice number?"},
                        headers=headers)
    assert reply.status_code == 409 and "upload it again" in reply.json()["detail"]
