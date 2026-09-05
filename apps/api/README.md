# NeuroSprint API

FastAPI backend. See the repo root `AGENTS.md` for common commands
(`uv sync`, `uv run pytest`).

## Auth setup (Supabase)

`GET /me` (and any future route using `app.auth.get_current_user`)
verifies the caller's Supabase-issued JWT — no custom auth/session
system. This repo does not include real Supabase credentials; you need
to provide your own:

1. Create a project at [supabase.com/dashboard](https://supabase.com/dashboard)
   (the same one `apps/web` is configured against).
2. Copy `.env.example` to `.env` (or export the vars another way).
3. Fill in `SUPABASE_URL` with your project's URL, e.g.
   `https://xxxx.supabase.co` — find it in Project Settings -> API ->
   Project URL (it's the same value as `apps/web`'s
   `NEXT_PUBLIC_SUPABASE_URL`).

Verification is JWKS-based (`app/auth.py`): tokens are verified against
the project's public signing keys, fetched from
`${SUPABASE_URL}/auth/v1/.well-known/jwks.json` via PyJWT's
`PyJWKClient`, which handles its own key caching. This matches Supabase's
current default signing method (asymmetric "JWT Signing Keys", ES256) —
no shared secret is used or stored by this app. Only `ES256`/`RS256`
signatures are ever accepted; anything else (including an `alg=none`
token) is rejected regardless of what the token's own header claims.

A project still on the older shared-secret (HS256 "Legacy JWT Secret")
signing method is not supported by this dependency — it would need a
separate HS256 verifier added, since a static secret can't be mixed into
JWKS-based verification. Check Project Settings -> API -> JWT Settings
to see which signing method your project uses.

### What's tested vs. not

`tests/test_auth.py` generates its own ES256 (EC/P-256) keypair, signs
test JWTs with the private key, and serves the corresponding public key
back to the app's `PyJWKClient` via a stubbed JWKS fetch (no real
network call) — this exercises the real JWKS-parsing and ES256
signature-verification code paths, not a re-implementation of them.
Covered: valid token accepted with correct id/email;
missing/malformed/expired tokens; a token signed with the wrong key;
an unknown `kid`; wrong audience; missing `sub`; wrong auth scheme; and
alg-confusion attempts (`alg=none`, and an HS256-signed token using the
ES256 public key as an HMAC secret) — all rejected with 401. Not
exercised: a real Supabase project's token issuance or signing-key
rotation, which can only be verified end-to-end against a live project.
