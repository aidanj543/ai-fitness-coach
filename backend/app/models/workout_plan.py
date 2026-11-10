import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.planned_exercise import PlannedExercise
    from app.models.workout_session import WorkoutSession


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    workout_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_ai_generated: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("false")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="workout_plans"
    )

    planned_exercises: Mapped[list["PlannedExercise"]] = relationship(
        back_populates="workout_plan"
    )

    workout_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="workout_plan"
    )