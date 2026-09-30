import pytest

from app.errors import ModelUnavailableError, TransientError
from app.llm import gemini_client, mistral_client
from app.llm.router import LLMRouter
from app.llm.types import LLMResult


def _ok(model):
    return lambda prompt: LLMResult("answer", model, 10, 5)


def _fail(prompt):
    raise TransientError("rate limited")


def _router():
    return LLMRouter(sleep=lambda s: None)


def test_gemini_success_never_calls_mistral(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", _ok("gemini-2.5-flash"))
    monkeypatch.setattr(mistral_client, "generate", lambda p: pytest.fail("called"))
    assert _router().generate("hi").model == "gemini-2.5-flash"


def test_gemini_failure_falls_back_to_mistral(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", _fail)
    monkeypatch.setattr(mistral_client, "generate", _ok("mistral-small-latest"))
    assert _router().generate("hi").model == "mistral-small-latest"


def test_gemini_is_retried_three_times_before_fallback(monkeypatch):
    calls = []
    monkeypatch.setattr(gemini_client, "generate", lambda p: calls.append(1) or _fail(p))
    monkeypatch.setattr(mistral_client, "generate", _ok("mistral-small-latest"))
    _router().generate("hi")
    assert len(calls) == 3


def test_both_models_failing_raises(monkeypatch):
    monkeypatch.setattr(gemini_client, "generate", _fail)
    monkeypatch.setattr(mistral_client, "generate", _fail)
    with pytest.raises(ModelUnavailableError):
        _router().generate("hi")
