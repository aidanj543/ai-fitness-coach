import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workout_plan import WorkoutPlan

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=func.gen_random_uuid()
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable = False
    )

    workout_plan_id: Mapped[uuid.UUID | None ] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_plans.id", ondelete = "SET NULL"),
        nullable = True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default = text("'in_progress'")
    )

    user: Mapped["User"] = relationship(
        back_populates="workout_sessions"
    )

    workout_plan: Mapped["WorkoutPlan | None"] = relationship(
        back_populates="workout_sessions"
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'completed', 'abandoned')",
            name = "ck_workout_sessions_status"
        ),

        CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name = "ck_workout_sessions_timestamp_order",
        ),

        CheckConstraint(
            "(status = 'in_progress' AND ended_at IS NULL) OR "
            "(status IN ('completed', 'abandoned') AND ended_at IS NOT NULL)",
            name="ck_workout_sessions_status_ended_at",
        ),
    )