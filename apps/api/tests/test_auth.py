"""Tests for the Supabase JWT verification dependency and `/me`.

These tests never talk to a real Supabase project. Instead they sign
tokens themselves with a throwaway HS256 secret and point
`SUPABASE_JWT_SECRET` at that same secret, exactly as recommended for
testing auth without live credentials. This verifies the *verification
logic* (accepts valid tokens, rejects missing/invalid/expired/
wrong-secret/wrong-audience ones) but does not exercise Supabase's real
token issuance, key rotation, or JWKS infrastructure.
"""

import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app

TEST_SECRET = "test-only-secret-do-not-use-in-prod-0123456789"

client = TestClient(app)


@pytest.fixture(autouse=True)
def _configure_jwt_secret(monkeypatch):
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_SECRET)
    monkeypatch.setenv("SUPABASE_JWT_AUD", "authenticated")


def _make_token(
    *,
    sub: str | None = "user-123",
    email: str | None = "user@example.com",
    exp_delta: int = 3600,
    secret: str = TEST_SECRET,
    aud: str | None = "authenticated",
    algorithm: str = "HS256",
) -> str:
    now = int(time.time())
    payload = {"iat": now, "exp": now + exp_delta}
    if sub is not None:
        payload["sub"] = sub
    if email is not None:
        payload["email"] = email
    if aud is not None:
        payload["aud"] = aud
    return jwt.encode(payload, secret, algorithm=algorithm)


def test_me_with_valid_token_returns_user_id_and_email():
    token = _make_token(sub="user-123", email="user@example.com")

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"id": "user-123", "email": "user@example.com"}


def test_me_without_authorization_header_returns_401():
    response = client.get("/me")

    assert response.status_code == 401


def test_me_with_malformed_token_returns_401():
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_me_with_expired_token_returns_401():
    token = _make_token(exp_delta=-3600)

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_wrong_signing_secret_returns_401():
    token = _make_token(secret="a-completely-different-secret-0123456789")

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_wrong_audience_returns_401():
    token = _make_token(aud="not-authenticated")

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_token_missing_subject_claim_returns_401():
    token = _make_token(sub=None)

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_non_bearer_scheme_returns_401():
    token = _make_token()

    response = client.get("/me", headers={"Authorization": f"Token {token}"})

    assert response.status_code == 401
