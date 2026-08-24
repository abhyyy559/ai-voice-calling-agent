"""GET /api/analytics/summary — counts, latency percentiles, 7-day histogram.

Rows are inserted directly through the ORM (the internal ingest API is
service-token scoped and covered elsewhere); the endpoint contract under test
is the org-scoped aggregation itself.
"""
from __future__ import annotations

from datetime import timedelta

from fastapi.testclient import TestClient

from app.timeutil import utcnow
from tests.conftest import auth_headers, register


def _seed_call(
    db,  # noqa: ANN001 - session factory
    org_id: int,
    *,
    status: str = "completed",
    kind: str = "phone",
    duration_seconds: float | None = 42.0,
    started_at=None,
    agent_version_id: int | None = None,
    e2e_values: list[float] | None = None,
    extracted_fields: int = 0,
):
    """Insert one Call (+transcript turns +extracted fields) directly."""
    from app.models import Call, ExtractedField, Transcript

    call = Call(
        org_id=org_id,
        kind=kind,
        status=status,
        duration_seconds=duration_seconds,
        started_at=started_at or utcnow(),
        agent_version_id=agent_version_id,
    )
    db.add(call)
    db.flush()
    for i, value in enumerate(e2e_values or []):
        db.add(
            Transcript(
                call_id=call.id,
                turn_index=i,
                speaker="agent" if i % 2 == 0 else "caller",
                text=f"turn {i}",
                e2e_ms=value,
            )
        )
    for i in range(extracted_fields):
        db.add(
            ExtractedField(
                call_id=call.id,
                field_name=f"field_{i}",
                field_value=f"value_{i}",
                confidence=0.9,
            )
        )
    return call


def test_summary_empty_org(client: TestClient) -> None:
    token, user = register(client, org_name="Empty Org")
    resp = client.get("/api/analytics/summary", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["total_calls"] == 0
    assert data["completed_calls"] == 0
    assert data["success_rate_pct"] == 0.0
    assert data["avg_e2e_ms"] is None
    assert data["p95_e2e_ms"] is None
    assert data["total_extracted_fields"] == 0
    assert data["recent_calls"] == []
    # zero-filled histogram, exactly seven UTC days ending today
    days = [d["date"] for d in data["calls_last_7d"]]
    assert len(days) == 7
    assert all(d["count"] == 0 for d in data["calls_last_7d"])
    today = utcnow().date().isoformat()
    assert days[-1] == today


def test_summary_counts_latency_and_fields(client: TestClient, session_factory) -> None:
    token, user = register(client, org_name="Metrics Org")
    org_id = user["org_id"]
    now = utcnow()

    with session_factory() as db:
        # e2e values -> median 1000.0, p95 (nearest-rank of 3) 1200.0, avg ~1000.0
        _seed_call(db, org_id, status="completed", e2e_values=[800.0, 1200.0], extracted_fields=3)
        _seed_call(
            db,
            org_id,
            status="completed",
            e2e_values=[1000.0],
            extracted_fields=1,
            started_at=now - timedelta(days=2),
        )
        _seed_call(db, org_id, status="failed", e2e_values=[9999.0])  # outlier only in avg/p95 pool? no: included
        _seed_call(db, org_id, status="no_answer", e2e_values=[], duration_seconds=None)
        _seed_call(db, org_id + 500, status="completed", e2e_values=[5000.0], extracted_fields=99)
        db.commit()

    resp = client.get("/api/analytics/summary", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # foreign-org call excluded everywhere
    assert data["total_calls"] == 4
    assert data["completed_calls"] == 2
    assert data["success_rate_pct"] == 50.0

    e2e = sorted([800.0, 1200.0, 1000.0, 9999.0])
    assert data["avg_e2e_ms"] == round(sum(e2e) / len(e2e), 1)
    assert data["median_e2e_ms"] == 1100.0
    assert data["p95_e2e_ms"] == 9999.0

    assert data["total_extracted_fields"] == 4  # 3 + 1; the 99 belong to the other org

    by_date = {d["date"]: d["count"] for d in data["calls_last_7d"]}
    today = utcnow().date().isoformat()
    two_days_ago = (utcnow() - timedelta(days=2)).date().isoformat()
    assert by_date[today] == 3  # calls 1, 3 and 4 started today
    assert by_date[two_days_ago] == 1
    assert sum(d["count"] for d in data["calls_last_7d"]) == 4  # every seeded call is within 7d

    recent_ids = [c["id"] for c in data["recent_calls"]]
    assert recent_ids == sorted(recent_ids, reverse=True)
    for item in data["recent_calls"]:
        assert {"id", "status", "duration_seconds", "started_at", "agent_name"} <= set(item)


def test_summary_resolves_agent_names_and_requires_auth(client: TestClient, session_factory) -> None:
    token, user = register(client, org_name="Named Org")
    org_id = user["org_id"]

    with session_factory() as db:
        from app.models import Agent, AgentVersion

        agent = Agent(org_id=org_id, name="Absentee Caller", description="")
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
        _seed_call(db, org_id, agent_version_id=version.id)
        db.commit()

    resp = client.get("/api/analytics/summary", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["recent_calls"]) == 1
    assert data["recent_calls"][0]["agent_name"] == "Absentee Caller"

    # bearer required
    assert client.get("/api/analytics/summary").status_code == 401
