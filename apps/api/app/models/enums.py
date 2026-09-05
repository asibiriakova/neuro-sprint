"""Enum values shared by the ORM models and the Alembic migration.

Keeping the Python enum members and their string values here means the
migration and the models can never drift from each other — both import
from this module. See ``app/models/__init__.py`` for the full schema
doc comment.
"""

import enum


class Pillar(str, enum.Enum):
    """`Task.pillar` — which of the three NeuroSprint pillars a task serves."""

    FOUNDATION = "foundation"
    DRIVE = "drive"
    JOY = "joy"


class TaskStatus(str, enum.Enum):
    """`Task.status` — deliberately only two values.

    See issue #31 for why there is no third ("in progress") status.
    """

    APPROVED = "approved"
    COMPLETE = "complete"


class State(str, enum.Enum):
    """`StateLog.state` — the user's self-reported nervous-system state."""

    APATHY = "apathy"
    PASSIVITY = "passivity"
    RELAXATION = "relaxation"
    BALANCE = "balance"
    ENGAGEMENT = "engagement"
    OVERAROUSAL = "overarousal"
    PANIC = "panic"
