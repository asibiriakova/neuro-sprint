"""create sprints, tasks, state_logs

See app/models/__init__.py for the full field/type/enum reference this
migration implements.

Revision ID: 545385b2a734
Revises:
Create Date: 2026-09-05 22:42:11.323541

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "545385b2a734"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Native Postgres enum types, created/dropped explicitly (create_type=False
# on the columns below) so upgrade/downgrade behavior is fully explicit
# rather than relying on SQLAlchemy's implicit create-on-table-create.
pillar_enum = postgresql.ENUM(
    "foundation", "drive", "joy", name="pillar", create_type=False
)
task_status_enum = postgresql.ENUM(
    "approved", "complete", name="task_status", create_type=False
)
state_enum = postgresql.ENUM(
    "apathy",
    "passivity",
    "relaxation",
    "balance",
    "engagement",
    "overarousal",
    "panic",
    name="state",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    pillar_enum.create(bind, checkfirst=True)
    task_status_enum.create(bind, checkfirst=True)
    state_enum.create(bind, checkfirst=True)

    op.create_table(
        "sprints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        # Plain UUID, no FK yet: issue #3 (Supabase auth.users) hasn't
        # landed. Wire this to auth.users.id (ON DELETE CASCADE) once it
        # does — see issue #2's constraints.
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "integration_week_duration_days",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("integration_week_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "sprint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sprints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("pillar", pillar_enum, nullable=False),
        sa.Column("hour_estimate", sa.Numeric(5, 2), nullable=False),
        sa.Column("status", task_status_enum, nullable=False),
        # Nullable: only set once linked to a CalDAV event (issue #22).
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "state_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "sprint_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sprints.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # Plain UUID, no FK yet — same note as sprints.user_id above.
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("state", state_enum, nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        # One row per user per local calendar day (issue #14), enforced
        # below by a unique constraint on (user_id, logged_at).
        sa.Column("logged_at", sa.Date(), nullable=False),
        sa.UniqueConstraint(
            "user_id", "logged_at", name="uq_state_logs_user_id_logged_at"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("state_logs")
    op.drop_table("tasks")
    op.drop_table("sprints")

    bind = op.get_bind()
    state_enum.drop(bind, checkfirst=True)
    task_status_enum.drop(bind, checkfirst=True)
    pillar_enum.drop(bind, checkfirst=True)
