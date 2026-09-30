"""Runs the real evaluation runner over the shipped dataset with fake OCR and LLMs."""
import json
from pathlib import Path

import numpy as np
import pytest

from app.evaluation.labels import load_cases
from app.evaluation.runner import evaluate
from app.llm import gemini_client, mistral_client
from app.llm.router import LLMRouter
from app.llm.types import LLMResult
from app.ocr import docling_engine
from app.ocr.types import OCRResult
from app.vectorstore import embedder

DATASET = Path(__file__).resolve().parents[2] / "eval" / "dataset"


def _fake_embed(texts):
    arr = np.array([[len(t) % 7 + 1.0, len(t) % 5 + 1.0, 1.0] for t in texts], dtype="float32")
    return arr / np.linalg.norm(arr, axis=1, keepdims=True)


@pytest.fixture
def perfect_models(monkeypatch):
    """Fake OCR + LLMs that return each document's own labeled values."""
    cases = {c.path.name: c for c in load_cases(DATASET)}
    current = {}

    def fake_ocr(path):
        current["case"] = cases[Path(path).name]
        return OCRResult(f"document {Path(path).name} " + "x" * 30, "docling")

    def fake_llm(wrong_field=None):
        def generate(prompt, json_mode=False):
            case = current["case"]
            if "You classify" in prompt:
                reply = {"doc_type": case.doc_type, "confidence": 0.99}
            else:
                fields = dict(case.fields)
                if wrong_field in fields:
                    fields[wrong_field] = "WRONG"
                rows = [{"description": f"r{i}", "amount": "1"}
                        for i in range(case.line_item_count or 0)]
                reply = {"fields": fields, "line_items": rows}
            return LLMResult(json.dumps(reply), "gemini-2.5-flash", 50, 10)
        return generate

    monkeypatch.setattr(docling_engine, "run_docling", fake_ocr)
    monkeypatch.setattr(embedder, "embed_texts", _fake_embed)
    monkeypatch.setattr(gemini_client, "generate", fake_llm())
    monkeypatch.setattr(mistral_client, "generate", fake_llm())
    return fake_llm


def test_perfect_models_score_full_marks(perfect_models):
    report = evaluate(load_cases(DATASET), LLMRouter)
    summary = report["summary"]
    assert summary["documents"] == 4 and summary["failed_documents"] == 0
    assert summary["doc_type_accuracy"] == 1.0
    assert summary["line_item_count_accuracy"] == 1.0
    assert summary["overall_accuracy"] == 1.0


def test_injected_error_lowers_accuracy(perfect_models, monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", perfect_models("vendor_name"))
    monkeypatch.setattr(mistral_client, "generate", perfect_models("vendor_name"))
    report = evaluate(load_cases(DATASET), LLMRouter)
    summary = report["summary"]
    assert summary["overall_accuracy"] < 1.0
    assert summary["per_field_accuracy"]["vendor_name"] == 0.0
    assert summary["per_field_accuracy"]["total"] == 1.0
