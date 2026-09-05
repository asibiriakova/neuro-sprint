"""FastAPI dependency for verifying Supabase-issued JWTs.

Frontend requests carry the Supabase access token as a standard
``Authorization: Bearer <token>`` header (this is what
``@supabase/ssr``'s session gives you client-side). This module verifies
that token on the backend without any custom auth/session system of its
own — no sessions are created or stored here.

Verification is JWKS-based: Supabase's newer "JWT Signing Keys" system
signs access tokens asymmetrically (this project uses ES256) and
publishes the corresponding public keys at
``${SUPABASE_URL}/auth/v1/.well-known/jwks.json``. We fetch that JWKS via
PyJWT's ``PyJWKClient`` (which does its own key caching) and verify each
token's signature against the matching public key — never against a
locally-held secret, so there's nothing here an attacker could brute
force or that we could leak.

Configuration is read from environment variables so the exact same code
works against a real Supabase project and against a mocked JWKS endpoint
in tests:

- ``SUPABASE_URL``: the project's base URL (e.g.
  ``https://xxxx.supabase.co``, the same value as apps/web's
  ``NEXT_PUBLIC_SUPABASE_URL``). Used to build the JWKS URL above.
  Required for ``GET /me`` and any other route behind
  ``get_current_user`` to work.
- ``SUPABASE_JWT_AUD``: the expected ``aud`` claim. Supabase issues
  ``"authenticated"`` for logged-in users by default; only override this
  if the project customizes it.

Only JWKS/asymmetric verification is implemented. This project's
Supabase instance has already migrated to JWT Signing Keys (ES256) — the
default for new projects — so a static-secret (HS256) fallback was left
out to keep this dependency simple; add one if a project genuinely still
needs legacy shared-secret support.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

# auto_error=False so we can control the response ourselves and always
# return 401 (never FastAPI's default 403) for missing credentials.
_bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing, invalid, or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)

# Algorithms we ever accept a signature under. Deliberately excludes
# "none" and any algorithm not explicitly listed here — passing this
# list to jwt.decode/PyJWKClient.get_signing_key_from_jwt is what
# prevents an alg-confusion attack (e.g. a token that claims alg=none,
# or claims HS256 and is "signed" with a public key as the secret) from
# ever being accepted, regardless of what the token's own header claims.
_ALLOWED_ALGORITHMS = ["ES256", "RS256"]


@dataclass(frozen=True)
class CurrentUser:
    """The caller identified by a verified Supabase access token."""

    id: str
    email: str | None


def _get_supabase_url() -> str:
    url = os.environ.get("SUPABASE_URL")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured on the server",
        )
    return url.rstrip("/")


def _get_audience() -> str:
    return os.environ.get("SUPABASE_JWT_AUD", "authenticated")


@lru_cache(maxsize=1)
def _get_jwk_client() -> PyJWKClient:
    """Build (once) and reuse the PyJWKClient for this process.

    PyJWKClient caches the fetched key set internally, but we also want
    to avoid rebuilding the client itself (and re-reading env vars) on
    every request. ``lru_cache`` keys on no arguments, so this only ever
    builds one client per ``SUPABASE_URL`` for the life of the process —
    tests that need a different URL/mock clear this cache explicitly
    (see ``app.auth._get_jwk_client.cache_clear()``).
    """
    jwks_url = f"{_get_supabase_url()}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """FastAPI dependency: verify the bearer token, or raise 401.

    Use as ``user: CurrentUser = Depends(get_current_user)`` on any route
    that should require a logged-in Supabase user.
    """
    if credentials is None or not credentials.credentials:
        raise _UNAUTHORIZED

    token = credentials.credentials

    try:
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=_ALLOWED_ALGORITHMS,
            audience=_get_audience(),
        )
    except jwt.PyJWTError:
        # Covers expired tokens, bad/mismatched signatures, malformed
        # tokens, audience mismatches, and alg-confusion attempts (an
        # unrecognized/disallowed "alg" header, e.g. "none", makes
        # get_signing_key_from_jwt itself raise) alike — all surface as
        # 401, never a 500.
        raise _UNAUTHORIZED
    except HTTPException:
        raise
    except Exception:
        # Any other failure fetching/parsing the JWKS (network error,
        # malformed key set, etc.) must still fail closed as 401 rather
        # than 500ing or passing the request through.
        raise _UNAUTHORIZED

    user_id = payload.get("sub")
    if not user_id:
        raise _UNAUTHORIZED

    return CurrentUser(id=user_id, email=payload.get("email"))
