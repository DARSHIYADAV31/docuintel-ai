"""Real OCR + real Gemini/Mistral. Run with: pytest -m eval (needs API keys in .env)."""
import os
from pathlib import Path

import pytest

from app.config import get_settings
from app.evaluation.labels import load_cases
from app.evaluation.runner import evaluate
from app.llm.router import LLMRouter

DATASET = Path(__file__).resolve().parents[2] / "eval" / "dataset"
MIN_ACCURACY = float(os.getenv("EVAL_MIN_ACCURACY", "0.85"))


@pytest.mark.eval
def test_extraction_accuracy_meets_threshold():
    get_settings.cache_clear()
    settings = get_settings()
    if not (settings.gemini_api_key and settings.mistral_api_key):
        pytest.skip("API keys are not configured")
    summary = evaluate(load_cases(DATASET), LLMRouter)["summary"]
    assert summary["overall_accuracy"] >= MIN_ACCURACY, summary["per_field_accuracy"]
