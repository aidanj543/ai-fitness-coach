import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func, text, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.workout_session import WorkoutSession


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"


    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    workout_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workout_sessions.id", ondelete="CASCADE"),
        nullable = False
    )

    exercise_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    exercise_order: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    set_number: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    reps_completed: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False
    )

    weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(6,2),
        nullable=True
    )

    workout_session: Mapped["WorkoutSession"] = relationship(
        back_populates="exercise_logs"
    )

    __table_args__ = (

        UniqueConstraint(
            "workout_session_id",
            "exercise_order",
            "set_number",
            name = "uq_exercise_logs_session_exercise_set"
        ),


        CheckConstraint(
            "exercise_order > 0",
            name = "ck_exercise_order_positive"
        ),

        CheckConstraint(
            "set_number > 0",
            name = "ck_set_number_positive"
        ),

        CheckConstraint(
            "reps_completed >=0",
            name = "ck_reps_completed_greater_or_zero"
        ),

        CheckConstraint(
            "weight_kg >= 0",
            name = "ck_weight_kg_positive"
        )
    )
