"""GET /api/calls — cross-campaign call history index (org-scoped)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.timeutil import utcnow
from tests.conftest import auth_headers, register
from tests.test_analytics import _seed_call


def _make_agent_version(db, org_id: int, name: str):
    from app.models import Agent, AgentVersion

    agent = Agent(org_id=org_id, name=name, description="")
    db.add(agent)
    db.flush()
    version = AgentVersion(
        agent_id=agent.id,
        version=1,
        system_prompt="x" * 12,
        disclosure_script="y" * 12,
    )
    db.add(version)
    db.flush()
    return version


def test_calls_index_org_scoped_with_agent_and_latency(client: TestClient, session_factory) -> None:
    token, user = register(client, org_name="History Org")
    other_token, other_user = register(client, org_name="Rival Org")
    org_id = user["org_id"]
    other_org_id = other_user["org_id"]

    with session_factory() as db:
        version = _make_agent_version(db, org_id, "Survey Bot")
        foreign_version = _make_agent_version(db, other_org_id, "Foreign Bot")
        _seed_call(db, org_id, status="completed", e2e_values=[600.0, 800.0], agent_version_id=version.id)
        _seed_call(db, org_id, status="failed", e2e_values=[], duration_seconds=None)
        _seed_call(
            db,
            other_org_id,
            status="completed",
            e2e_values=[100.0],
            agent_version_id=foreign_version.id,
        )
        db.commit()

    resp = client.get("/api/calls", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    rows = resp.json()

    assert len(rows) == 2  # foreign-org call excluded
    assert [r["id"] for r in rows] == sorted((r["id"] for r in rows), reverse=True)

    with_agent = next(r for r in rows if r["agent_name"] is not None)
    assert with_agent["agent_name"] == "Survey Bot"
    assert with_agent["avg_e2e_ms"] == 700.0
    assert {"id", "status", "kind", "duration_seconds", "started_at", "flagged_for_human"} <= set(with_agent)

    # filter by agent version
    filtered = client.get(
        f"/api/calls?agent_version_id={version.id}", headers=auth_headers(token)
    ).json()
    assert len(filtered) == 1 and filtered[0]["agent_name"] == "Survey Bot"

    # bearer required
    assert client.get("/api/calls").status_code == 401


def test_calls_index_empty_and_limit_cap(client: TestClient) -> None:
    token, _user = register(client, org_name="Quiet Org")
    resp = client.get("/api/calls?limit=9999", headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json() == []
