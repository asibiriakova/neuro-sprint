from fastapi import Depends, FastAPI

from app.auth import CurrentUser, get_current_user

app = FastAPI(title="NeuroSprint API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/me")
def me(user: CurrentUser = Depends(get_current_user)) -> dict[str, str | None]:
    """Return the caller's identity from their verified Supabase token."""
    return {"id": user.id, "email": user.email}
