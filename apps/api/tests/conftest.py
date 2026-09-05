import os

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Tests for the schema in this issue need a *real* Postgres instance
# (native enums + FK cascade behavior don't exist on sqlite). Point
# TEST_DATABASE_URL at a scratch database that already has the Alembic
# migration applied (see migrations/versions), e.g.:
#
#   createdb neuro_sprint_test
#   DATABASE_URL=postgresql+psycopg://localhost/neuro_sprint_test \
#       uv run alembic upgrade head
#   TEST_DATABASE_URL=postgresql+psycopg://localhost/neuro_sprint_test \
#       uv run pytest
#
# If no database is reachable, these tests are skipped (not failed) so
# `uv run pytest` still passes in environments without Postgres.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://localhost/neuro_sprint_test"
)


@pytest.fixture(scope="session")
def db_engine():
    engine = sa.create_engine(TEST_DATABASE_URL)
    try:
        with engine.connect() as conn:
            has_sprints = sa.inspect(conn).has_table("sprints")
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"no reachable Postgres at {TEST_DATABASE_URL}: {exc}")
    if not has_sprints:
        pytest.skip(
            f"{TEST_DATABASE_URL} has no 'sprints' table — "
            "run `alembic upgrade head` against it first"
        )
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """A session bound to a transaction that is rolled back after the test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
