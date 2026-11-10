import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from app.models import Base


# Alembic configuration
config = context.config

# Load the backend/.env file
backend_dir = Path(__file__).resolve().parents[1]
load_dotenv(backend_dir / ".env")

# Read credentials from the environment
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )

# Configure Alembic logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Register all six SQLAlchemy tables
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate migration SQL without a database connection."""

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a PostgreSQL connection."""

    engine = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()