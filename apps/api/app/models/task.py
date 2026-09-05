import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import Pillar, TaskStatus


class Task(Base):
    """A task that belongs to a sprint.

    See ``app/models/__init__.py`` for the full field/type/enum reference.
    """

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sprint_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sprints.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    pillar: Mapped[Pillar] = mapped_column(
        PgEnum(
            Pillar,
            name="pillar",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )

    hour_estimate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    status: Mapped[TaskStatus] = mapped_column(
        PgEnum(
            TaskStatus,
            name="task_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )

    # Nullable: only set once the task is linked to a CalDAV event (issue #22).
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    sprint: Mapped["Sprint"] = relationship(back_populates="tasks")  # noqa: F821
