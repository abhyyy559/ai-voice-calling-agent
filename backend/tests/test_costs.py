"""GET /api/analytics/costs — org-scoped estimated spend (P1 cost dashboard).

Uses the module-level PRICING_USD_PER_MINUTE constants ('update per invoice')
over each org call's duration_seconds."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from app.models import Call, Organization
from app.routers import analytics as analytics_module
from conftest import auth_headers, register


def _seed_calls(db: Any, org_id: int) -> None:
    org = db.get(Organization, org_id)
    assert org is not None
    from app.timeutil import utcnow

    now = utcnow()
    last_month = (now.replace(day=1) - timedelta(days=1)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    rows = [
        Call(kind="phone", org_id=org_id, status="completed", started_at=now,
             ended_at=now, duration_seconds=120.0),
        Call(kind="playground", org_id=org_id, status="completed", started_at=now,
             ended_at=now, duration_seconds=60.0),
        # No duration yet (in-flight) -> contributes zero minutes.
        Call(kind="phone", org_id=org_id, status="in_progress", started_at=now),
        # Previous calendar month bucket.
        Call(kind="phone", org_id=org_id, status="completed", started_at=last_month,
             ended_at=last_month, duration_seconds=600.0),
    ]
    db.add_all(rows)
    db.commit()


def test_costs_endpoint_org_scoped(client, session_factory):
    token, user = register(client)
    other_token, _ = register(client, org_name="Other Org", email="other@example.test")

    with session_factory() as db:
        _seed_calls(db, user["org_id"])
        # Foreign-org call must not leak into the first org's numbers.
        from app.timeutil import utcnow

        now = utcnow()
        db.add(Call(kind="phone", org_id=user["org_id"] + 1000, status="completed",
                    started_at=now, ended_at=now, duration_seconds=3600.0))
        db.commit()

    resp = client.get("/api/analytics/costs", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # 120s + 60s + 600s = 13 minutes total.
    assert body["total_minutes"] == 13.0
    expected_usd = round(13.0 * sum(analytics_module.PRICING_USD_PER_MINUTE.values()), 4)
    assert body["est_cost_usd"] == expected_usd

    assert sorted(p["minutes"] for p in body["per_call"]) == [1.0, 2.0, 10.0]

    monthly = body["monthly"]
    assert len(monthly) == 2
    total_from_monthly = round(sum(m["minutes"] for m in monthly.values()), 1)
    assert total_from_monthly == 13.0

    # Tenancy: another org sees zero.
    resp_b = client.get("/api/analytics/costs", headers=auth_headers(other_token))
    body_b = resp_b.json()
    assert body_b["total_minutes"] == 0.0
    assert body_b["per_call"] == []


def test_costs_requires_auth(client):
    assert client.get("/api/analytics/costs").status_code == 401
