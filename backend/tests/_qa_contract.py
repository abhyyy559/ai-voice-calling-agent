"""Shared contract-test helpers for the Lane E backend suites.

Imports whatever FastAPI app Lane A has merged so far and binds an in-memory
SQLite session factory to it (never touches real Postgres). Every step fails
soft: callers get ``(value_or_None, reason)`` so suites can skip with an
informative message while lanes land concurrently.
"""
from __future__ import annotations

import importlib
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
BACKEND_DIR: Path = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

ABSENT_STUDENT_PATH: Path = PROJECT_ROOT / "domain-configs" / "absent-student.json"

AUTH_REGISTER: str = "/api/auth/register"
AUTH_LOGIN: str = "/api/auth/login"
DEFAULT_MEMBER_PASSWORD: str = "test-password-1"


def load_absent_student_config() -> dict[str, Any]:
    with ABSENT_STUDENT_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def build_version_payload(config: dict[str, Any]) -> dict[str, Any]:
    """Map a domain-config file onto the frozen AgentVersion payload shape."""
    disclosure = config.get("disclosure_script") or config.get("mandatory_disclosure") or ""
    return {
        "system_prompt": config.get("system_prompt", ""),
        "company_context": config.get("company_context", {}),
        "question_flow": config.get("question_flow", []),
        "extraction_schema": config.get("extraction_schema", {}),
        "disclosure_script": disclosure,
        "escalation_rules": config.get("escalation_rules", []),
        "voice_settings": config.get("voice_settings", {}),
    }


def import_first(candidates: list[tuple[str, str]]) -> tuple[Optional[Any], str]:
    """Try ``(module, attr)`` pairs in order; return the first hit or why all failed."""
    failures: list[str] = []
    for mod_name, attr in candidates:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as exc:
            failures.append(f"{mod_name}: {type(exc).__name__}: {exc}")
            continue
        obj = getattr(mod, attr, None)
        if obj is not None:
            return obj, ""
        failures.append(f"{mod_name}.{attr}: attribute missing")
    return None, "; ".join(failures)


def import_app() -> tuple[Optional[Any], str]:
    """Locate the merged FastAPI app or app factory, or explain why not."""
    app, reason = import_first(
        [
            ("main", "app"),
            ("main", "create_app"),
            ("app.main", "app"),
            ("app.main", "create_app"),
        ]
    )
    if app is None:
        return None, f"FastAPI app not importable yet ({reason})"
    if not hasattr(app, "routes") and callable(app):
        try:
            app = app()
        except TypeError as exc:
            return None, f"app factory requires arguments ({exc})"
    if not hasattr(app, "routes"):
        return None, "imported object is not an ASGI app"
    return app, ""


def build_test_client(app: Any) -> tuple[Optional[Any], str]:
    """Bind an in-memory SQLite session factory to ``app`` and wrap a TestClient."""
    try:
        from fastapi.testclient import TestClient
    except Exception as exc:
        return None, f"TestClient/httpx unavailable: {exc}"
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool
    except Exception as exc:
        return None, f"sqlalchemy unavailable: {exc}"

    base, base_reason = import_first(
        [("app.models", "Base"), ("models", "Base"), ("app.database", "Base")]
    )
    if base is None:
        return None, f"ORM Base not located ({base_reason})"

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        base.metadata.create_all(engine)
    except Exception as exc:
        return None, (
            "models not creatable on SQLite yet "
            f"({type(exc).__name__}: {exc}); Lane A conftest owns the canonical fixture"
        )
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    bound = False
    try:
        app.state.session_factory = factory
        bound = True
    except Exception:
        pass
    get_db, _gdb_reason = import_first([("app.database", "get_db"), ("database", "get_db")])
    if get_db is not None:
        def _override() -> Any:
            db = factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = _override
        bound = True
    if not bound:
        return None, "could not rebind sessions (neither app.state.session_factory nor get_db override)"

    return TestClient(app, raise_server_exceptions=False), ""


def api(
    client: Any,
    method: str,
    url: str,
    token: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    headers = dict(kwargs.pop("headers", {}) or {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return client.request(method, url, headers=headers, **kwargs)


def extract_token(payload: dict[str, Any]) -> Optional[str]:
    token = payload.get("token") or payload.get("access_token")
    return token if isinstance(token, str) and token else None


def register_org(
    client: Any,
    *,
    org_name: str,
    email: str,
    password: str = "test-password-1",
) -> tuple[Optional[dict[str, Any]], str]:
    resp = client.post(
        AUTH_REGISTER, json={"org_name": org_name, "email": email, "password": password}
    )
    if resp.status_code == 404:
        return None, "register route missing (auth router not merged yet)"
    if resp.status_code not in (200, 201):
        return None, f"register failed {resp.status_code}: {resp.text[:300]}"
    data = resp.json()
    token = extract_token(data if isinstance(data, dict) else {})
    if not token:
        return None, f"register response missing token: {str(data)[:300]}"
    return {
        "token": token,
        "user": data.get("user", {}) if isinstance(data, dict) else {},
        "email": email,
        "password": password,
        "org": (data.get("user", {}) or {}).get("org_id"),
    }, ""


def create_agent(client: Any, token: str, name: str) -> tuple[Optional[dict[str, Any]], str]:
    resp = api(client, "POST", "/api/agents", token=token,
               json={"name": name, "description": "qa contract test agent"})
    if resp.status_code == 404:
        return None, "/api/agents route missing (agents router not merged yet)"
    if resp.status_code not in (200, 201):
        return None, f"agent create failed {resp.status_code}: {resp.text[:300]}"
    return resp.json(), ""


def create_version(
    client: Any,
    token: str,
    agent_id: Any,
    overrides: Optional[dict[str, Any]] = None,
) -> tuple[Optional[dict[str, Any]], str]:
    payload = build_version_payload(load_absent_student_config())
    payload.update(overrides or {})
    resp = api(client, "POST", f"/api/agents/{agent_id}/versions", token=token, json=payload)
    if resp.status_code == 404:
        return None, f"POST /api/agents/{agent_id}/versions missing (router not merged yet)"
    if resp.status_code not in (200, 201):
        return None, f"version create failed {resp.status_code}: {resp.text[:400]}"
    return resp.json(), ""


_MEMBER_PATH_RE = re.compile(r"user|invite|member", re.IGNORECASE)


def provision_member(
    client: Any,
    owner: dict[str, Any],
) -> tuple[Optional[dict[str, Any]], str]:
    """Create a role=member user via a discovered invite-style endpoint, then log in."""
    try:
        spec_resp = client.get("/openapi.json")
        spec = spec_resp.json()
    except Exception as exc:
        return None, f"openapi unavailable ({exc})"
    paths = [
        path
        for path, ops in (spec.get("paths") or {}).items()
        if isinstance(ops, dict) and "post" in ops and _MEMBER_PATH_RE.search(path)
    ]
    member_email = f"member-{uuid.uuid4().hex[:8]}@example.com"
    for path in sorted(paths):
        resp = api(
            client,
            "POST",
            path,
            token=owner["token"],
            json={"email": member_email, "password": DEFAULT_MEMBER_PASSWORD, "role": "member"},
        )
        if resp.status_code not in (200, 201):
            continue
        login = client.post(
            AUTH_LOGIN, json={"email": member_email, "password": DEFAULT_MEMBER_PASSWORD}
        )
        token = extract_token(login.json()) if login.status_code in (200, 201) else None
        if token:
            return {"token": token, "user": {"role": "member", "email": member_email}}, ""
        return None, f"member created via {path} but login failed {login.status_code}"
    return None, (
        "no member-provisioning endpoint advertised in OpenAPI "
        f"(scanned POST paths matching {_MEMBER_PATH_RE.pattern}): cannot exercise role checks"
    )


def mint_token_without_org(subject: Any) -> tuple[Optional[str], str]:
    """Best-effort JWT carrying only a subject claim (no org context)."""
    for mod_name in ("app.auth", "auth", "app.deps", "deps", "app.security", "security"):
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for fname in ("create_access_token", "create_token", "_create_token"):
            fn = getattr(mod, fname, None)
            if not callable(fn):
                continue
            for arg in ({"sub": str(subject)}, str(subject)):
                try:
                    token = fn(arg)
                except TypeError:
                    continue
                except Exception:
                    break
                if isinstance(token, str) and token.count(".") == 2:
                    return token, ""
    try:
        import jwt
        from app.config import get_settings

        settings = get_settings()
        secret = next(
            (
                getattr(settings, name)
                for name in dir(settings)
                if "secret" in name.lower() and isinstance(getattr(settings, name), str)
                and getattr(settings, name)
            ),
            "",
        )
        if secret:
            import datetime as _dt

            token = jwt.encode(
                {
                    "sub": str(subject),
                    "exp": _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=1),
                },
                secret,
                algorithm="HS256",
            )
            return token, ""
    except Exception:
        pass
    return None, "no token issuer or signing secret discoverable"
