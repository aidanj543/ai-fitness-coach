from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from app.core import security
from app.core.security import create_access_token


def test_get_my_profile_with_valid_access_token(client_and_session):
    client, _ = client_and_session
    email = "profile@example.com"

    registration = client.post(
        "/auth/register",
        json={"email": email, "password": "ExamplePassword123!"},
    )
    assert registration.status_code == 201
    user_id = registration.json()["id"]
    token = create_access_token(user_id)

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["email"] == email


def test_get_my_profile_without_authorization_header(client_and_session):
    client, _ = client_and_session

    response = client.get("/users/me")

    assert response.status_code == 401


def test_get_my_profile_with_invalid_token_signature(client_and_session):
    client, _ = client_and_session
    registration = client.post(
        "/auth/register",
        json={"email": "signature@example.com", "password": "ExamplePassword123!"},
    )
    assert registration.status_code == 201
    token = create_access_token(registration.json()["id"])
    header, payload, signature = token.split(".")
    replacement = "B" if signature[0] == "A" else "A"
    invalid_token = f"{header}.{payload}.{replacement}{signature[1:]}"

    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 401


def test_get_my_profile_with_expired_access_token(client_and_session, monkeypatch):
    client, _ = client_and_session
    registration = client.post(
        "/auth/register",
        json={"email": "expired@example.com", "password": "ExamplePassword123!"},
    )
    assert registration.status_code == 201
    monkeypatch.setattr(security, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    token = create_access_token(registration.json()["id"])

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_get_my_profile_with_refresh_token(client_and_session):
    client, _ = client_and_session
    registration = client.post(
        "/auth/register",
        json={"email": "refresh@example.com", "password": "ExamplePassword123!"},
    )
    assert registration.status_code == 201
    token = jwt.encode(
        {
            "sub": registration.json()["id"],
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "refresh",
        },
        security.JWT_SECRET_KEY,
        algorithm=security.JWT_ALGORITHM,
    )

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_get_my_profile_with_access_token_for_nonexistent_user(client_and_session):
    client, _ = client_and_session
    token = create_access_token(str(uuid4()))

    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_get_my_profile_with_unsupported_authentication_scheme(client_and_session):
    client, _ = client_and_session
    registration = client.post(
        "/auth/register",
        json={"email": "scheme@example.com", "password": "ExamplePassword123!"},
    )
    assert registration.status_code == 201
    token = create_access_token(registration.json()["id"])

    response = client.get("/users/me", headers={"Authorization": f"Basic {token}"})

    assert response.status_code == 401
