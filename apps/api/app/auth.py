"""FastAPI dependency for verifying Supabase-issued JWTs.

Frontend requests carry the Supabase access token as a standard
``Authorization: Bearer <token>`` header (this is what
``@supabase/ssr``'s session gives you client-side). This module verifies
that token on the backend without any custom auth/session system of its
own — no sessions are created or stored here.

Configuration is read from environment variables so the exact same code
works against a real Supabase project and against a throwaway secret in
tests:

- ``SUPABASE_JWT_SECRET``: the project's JWT signing secret, used to
  verify the HS256 signature on access tokens. Find it in the Supabase
  dashboard under Project Settings -> API -> JWT Settings -> "JWT
  Secret" (the "legacy" shared-secret signing key; this is what
  Supabase issues access tokens with by default).
- ``SUPABASE_JWT_AUD``: the expected ``aud`` claim. Supabase issues
  ``"authenticated"`` for logged-in users by default; only override this
  if the project customizes it.

Only HS256 shared-secret verification is implemented. Supabase projects
that opt into asymmetric JWT signing keys (JWKS-based, e.g. ES256/RS256)
would need a JWKS-fetching verifier instead — see the note in
apps/api/README or .env.example.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# auto_error=False so we can control the response ourselves and always
# return 401 (never FastAPI's default 403) for missing credentials.
_bearer_scheme = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Missing, invalid, or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


@dataclass(frozen=True)
class CurrentUser:
    """The caller identified by a verified Supabase access token."""

    id: str
    email: str | None


def _get_jwt_secret() -> str:
    secret = os.environ.get("SUPABASE_JWT_SECRET")
    if not secret:
        # Misconfiguration, not a caller error — but we still must not
        # silently pass the request through, so fail closed.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured on the server",
        )
    return secret


def _get_audience() -> str:
    return os.environ.get("SUPABASE_JWT_AUD", "authenticated")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """FastAPI dependency: verify the bearer token, or raise 401.

    Use as ``user: CurrentUser = Depends(get_current_user)`` on any route
    that should require a logged-in Supabase user.
    """
    if credentials is None or not credentials.credentials:
        raise _UNAUTHORIZED

    secret = _get_jwt_secret()

    try:
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=["HS256"],
            audience=_get_audience(),
        )
    except jwt.PyJWTError:
        # Covers expired tokens, bad signatures, malformed tokens, and
        # audience mismatches alike — all surface as 401, never a 500.
        raise _UNAUTHORIZED

    user_id = payload.get("sub")
    if not user_id:
        raise _UNAUTHORIZED

    return CurrentUser(id=user_id, email=payload.get("email"))
