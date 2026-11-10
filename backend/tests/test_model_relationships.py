from sqlalchemy import inspect

from app.models import User


def test_user_workout_sessions_is_collection():
    relationship = inspect(User).relationships["workout_sessions"]

    assert relationship.uselist is True