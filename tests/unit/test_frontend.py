import sys
from pathlib import Path

import pytest
import requests

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
sys.path.insert(0, str(FRONTEND))

from api_client import ApiClient  # noqa: E402
from http_client import ApiError  # noqa: E402


class FakeResponse:
    def __init__(self, status=200, body=None):
        self.status_code, self._body, self.ok = status, body or {}, status < 400

    def json(self):
        return self._body


TOKENS = {"access_token": "new-access", "refresh_token": "new-refresh"}


def test_login_stores_tokens(monkeypatch):
    monkeypatch.setattr(requests, "request", lambda *a, **k: FakeResponse(200, TOKENS))
    tokens = {}
    ApiClient("http://x", tokens).login("alice", "password1")
    assert tokens == {"access": "new-access", "refresh": "new-refresh"}


def test_expired_token_is_refreshed_and_request_retried(monkeypatch):
    replies = iter([FakeResponse(401), FakeResponse(200, {"ok": True})])
    monkeypatch.setattr(requests, "request", lambda *a, **k: next(replies))
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResponse(200, TOKENS))
    tokens = {"access": "old", "refresh": "r"}
    assert ApiClient("http://x", tokens).dashboard() == {"ok": True}
    assert tokens["access"] == "new-access"


def test_failed_refresh_clears_session(monkeypatch):
    monkeypatch.setattr(requests, "request", lambda *a, **k: FakeResponse(401, {"detail": "expired"}))
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResponse(401))
    tokens = {"access": "old", "refresh": "r"}
    with pytest.raises(ApiError):
        ApiClient("http://x", tokens).dashboard()
    assert tokens == {}


def test_server_error_message_is_surfaced(monkeypatch):
    reply = FakeResponse(422, {"detail": "File is empty"})
    monkeypatch.setattr(requests, "request", lambda *a, **k: reply)
    with pytest.raises(ApiError, match="File is empty"):
        ApiClient("http://x", {}).upload("a.pdf", b"", "application/pdf", False)


@pytest.mark.parametrize("error, message", [
    (requests.Timeout(), "too long"), (requests.ConnectionError(), "Cannot reach")])
def test_network_problems_become_friendly_errors(monkeypatch, error, message):
    def fail(*a, **k):
        raise error

    monkeypatch.setattr(requests, "request", fail)
    with pytest.raises(ApiError, match=message):
        ApiClient("http://x", {}).list_documents()


def test_every_request_has_a_timeout(monkeypatch):
    seen = {}
    monkeypatch.setattr(requests, "request",
                        lambda *a, **k: seen.update(k) or FakeResponse(200, []))
    ApiClient("http://x", {}).list_documents()
    assert seen["timeout"] > 0
