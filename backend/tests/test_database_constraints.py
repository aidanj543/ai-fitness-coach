import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def test_invalid_training_days_rejected():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        pytest.skip("Local PostgreSQL is not configured")

    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                # Create a temporary user for our test
                user_id = connection.execute(
                    text("""
                        INSERT INTO users (email, password_hash)
                        VALUES (:email, :password_hash)
                        RETURNING id
                    """),
                    {
                        "email": f"test-{uuid.uuid4()}@example.invalid",
                        "password_hash": "test-only-not-a-real-password-hash",
                    },
                ).scalar_one()

                # Attempt to insert an invalid profile.
                # SAVEPOINT isolates the expected SQL error.
                with pytest.raises(IntegrityError):
                    with connection.begin_nested():
                        connection.execute(
                            text("""
                                INSERT INTO fitness_profiles (
                                    user_id,
                                    fitness_goal,
                                    experience_level,
                                    days_per_week,
                                    session_minutes
                                )
                                VALUES (
                                    :user_id,
                                    'build_muscle',
                                    'beginner',
                                    9,
                                    45
                                )
                            """),
                            {"user_id": user_id},
                        )

            finally:
                # Don't leave any test records behind
                transaction.rollback()
    finally:
        engine.dispose()