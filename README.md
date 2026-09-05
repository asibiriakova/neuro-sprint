# NeuroSprint

Personal execution app for 3-week goal sprints, built on the Neurointegration methodology. See [`_docs/plan.md`](_docs/plan.md) for the full spec and [`_docs/tasks.md`](_docs/tasks.md) / GitHub issues for the backlog.

## Repo layout

- `apps/web` — Next.js (TypeScript) frontend.
- `apps/api` — FastAPI (Python) backend.

Each service is independently installable, runnable, and testable — no root-level install step is required.

## apps/web (frontend)

Requires Node `24.17.0` (pinned in `apps/web/.nvmrc` — `nvm use` picks it up automatically).

```bash
cd apps/web
npm install           # install dependencies
npm run dev           # run locally at http://localhost:3000
npm test              # run the test suite
npm run lint          # ESLint — fails on any rule violation
npm run format:check  # Prettier — fails on any formatting violation
```

## apps/api (backend)

Requires Python `3.11` (pinned in `apps/api/.python-version`) and [uv](https://docs.astral.sh/uv/) as the package manager.

```bash
cd apps/api
uv sync                              # install dependencies into .venv
uv run uvicorn app.main:app --reload # run locally at http://localhost:8000
uv run pytest                        # run the test suite
uv run ruff check .                  # lint — fails on any rule violation
uv run black --check .               # format check — fails on any formatting violation
```

`GET /health` returns `{"status": "ok"}` once the server is running.
