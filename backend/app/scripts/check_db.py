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
            row = result.one()
            print("Test result:", row[0])
            print("Test result:", row[1])
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()