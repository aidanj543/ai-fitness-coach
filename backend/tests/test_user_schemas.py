import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_valid_registration_input():
    user = UserCreate(
        email="athlete@example.com",
        password="ExamplePassword123!",
    )

    assert user.email == "athlete@example.com"


def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="ExamplePassword123!",
        )