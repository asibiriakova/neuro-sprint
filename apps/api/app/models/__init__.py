"""SQLAlchemy models for NeuroSprint's core schema (issue #2).

This module is the single source of truth for field/type/enum values
that other tasks should point to instead of re-deriving them. Keep it
updated if the schema changes.

Sprint (table: ``sprints``)
    id                              UUID, primary key
    user_id                         UUID, not null, owner.
                                     NOTE: plain UUID column, no FK yet.
                                     Issue #3 (Supabase auth.users) hasn't
                                     landed; wire this to
                                     ``auth.users.id`` once it does.
    start_date                      DATE, not null
    end_date                        DATE, not null
    integration_week_duration_days  INTEGER, not null, default 0.
                                     Number of days at the end of the
                                     sprint reserved as an "integration
                                     week" (see issue #28); 0 = none.
    integration_week_notes          TEXT, nullable. Free-text notes
                                     about the integration week.
    created_at                      TIMESTAMPTZ, not null, default now()

Task (table: ``tasks``)
    id            UUID, primary key
    sprint_id     UUID, not null, FK -> sprints.id, ON DELETE CASCADE
                  (deleting a Sprint deletes its Tasks).
    title         VARCHAR(255), not null
    pillar        ENUM ``pillar``, not null.
                  Values: foundation | drive | joy
    hour_estimate NUMERIC(5, 2), not null
    status        ENUM ``task_status``, not null.
                  Values: approved | complete
                  (deliberately only two — see issue #31 for why there
                  is no third, "in progress", status)
    external_id   VARCHAR(255), nullable. CalDAV event id, set once the
                  task is linked to an external calendar (issue #22).
    created_at    TIMESTAMPTZ, not null, default now()

StateLog (table: ``state_logs``)
    id         UUID, primary key
    sprint_id  UUID, not null, FK -> sprints.id, ON DELETE CASCADE
               (deleting a Sprint deletes its StateLogs).
    user_id    UUID, not null. Plain UUID column, no FK yet — same note
               as Sprint.user_id above.
    state      ENUM ``state``, not null.
               Values: apathy | passivity | relaxation | balance |
                       engagement | overarousal | panic
    note       TEXT, nullable.
    logged_at  DATE, not null. One row per (user_id, logged_at) — see
               issue #14 — enforced by a unique constraint
               (``uq_state_logs_user_id_logged_at``).

Cascade behavior
    Both FKs to ``sprints.id`` are declared ``ON DELETE CASCADE``:
    deleting a Sprint row deletes its Task and StateLog rows. This is
    explicit in the migration (see
    ``migrations/versions``) rather than left as the database default.
"""

from app.models.base import Base
from app.models.enums import Pillar, State, TaskStatus
from app.models.sprint import Sprint
from app.models.state_log import StateLog
from app.models.task import Task

__all__ = [
    "Base",
    "Pillar",
    "State",
    "TaskStatus",
    "Sprint",
    "StateLog",
    "Task",
]
