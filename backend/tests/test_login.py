from app.core.security import decode_access_token


def test_login_success(client_and_session):
    client, session = client_and_session

    credentials = {
        "email": "loginathlete@example.com",
        "password": "ExamplePassword123!",
    }

    registration = client.post(
        "/auth/register",
        json=credentials,
    )

    assert registration.status_code == 201

    response = client.post(
        "/auth/login",
        json=credentials,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"]


def test_login_incorrect_password(client_and_session):
    client, _ = client_and_session
    email = "wrongpassword@example.com"

    registration = client.post(
        "/auth/register",
        json={"email": email, "password": "ExamplePassword123!"},
    )

    assert registration.status_code == 201

    response = client.post(
        "/auth/login",
        json={"email": email, "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_non_existent_user(client_and_session):
    client, _ = client_and_session

    response = client.post(
        "/auth/login",
        json={
            "email": "unregistered@example.com",
            "password": "ExamplePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_with_uppercase_email(client_and_session):
    client, _ = client_and_session
    credentials = {
        "email": "uppercase@example.com",
        "password": "ExamplePassword123!",
    }

    registration = client.post("/auth/register", json=credentials)
    assert registration.status_code == 201

    response = client.post(
        "/auth/login",
        json={**credentials, "email": credentials["email"].upper()},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_invalid_email_format(client_and_session):
    client, _ = client_and_session

    response = client.post(
        "/auth/login",
        json={"email": "invalid-email", "password": "ExamplePassword123!"},
    )

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [["body", "email"]]


def test_login_with_empty_password(client_and_session):
    client, _ = client_and_session

    response = client.post(
        "/auth/login",
        json={"email": "emptypassword@example.com", "password": ""},
    )

    assert response.status_code == 422
    assert [error["loc"] for error in response.json()["detail"]] == [["body", "password"]]


def test_login_response(client_and_session):
    client, _ = client_and_session
    credentials = {
        "email": "loginresponse@example.com",
        "password": "ExamplePassword123!",
    }

    registration = client.post("/auth/register", json=credentials)
    assert registration.status_code == 201

    response = client.post("/auth/login", json=credentials)
    assert response.status_code == 200

    data = response.json()
    assert set(data) == {"access_token", "token_type"}
    assert data["token_type"] == "bearer"
    assert decode_access_token(data["access_token"]) == registration.json()["id"]


def test_nonexistent_user_with_dummy_password(client_and_session):
    client, _ = client_and_session

    response = client.post(
        "/auth/login",
        json={
            "email": "missing-dummy-test@example.com",
            "password": "ThisIsADummyPasswordUsedForTimingOnly!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }
    assert response.headers["www-authenticate"] == "Bearer"