import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.session import get_db
from app.main import app
from app.models.user import User

@pytest.fixture
def client_and_session():
    """
    Create an isolated PostgreSQL transaction for each test.

    The application may call session.commit(), but all changes
    are rolled back after the test finishes.
    """

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    test_url = os.getenv("TEST_DATABASE_URL")

    if not test_url:
        pytest.fail("TEST_DATABASE_URL must be configured")

    if make_url(test_url).database != "fitness_coach_test":
        pytest.fail(
            "Refusing to test against a non-test database"
        )

    engine = create_engine(test_url)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                with Session(
                    bind=connection,
                    join_transaction_mode="create_savepoint",
                    expire_on_commit=False,
                ) as session:

                    def override_get_db():
                        yield session

                    app.dependency_overrides[get_db] = (
                        override_get_db
                    )

                    with TestClient(app) as test_client:
                        yield test_client, session

            finally:
                app.dependency_overrides.pop(get_db, None)
                transaction.rollback()

    finally:
        engine.dispose()