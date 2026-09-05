import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import State


class StateLog(Base):
    """A user's self-reported nervous-system state for one local calendar day.

    See ``app/models/__init__.py`` for the full field/type/enum reference.
    """

    __tablename__ = "state_logs"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "logged_at", name="uq_state_logs_user_id_logged_at"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sprint_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sprints.id", ondelete="CASCADE"),
        nullable=False,
    )

    # NOTE: Plain UUID column, no FK yet — see the same note on Sprint.user_id.
    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)

    state: Mapped[State] = mapped_column(
        PgEnum(
            State,
            name="state",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Date (not datetime): one row per user per *local calendar day*
    # (see issue #14), enforced by the unique constraint above.
    logged_at: Mapped[date] = mapped_column(Date, nullable=False)

    sprint: Mapped["Sprint"] = relationship(back_populates="state_logs")  # noqa: F821
