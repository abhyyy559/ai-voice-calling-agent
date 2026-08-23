"""Shared pytest fixtures: hermetic in-memory SQLite app client.

Each test gets a fresh database (StaticPool keeps one shared in-memory
connection alive across sessions/threads) and a FastAPI app whose
``app.state.session_factory`` is pointed at it — the same seam production
uses (see ``app.database.get_db``).
"""
from __future__ import annotations

from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.main import create_app
from app.models import Base


def make_settings(**overrides: Any) -> Settings:
    """Test Settings: ignores any developer .env file on disk."""
    defaults: dict[str, Any] = {
        "database_url": "sqlite://",
        "jwt_secret": "test_jwt_secret",
        "jwt_expire_minutes": 60,
        "internal_api_token": "test_internal_token",
        "livekit_url": "ws://localhost:7880",
        "livekit_api_key": "devkey",
        "livekit_api_secret": "devsecret",
        "cors_origins": "http://localhost:3000,http://localhost:5173",
        "dialer_enabled": False,
        "_env_file": None,
    }
    defaults.update(overrides)
    return Settings(**defaults)


@pytest.fixture()
def db_engine() -> Iterator[Any]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def session_factory(db_engine: Any) -> sessionmaker[Session]:
    return sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def app(session_factory: sessionmaker[Session]):
    application = create_app(make_settings())
    application.state.session_factory = session_factory
    return application


@pytest.fixture()
def client(app) -> Iterator[TestClient]:
    with TestClient(app) as test_client:  # runs startup/shutdown handlers
        yield test_client


# --- helpers used by test modules ------------------------------------------


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register(
    client: TestClient,
    org_name: str = "Acme University",
    email: str | None = None,
    password: str = "password123",
) -> tuple[str, dict[str, Any]]:
    """Register a fresh org+owner; returns (token, user_dict)."""
    if email is None:
        email = f"{org_name.lower().replace(' ', '-').replace('.', '')}@example.test"
    resp = client.post(
        "/api/auth/register",
        json={"org_name": org_name, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    return data["token"], data["user"]
