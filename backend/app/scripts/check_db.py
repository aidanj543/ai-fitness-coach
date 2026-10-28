import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def main():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    engine = create_engine(database_url, pool_pre_ping=True)

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_user, current_database()"))
            print("Database connection successful!")
            print("Test result:", result.scalar_one())
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()