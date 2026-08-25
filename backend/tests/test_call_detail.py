"""GET /api/calls/{id} for PLAYGROUND calls (regression: campaign_id/contact_id NULL).

Playground calls carry no campaign/contact lineage; the detail endpoint used to
explode with ResponseValidationError (int_type on None) which surfaced in the
browser as a fake CORS failure.
"""

from __future__ import annotations

from typing import Any

from app.models import Call
from conftest import auth_headers, register


def _seed_playground_call(db: Any, org_id: int) -> int:
    call = Call(
        kind="playground",
        org_id=org_id,
        status="completed",
        duration_seconds=24.0,
        summary="test summary",
    )
    db.add(call)
    db.commit()
    return call.id


def test_call_detail_ok_for_playground_call(client, session_factory):
    token, user = register(client)
    with session_factory() as db:
        call_id = _seed_playground_call(db, user["org_id"])

    resp = client.get(f"/api/calls/{call_id}", headers=auth_headers(token))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == call_id
    assert body["campaign_id"] is None
    assert body["contact_id"] is None
    assert body["contact_name"] is None
