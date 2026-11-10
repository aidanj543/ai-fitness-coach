import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.fitness_profile import FitnessProfile
    from app.models.workout_plan import WorkoutPlan
    from app.models.workout_session import WorkoutSession


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key = True,
        server_default = func.gen_random_uuid()
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable = False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    fitness_profile: Mapped["FitnessProfile | None"] = relationship(
        back_populates = "user",
        uselist = False
    )

    workout_plans: Mapped[list["WorkoutPlan"]] = relationship(
        back_populates = "user"
    )

    workout_sessions: Mapped["WorkoutSession"] = relationship(
        back_populates="user"
    )