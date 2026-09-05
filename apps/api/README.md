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
3. Fill in `SUPABASE_JWT_SECRET` from Project Settings -> API -> JWT
   Settings -> "JWT Secret" in the Supabase dashboard.

Only HS256 shared-secret verification is implemented (`app/auth.py`),
matching Supabase's default signing method. If a project is switched to
asymmetric JWT signing keys (JWKS), `SUPABASE_JWT_SECRET` verification
will not work there and the verifier would need to fetch and use the
project's JWKS endpoint instead.

### What's tested vs. not

`tests/test_auth.py` signs its own JWTs with a throwaway HS256 secret
and points `SUPABASE_JWT_SECRET` at that same secret — this verifies the
verification logic (valid token accepted with correct id/email;
missing/malformed/expired/wrong-secret/wrong-audience tokens rejected
with 401), but does not exercise a real Supabase project's token
issuance, signing key rotation, or JWKS infrastructure. That can only be
verified end-to-end once a real Supabase project is wired up on both
`apps/web` and `apps/api`.
