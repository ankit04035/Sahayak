"""
Database Foundation Module.
Manages SQLAlchemy engine, session factory, base model class,
session dependency, database initialization, and connectivity verification.
"""

from pathlib import Path
from typing import Generator, Optional, Tuple
from sqlalchemy import create_engine, text, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.app.config import get_settings

settings = get_settings()

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if ":///" in settings.DATABASE_URL:
        db_path_part = settings.DATABASE_URL.split(":///", 1)[1]
        if db_path_part and not db_path_part.startswith(":memory:"):
            db_path = Path(db_path_part)
            db_path.parent.mkdir(parents=True, exist_ok=True)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite connections."""
    if "sqlite" not in str(type(dbapi_connection)).lower():
        return
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    finally:
        cursor.close()


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def _ensure_user_password_hash_column(target_engine: Optional[Engine] = None) -> None:
    """Backfill legacy SQLite databases with the password_hash column required for auth."""
    eng = target_engine or engine
    if not str(eng.url).startswith("sqlite"):
        return

    inspector = inspect(eng)
    if "users" not in inspector.get_table_names():
        return

    columns = [col["name"] for col in inspector.get_columns("users")]
    if "password_hash" in columns:
        return

    with eng.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''"))


def init_db(target_engine: Optional[Engine] = None) -> None:
    """
    Initialize all database tables defined in the metadata.
    Idempotent: does not drop or recreate existing tables.
    """
    import backend.app.models  # noqa: F401
    eng = target_engine or engine
    Base.metadata.create_all(bind=eng)
    _ensure_user_password_hash_column(target_engine=eng)


def get_db() -> Generator[Session, None, None]:
    """Dependency providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Tuple[bool, str]:
    """
    Verify database connectivity without assuming any schema/table existence.
    Returns (is_connected, message).
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "ok"
    except Exception as exc:
        return False, str(exc)
