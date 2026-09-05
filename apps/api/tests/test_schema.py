"""Tests for issue #2: Sprint / Task / StateLog schema.

These exercise the real migrated Postgres schema (native enums, FK
cascade, unique constraint) via the SQLAlchemy models — see conftest.py
for how to point them at a database.
"""

import uuid
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from app.models import Pillar, Sprint, State, StateLog, Task, TaskStatus


def make_sprint(**overrides) -> Sprint:
    defaults = dict(
        user_id=uuid.uuid4(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 14),
    )
    defaults.update(overrides)
    return Sprint(**defaults)


def test_migration_created_expected_tables_and_columns(db_engine):
    inspector = sa.inspect(db_engine)
    assert set(inspector.get_table_names()) >= {"sprints", "tasks", "state_logs"}

    sprint_columns = {c["name"] for c in inspector.get_columns("sprints")}
    assert sprint_columns == {
        "id",
        "user_id",
        "start_date",
        "end_date",
        "integration_week_duration_days",
        "integration_week_notes",
        "created_at",
    }

    task_columns = {c["name"] for c in inspector.get_columns("tasks")}
    assert task_columns == {
        "id",
        "sprint_id",
        "title",
        "pillar",
        "hour_estimate",
        "status",
        "external_id",
        "created_at",
    }

    state_log_columns = {c["name"] for c in inspector.get_columns("state_logs")}
    assert state_log_columns == {
        "id",
        "sprint_id",
        "user_id",
        "state",
        "note",
        "logged_at",
    }


def test_migration_created_fk_cascade_and_unique_constraint(db_engine):
    inspector = sa.inspect(db_engine)

    task_fks = inspector.get_foreign_keys("tasks")
    assert len(task_fks) == 1
    assert task_fks[0]["referred_table"] == "sprints"
    assert task_fks[0]["options"].get("ondelete") == "CASCADE"

    state_log_fks = inspector.get_foreign_keys("state_logs")
    assert len(state_log_fks) == 1
    assert state_log_fks[0]["referred_table"] == "sprints"
    assert state_log_fks[0]["options"].get("ondelete") == "CASCADE"

    unique_constraints = inspector.get_unique_constraints("state_logs")
    assert any(
        set(uc["column_names"]) == {"user_id", "logged_at"}
        for uc in unique_constraints
    )


def test_sprint_task_state_log_can_be_created(db_session):
    sprint = make_sprint(integration_week_duration_days=3, integration_week_notes="rest")
    task = Task(
        sprint=sprint,
        title="Write acceptance criteria",
        pillar=Pillar.FOUNDATION,
        hour_estimate=Decimal("2.5"),
        status=TaskStatus.APPROVED,
    )
    state_log = StateLog(
        sprint=sprint,
        user_id=sprint.user_id,
        state=State.BALANCE,
        logged_at=date(2026, 1, 2),
    )
    db_session.add_all([sprint, task, state_log])
    db_session.commit()

    db_session.refresh(sprint)
    db_session.refresh(task)
    db_session.refresh(state_log)

    assert sprint.id is not None
    assert sprint.created_at is not None
    assert sprint.integration_week_duration_days == 3
    assert task.sprint_id == sprint.id
    assert task.pillar == Pillar.FOUNDATION
    assert task.status == TaskStatus.APPROVED
    assert task.external_id is None
    assert state_log.sprint_id == sprint.id
    assert state_log.state == State.BALANCE
    assert state_log.note is None


def test_sprint_defaults_integration_week_duration_to_zero(db_session):
    sprint = make_sprint()
    db_session.add(sprint)
    db_session.commit()
    db_session.refresh(sprint)

    assert sprint.integration_week_duration_days == 0
    assert sprint.integration_week_notes is None


def test_deleting_sprint_cascades_to_tasks_and_state_logs(db_session):
    sprint = make_sprint()
    task = Task(
        sprint=sprint,
        title="Cascade me",
        pillar=Pillar.DRIVE,
        hour_estimate=Decimal("1.0"),
        status=TaskStatus.APPROVED,
    )
    state_log = StateLog(
        sprint=sprint,
        user_id=sprint.user_id,
        state=State.ENGAGEMENT,
        logged_at=date(2026, 1, 3),
    )
    db_session.add_all([sprint, task, state_log])
    db_session.commit()

    sprint_id = sprint.id
    db_session.delete(sprint)
    db_session.commit()

    remaining_tasks = db_session.scalars(
        sa.select(Task).where(Task.sprint_id == sprint_id)
    ).all()
    remaining_state_logs = db_session.scalars(
        sa.select(StateLog).where(StateLog.sprint_id == sprint_id)
    ).all()
    assert remaining_tasks == []
    assert remaining_state_logs == []


def test_state_log_enforces_one_row_per_user_per_day(db_session):
    sprint = make_sprint()
    db_session.add(sprint)
    db_session.flush()

    same_day = date(2026, 1, 5)
    db_session.add(
        StateLog(
            sprint=sprint,
            user_id=sprint.user_id,
            state=State.PANIC,
            logged_at=same_day,
        )
    )
    db_session.flush()

    db_session.add(
        StateLog(
            sprint=sprint,
            user_id=sprint.user_id,
            state=State.RELAXATION,
            logged_at=same_day,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_task_status_enum_rejects_values_outside_approved_or_complete(db_session):
    sprint = make_sprint()
    db_session.add(sprint)
    db_session.flush()

    with pytest.raises(Exception):
        db_session.execute(
            sa.text(
                "INSERT INTO tasks "
                "(id, sprint_id, title, pillar, hour_estimate, status) "
                "VALUES (:id, :sprint_id, 'bad', 'foundation', "
                "1.0, 'in_progress')"
            ),
            {"id": uuid.uuid4(), "sprint_id": sprint.id},
        )
        db_session.flush()
    db_session.rollback()
