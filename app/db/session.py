"""Engine/session factory. SQLite is tuned for concurrent web workloads."""

from collections.abc import Iterator
from typing import Any

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine(url: str, echo: bool = False) -> Engine:
    kwargs: dict[str, Any] = {}
    is_sqlite = url.startswith("sqlite")
    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
    engine = create_engine(url, echo=echo, pool_pre_ping=True, **kwargs)

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_conn: Any, _: Any) -> None:
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")  # readers don't block the writer
            cur.execute("PRAGMA synchronous=NORMAL")  # safe with WAL, much faster
            cur.execute("PRAGMA foreign_keys=ON")  # SQLite disables FKs by default!
            cur.execute("PRAGMA busy_timeout=30000")
            cur.execute("PRAGMA cache_size=-64000")  # ~64 MB page cache
            cur.execute("PRAGMA temp_store=MEMORY")
            cur.close()

    return engine


_settings = get_settings()
engine = build_engine(_settings.database_url, _settings.db_echo)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency. Services commit explicitly; this only guarantees cleanup."""
    with SessionLocal() as session:
        yield session


def optimize_db() -> None:
    """Refresh SQLite query-planner statistics (cheap no-op when nothing changed).

    Without statistics SQLite can pick poor indexes on large tables, so this runs on
    startup/shutdown. Also run `ANALYZE` after any bulk import.
    """
    if engine.dialect.name == "sqlite":
        with engine.connect() as conn:
            conn.execute(text("PRAGMA optimize"))
