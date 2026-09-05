"""Database engine configuration.

Reads the connection string from the ``DATABASE_URL`` environment
variable so the same code works locally, in CI, and against a real
Supabase/Postgres instance. Falls back to a sensible local default.
"""

import os

DEFAULT_DATABASE_URL = "postgresql+psycopg://localhost/neuro_sprint"


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
