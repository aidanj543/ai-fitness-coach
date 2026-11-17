import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_password
from app.main import app
from app.models.user import User

@pytest.fixture
def client():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    test_url = os.getenv("TEST_DATABASE_URL")

    if not test_url:
        pytest.fail("TEST_DATABASE_URL must be configured")

    if make_url(test_url).database != "fitness_coach_test":
        pytest.fail("Refusing to test against a non-test database")

    engine = create_engine(test_url)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                session = Session(
                    bind=connection,
                    join_transaction_mode="create_savepoint",
                    expire_on_commit=False,
                )

                def override_get_db():
                    yield session

                app.dependency_overrides[get_db] = override_get_db

                with TestClient(app) as test_client:
                    yield test_client

            finally:
                app.dependency_overrides.pop(get_db, None)
                session.close()
                transaction.rollback()
    finally:
        engine.dispose()

def test_register_user_success(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newathlete@example.com",
            "password": "ExamplePassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "newathlete@example.com"
    assert "id" in data
    assert "created_at" in data

    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_registration(client):
    payload = {
        "email": "duplicateathlete@example.com",
        "password": "ExamplePassword123!",
    }

    first_response = client.post("/auth/register", json=payload)
    assert first_response.status_code == 201

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_email_normalization(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "  MixedCaseAthlete@Example.COM  ",
            "password": "ExamplePassword123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "mixedcaseathlete@example.com"

    duplicate_response = client.post(
        "/auth/register",
        json={
            "email": "mixedcaseathlete@example.com",
            "password": "ExamplePassword123!",
        },
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "Email already registered"}


def test_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": "ExamplePassword123!",
        },
    )

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "email"]
        for error in response.json()["detail"]
    )


def test_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "shortpasswordathlete@example.com",
            "password": "ShortPass1!",
        },
    )

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "password"]
        and error["type"] == "string_too_short"
        for error in response.json()["detail"]
    )


def test_password_stored_as_hash(client):
    password = "ExamplePassword123!"
    email = "hashedpasswordathlete@example.com"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )

    assert response.status_code == 201

    session = next(app.dependency_overrides[get_db]())
    user = session.scalars(select(User).where(User.email == email)).one()

    assert user.password_hash != password
    assert verify_password(password, user.password_hash)
