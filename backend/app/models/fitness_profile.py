import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User

class FitnessProfile(Base):
    __tablename__ = "fitness_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key = True,
        nullable = False,
        server_default = func.gen_random_uuid()
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid = True),
        ForeignKey("users.id"),
        nullable = False,
        unique = True
    )

    fitness_goal: Mapped[str] = mapped_column(
        String(50),
        nullable = False
    )

    experience_level: Mapped[str] = mapped_column(
        String(30),
        nullable = False
    )

    days_per_week: Mapped[int] = mapped_column(
        SmallInteger,
        nullable = False
    )

    session_minutes: Mapped[int] = mapped_column(
        SmallInteger,
        nullable = False
    )

    equipment_available: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable = False,
        server_default = text("'[]'::jsonb")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates = "fitness_profile",
    )

    __table_args__ = (
    CheckConstraint(
        "days_per_week BETWEEN 1 AND 7",
        name = "ck_fitness_profiles_days_per_week"
    ),

    CheckConstraint(
        "session_minutes > 0",
        name = "ck_fitness_profiles_session_minutes"
    ),

    CheckConstraint(
        "jsonb_typeof(equipment_available) = 'array'",
        name = "ck_fitness_profiles_equipment_array"
    ),
)

    