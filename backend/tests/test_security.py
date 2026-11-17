from app.core.security import (
    hash_password,
    verify_password,
)


def test_password_is_hashed():
    password = "ExamplePassword123!"

    hashed = hash_password(password)

    assert hashed != password


def test_correct_password_verifies():
    password = "ExamplePassword123!"

    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_wrong_password():
    hashed = hash_password("ExamplePassword123!")

    assert verify_password("WrongPassword123!", hashed) is False

