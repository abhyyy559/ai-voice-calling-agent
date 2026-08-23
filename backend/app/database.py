"""Database engine/session setup — SQLAlchemy 2.x, sync engine.

psycopg2 is imported lazily by SQLAlchemy on first connect, so the backend
(and tests) run fine on SQLite without psycopg2 installed locally.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import Request
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings


def create_db_engine(database_url: str) -> Engine:
    """Create a sync engine; applies SQLite-specific options when needed."""
    kwargs: dict = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **kwargs)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Session factory bound to the given engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(settings: Settings) -> tuple[Engine, sessionmaker[Session]]:
    """Build engine + session factory from settings."""
    engine = create_db_engine(settings.database_url)
    # Enforce FK constraints on SQLite too (off by default there).
    if settings.database_url.startswith("sqlite") and not settings.database_url.startswith("sqlite:///file:"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _record):  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    return engine, make_session_factory(engine)


def get_db(request: Request):
    """FastAPI dependency: yield a session from the app-bound factory.

    Tests rebind ``app.state.session_factory`` (or override this dependency).
    """
    factory: sessionmaker[Session] = request.app.state.session_factory
    db = factory()
    try:
        yield db
    finally:
        db.close()


def repo_relative(path: str) -> Path:
    """Resolve a path relative to the backend package's parent (repo root)."""
    return (Path(__file__).resolve().parent.parent / path).resolve()
