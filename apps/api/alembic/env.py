import logging
from logging.config import fileConfig
from urllib.parse import urlparse

from sqlalchemy import create_engine, pool

from alembic import context

from app.core.config import get_settings
from app.core.database import Base
from app.models import *  # noqa: F401,F403 — ensure all models are registered

logger = logging.getLogger("alembic.env")

config = context.config

settings = get_settings()


def get_sync_database_url() -> str:
    url = settings.DATABASE_URL_SYNC
    if not url:
        url = settings.DATABASE_URL
    if not url:
        url = config.get_main_option("sqlalchemy.url") or ""

    # Normalize scheme to standard postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    elif url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://", 1)

    return url


sync_db_url = get_sync_database_url()
if sync_db_url:
    config.set_main_option(
        "sqlalchemy.url", sync_db_url.replace("%", "%%")
    )

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_database_url() or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_sync_database_url()

    # Redact password for safe logging
    try:
        parsed = urlparse(url)
        safe_url = (
            f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
            if parsed.password
            else url
        )
        logger.info(f"Connecting to database for migrations: {safe_url}")
    except Exception:
        pass

    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    except Exception as exc:
        logger.error(f"Failed to execute Alembic migrations: {exc}")
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

