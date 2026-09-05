import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Sprint(Base):
    """A user's sprint (planning period).

    See ``app/models/__init__.py`` for the full field/type/enum reference.
    """

    __tablename__ = "sprints"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # NOTE: Plain UUID column, no FK yet. Issue #3 (Supabase auth.users)
    # hasn't landed. Once it does, wire this up as:
    #   ForeignKey("auth.users.id", ondelete="CASCADE")
    # (decision recorded in issue #2's constraints).
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Integration-week config (see issue #28): how many days at the end of
    # the sprint are set aside as an "integration week" (0 = none), plus
    # optional free-text notes about it.
    integration_week_duration_days: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    integration_week_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    tasks: Mapped[list["Task"]] = relationship(  # noqa: F821
        back_populates="sprint", cascade="all, delete-orphan", passive_deletes=True
    )
    state_logs: Mapped[list["StateLog"]] = relationship(  # noqa: F821
        back_populates="sprint", cascade="all, delete-orphan", passive_deletes=True
    )
