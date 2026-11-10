import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.workout_plan import WorkoutPlan


class PlannedExercise(Base):
    __tablename__ = "planned_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=func.gen_random_uuid()
    )

    workout_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_plans.id", ondelete="CASCADE"),
        nullable=False
    )

    exercise_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    number_of_sets: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    number_of_reps: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    exercise_order: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    workout_plan: Mapped["WorkoutPlan"] = relationship(
        back_populates="planned_exercises"
    )

    __table_args__ = (

        UniqueConstraint(
            "workout_plan_id",
            "exercise_order",
            name="uq_planned_exercises_workout_plan_id_exercise_order"
        ),

        CheckConstraint(
            "number_of_sets > 0",
            name="ch_planned_exercises_number_of_sets_positive"
        ),
        CheckConstraint(
            "number_of_reps > 0",
            name="ch_planned_exercises_number_of_reps_positive"
        ),
        CheckConstraint(
            "exercise_order > 0",
            name="ch_planned_exercises_exercise_order_positive"
        ),
    )
