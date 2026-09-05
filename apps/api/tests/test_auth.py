"""Tests for the Supabase JWT verification dependency and `/me`.

These tests never talk to a real Supabase project or make a real HTTP
call. The Supabase project this app targets signs access tokens with
ES256 (asymmetric) via its JWKS-based "JWT Signing Keys" system, so the
tests here:

- generate a real EC (P-256) keypair,
- sign test JWTs with the private key using PyJWT (exactly like
  Supabase would),
- and stand in for the network fetch inside PyJWT's own `PyJWKClient` by
  subclassing it and overriding `fetch_data()` to return a static JWKS
  document (built from the *public* key, in real JWK format) instead of
  making an HTTP request.

Everything else — parsing the JWKS, matching `kid`, verifying the ES256
signature, checking `exp`/`aud`/`sub` — is the real PyJWT/`app.auth`
code path, not re-implemented or bypassed. This genuinely exercises
JWKS/ES256 verification, including rejecting tokens signed with the
wrong key and alg-confusion attempts (`alg=none`, and HS256-signed
tokens that are not in the allowed algorithm list).
"""

from __future__ import annotations

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from jwt import PyJWKClient
from jwt.algorithms import ECAlgorithm

import app.auth as auth_module
from app.main import app

client = TestClient(app)

_KID = "test-kid-1"

# The keypair the "real" JWKS (served by our fake client) advertises.
# Tokens signed with this key's private half should verify successfully.
_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
_PUBLIC_KEY = _PRIVATE_KEY.public_key()

# A second, unrelated keypair used only to simulate a token signed by
# someone who is *not* holding this project's real private key (e.g. a
# forged/stolen token, or a key from a different Supabase project).
_OTHER_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())


def _jwk_for(public_key, kid: str) -> dict:
    jwk = ECAlgorithm.to_jwk(public_key, as_dict=True)
    jwk.update({"kid": kid, "use": "sig", "alg": "ES256"})
    return jwk


class _StaticJWKClient(PyJWKClient):
    """A PyJWKClient that serves a fixed JWKS instead of hitting the network.

    Subclassing (rather than a hand-rolled stand-in) means `get_signing_key_from_jwt`,
    `get_signing_keys`, JWKS parsing, and `kid` matching all run their real
    implementations — only the HTTP fetch is replaced.
    """

    def __init__(self, jwks: dict):
        super().__init__(
            uri="https://example-project.supabase.co/auth/v1/.well-known/jwks.json"
        )
        self._jwks = jwks

    def fetch_data(self):
        return self._jwks


@pytest.fixture(autouse=True)
def _configure_auth(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example-project.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_AUD", "authenticated")

    fake_client = _StaticJWKClient({"keys": [_jwk_for(_PUBLIC_KEY, _KID)]})
    # Replacing the whole (lru_cache-wrapped) function, rather than
    # clearing/populating its cache, means each test gets an isolated
    # fake client regardless of caching behaviour.
    monkeypatch.setattr(auth_module, "_get_jwk_client", lambda: fake_client)
    yield


def _make_token(
    *,
    sub: str | None = "user-123",
    email: str | None = "user@example.com",
    exp_delta: int = 3600,
    private_key=_PRIVATE_KEY,
    aud: str | None = "authenticated",
    algorithm: str = "ES256",
    kid: str | None = _KID,
) -> str:
    now = int(time.time())
    payload = {"iat": now, "exp": now + exp_delta}
    if sub is not None:
        payload["sub"] = sub
    if email is not None:
        payload["email"] = email
    if aud is not None:
        payload["aud"] = aud
    headers = {"kid": kid} if kid is not None else None
    return jwt.encode(payload, private_key, algorithm=algorithm, headers=headers)


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


def test_me_with_token_signed_by_wrong_key_returns_401():
    # Same kid the fake JWKS knows about, but signed with a *different*
    # private key than the one whose public half is in the JWKS -- the
    # signature must fail to verify even though key lookup succeeds.
    token = _make_token(private_key=_OTHER_PRIVATE_KEY)

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_unknown_kid_returns_401():
    token = _make_token(kid="some-other-kid-not-in-jwks")

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


def test_me_with_alg_none_token_returns_401():
    # Classic alg-confusion / signature-stripping attack: a token that
    # claims alg=none and carries no signature at all.
    header = jwt.utils.base64url_encode(
        b'{"alg":"none","typ":"JWT","kid":"' + _KID.encode() + b'"}'
    ).decode()
    now = int(time.time())
    payload_bytes = (
        '{"sub":"user-123","aud":"authenticated","iat":%d,"exp":%d}' % (now, now + 3600)
    ).encode()
    payload = jwt.utils.base64url_encode(payload_bytes).decode()
    token = f"{header}.{payload}."

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_hs256_confusion_token_returns_401():
    # Algorithm-confusion attack: sign a token with HS256, using the
    # ES256 *public* key's PEM bytes as the HMAC secret (a well-known
    # attack against verifiers that naively pass whatever key they look
    # up into HS256 verification). Crafted by hand with hmac/base64url
    # (rather than jwt.encode) because PyJWT's own encoder now refuses to
    # use an asymmetric PEM key as an HMAC secret -- but a real attacker
    # isn't going through our server's encoder, so the forged token must
    # still be rejected on the *verification* side regardless. It must
    # be rejected because HS256 is not in the server's allowed algorithm
    # list, irrespective of what key material was used.
    import hashlib
    import hmac as hmac_mod
    import json

    from cryptography.hazmat.primitives import serialization

    public_pem = _PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    now = int(time.time())
    header = jwt.utils.base64url_encode(
        json.dumps({"alg": "HS256", "typ": "JWT", "kid": _KID}).encode()
    ).decode()
    payload = jwt.utils.base64url_encode(
        json.dumps(
            {"sub": "user-123", "aud": "authenticated", "iat": now, "exp": now + 3600}
        ).encode()
    ).decode()
    signing_input = f"{header}.{payload}".encode()
    signature = jwt.utils.base64url_encode(
        hmac_mod.new(public_pem, signing_input, hashlib.sha256).digest()
    ).decode()
    token = f"{header}.{payload}.{signature}"

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
