# Task 5 Brief: test-call dispatch — agent_version_id + room_name

**Files:**
- Modify: `backend/app/schemas.py` (`TestCallRequest`, `TestCallOut` only)
- Modify: `backend/app/routers/test_call.py`
- Create test: `backend/tests/test_call_flow.py`

**Interfaces (locked):**
- `TestCallRequest`: adds `agent_version_id: Optional[int] = None`
- `TestCallOut`: adds required `room_name: str`
- Route becomes AUTHENTICATED (`user: User = Depends(get_current_user)`); response includes `room_name = f"{PHONE_ROOM_PREFIX}{call.id}"`; `calls.agent_version_id` persisted.

## Step 1: Failing tests — create `backend/tests/test_call_flow.py`

```python
"""/api/test-call resolves an agent version, stamps the call, returns room name."""
from typing import Any

import pytest

from app.models import Agent, AgentVersion, Call, DomainConfig
from conftest import auth_headers, make_settings, register  # adapt imports to conftest reality


def _seed_domain_and_agent(db: Any, org_id: int) -> int:
    dc = DomainConfig(name="absent-student", version="1", question_flow=[], extraction_schema={})
    db.add(dc)
    db.flush()
    agent = Agent(org_id=org_id, name="Phone Agent", description="", status="draft")
    db.add(agent)
    db.flush()
    owner_id = db.execute(
        __import__("sqlalchemy").text("SELECT id FROM users LIMIT 1")
    ).scalar()
    version = AgentVersion(
        agent_id=agent.id,
        version=1,
        system_prompt="You call parents about absences.",
        company_context={},
        question_flow=[{"question": "Why absent?"}],
        extraction_schema={"reason_for_absence": {"type": "string", "validation": "required"}},
        disclosure_script="Hello, this is an automated call.",
        escalation_rules=[],
        voice_settings={},
        created_by=owner_id,
    )
    db.add(version)
    db.commit()
    return version.id


class FakeTelephony:
    def place_call(self, to: str, call_id: int) -> str:
        return f"CAfake{call_id}"


@pytest.fixture()
def fake_telephony(monkeypatch):
    monkeypatch.setattr(
        "app.routers.test_call._get_telephony", lambda request: FakeTelephony()
    )


def _post(client, token, payload):
    return client.post("/api/test-call", headers=auth_headers(token), json=payload)


def test_requires_auth(client):
    assert client.post("/api/test-call", json={}).status_code == 401


def test_unknown_agent_version_422(client, session_factory):
    token, user = register(client)
    with session_factory() as db:
        _seed_domain_and_agent(db, user["org_id"])
    resp = _post(client, token, {"to": "+919391470646", "domain_config_id": 1,
                                 "agent_version_id": 99999})
    assert resp.status_code == 422


def test_happy_path_stamps_version_and_room(client, session_factory, fake_telephony):
    token, user = register(client)
    with session_factory() as db:
        version_id = _seed_domain_and_agent(db, user["org_id"])
    resp = _post(client, token, {"to": "+919391470646", "domain_config_id": 1,
                                 "agent_version_id": version_id})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["room_name"] == f"phone-{body['call_id']}"
    with session_factory() as db:
        call = db.get(Call, body["call_id"])
        assert call.agent_version_id == version_id


def test_latest_org_version_used_when_omitted(client, session_factory, fake_telephony):
    token, user = register(client)
    with session_factory() as db:
        version_id = _seed_domain_and_agent(db, user["org_id"])
    resp = _post(client, token, {"to": "+919391470646", "domain_config_id": 1})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    with session_factory() as db:
        call = db.get(Call, body["call_id"])
        assert call.agent_version_id == version_id
```

ADAPT to conftest reality first: read `backend/tests/conftest.py` for exact helper names (`register`, `auth_headers`, settings fixture style) and how OTHER router tests authenticate; mirror their pattern exactly. If `DomainConfig` requires more fields per its model, seed minimally-valid rows the same way existing tests do (see `tests/test_campaign_launch.py`).

## Step 2: Run → expect multiple FAILures (401s / missing room_name)

Run (workdir backend): `.venv\Scripts\python.exe -m pytest tests\test_call_flow.py -q`

## Step 3: Implement

`schemas.py`:

```python
class TestCallRequest(BaseModel):
    to: Optional[str] = None
    domain_config_id: int
    agent_version_id: Optional[int] = None  # phone leg: which agent version speaks


class TestCallOut(BaseModel):
    call_id: int
    provider_call_id: str
    status: str
    room_name: str
```

`routers/test_call.py` binding changes:
1. Imports: add `from app.deps import get_current_user`, `from app.models import AgentVersion, User`, `from app.services.twilio_bridge import PHONE_ROOM_PREFIX`.
2. Route signature gains `user: User = Depends(get_current_user)` and `response_model=TestCallOut` stays.
3. After the domain-config check block, insert version resolution:

```python
    if payload.agent_version_id is not None:
        version = db.get(AgentVersion, payload.agent_version_id)
        if version is None:
            raise HTTPException(status_code=422, detail="unknown agent_version_id")
    else:
        version = db.scalar(
            select(AgentVersion)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(Agent.org_id == user.org_id)
            .order_by(AgentVersion.id.desc())
            .limit(1)
        )
        if version is None:
            raise HTTPException(status_code=422, detail="no agent versions in org")
```

4. On the `call = Call(...)` construction add `agent_version_id=version.id`.
5. Success return becomes:

```python
    return {
        "call_id": call.id,
        "provider_call_id": sid,
        "status": call.status,
        "room_name": f"{PHONE_ROOM_PREFIX}{call.id}",
    }
```

6. If ANY pre-existing tests hit `/api/test-call` unauthenticated or assert old response shape, UPDATE them to the new authenticated contract (register + headers + room_name assertion). Search: grep "test-call" under backend/tests.

## Step 4: Verify

Full suite (workdir backend): `.venv\Scripts\python.exe -m pytest -q` → all green (92 baseline + new).

## Step 5: Report → `.superpowers/sdd/t5-report.md`; return status/files/one-line/concerns only.

## Global Constraints

PowerShell 5.1 · NO git commands · touch ONLY schemas.py, routers/test_call.py, tests/test_call_flow.py (+ minimal edits to existing tests broken by the auth change).
