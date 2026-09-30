from datetime import timedelta

import pytest

from app.auth.jwt_tokens import _create, create_access_token, decode_token
from app.errors import InvalidTokenError

CREDS = {"username": "alice", "password": "s3cret-pass"}


def test_register_login_and_access_protected_route(client):
    assert client.post("/auth/register", json=CREDS).status_code == 201
    tokens = client.post("/auth/login", json=CREDS).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.get("/me", headers=headers).json()["username"] == "alice"


def test_wrong_password_rejected(client):
    client.post("/auth/register", json=CREDS)
    bad = {**CREDS, "password": "wrong-password"}
    assert client.post("/auth/login", json=bad).status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/me").status_code in (401, 403)


def test_refresh_returns_new_tokens(client):
    tokens = client.post("/auth/register", json=CREDS).json()
    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200


def test_access_token_cannot_be_used_to_refresh(client):
    tokens = client.post("/auth/register", json=CREDS).json()
    resp = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


def test_expired_token_rejected():
    expired = _create(1, "access", timedelta(seconds=-5))
    with pytest.raises(InvalidTokenError):
        decode_token(expired, "access")


def test_valid_token_round_trip():
    assert decode_token(create_access_token(7), "access") == 7


def test_restart_marks_stuck_documents_failed(db_session):
    from app.db.repositories import document_repo, user_repo

    owner = user_repo.create_user(db_session, "carol", "hash")
    doc = document_repo.create(db_session, owner.id, "a.pdf", "a.pdf", False)
    assert document_repo.fail_interrupted(db_session) == 1
    assert document_repo.get(db_session, doc.id).status == "failed"
