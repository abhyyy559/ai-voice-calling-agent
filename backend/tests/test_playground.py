"""Web playground tests (Lane A): LiveKit session issue + completion summary.

Contract §4:
- POST /api/playground/sessions {agent_version_id} -> {call_id, room_name,
  livekit_token, livekit_url}; creates a calls(kind='playground') row
- POST /api/playground/sessions/{call_id}/complete -> transcript + extracted
  fields + latency summary
"""
from __future__ import annotations

import json
from typing import Any

import jwt as pyjwt

from conftest import auth_headers, register
from test_agents import version_payload


def _make_agent_and_version(client: Any, token: str) -> dict[str, Any]:
    agent = client.post(
        "/api/agents",
        json={"name": "Playground Agent", "description": ""},
        headers=auth_headers(token),
    ).json()
    version = client.post(
        f"/api/agents/{agent['id']}/versions",
        json=version_payload(),
        headers=auth_headers(token),
    ).json()
    return {"agent": agent, "version": version}


def _create_session(client: Any, token: str, version_id: int) -> Any:
    return client.post(
        "/api/playground/sessions",
        json={"agent_version_id": version_id},
        headers=auth_headers(token),
    )


def test_create_session_issues_room_token_and_call_row(client, session_factory):
    from app.models import Call

    token, user = register(client)
    ids = _make_agent_and_version(client, token)

    resp = _create_session(client, token, ids["version"]["id"])
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert isinstance(body["call_id"], int)
    assert body["room_name"].startswith(f"playground-{user['org_id']}-")
    assert body["livekit_url"] == "ws://localhost:7880"

    # Token carries room join grant + our metadata for the voice-agent worker.
    claims = pyjwt.decode(
        body["livekit_token"], options={"verify_signature": False}
    )
    assert claims["video"]["room"] == body["room_name"]
    assert claims["video"]["roomJoin"] is True
    metadata = json.loads(claims["metadata"])
    assert metadata["version_id"] == ids["version"]["id"]
    assert metadata["call_id"] == body["call_id"]
    # TTL 1h (LiveKit sets nbf=issue time, no iat)
    assert 3500 <= claims["exp"] - claims["nbf"] <= 3600

    with session_factory() as db:
        call = db.get(Call, body["call_id"])
        assert call is not None
        assert call.kind == "playground"
        assert call.status == "in_progress"
        assert call.org_id == user["org_id"]
        assert call.agent_version_id == ids["version"]["id"]
        assert call.campaign_id is None


def test_session_for_foreign_agent_version_is_404(client):
    token_a, _ = register(client, org_name="Org A", email="a@example.test")
    token_b, _ = register(client, org_name="Org B", email="b@example.test")
    ids_a = _make_agent_and_version(client, token_a)

    foreign = _create_session(client, token_b, ids_a["version"]["id"])
    assert foreign.status_code == 404

    own = _create_session(client, token_a, ids_a["version"]["id"])
    assert own.status_code == 200


def test_unknown_version_is_404(client):
    token, _ = register(client)
    resp = _create_session(client, token, 999999)
    assert resp.status_code == 404


def test_sessions_require_bearer(client):
    assert client.post("/api/playground/sessions", json={"agent_version_id": 1}).status_code == 401


def test_session_without_livekit_credentials_is_503(session_factory):
    from fastapi.testclient import TestClient

    from app.main import create_app
    from conftest import make_settings

    fresh = create_app(make_settings(livekit_api_key="", livekit_api_secret=""))
    fresh.state.session_factory = session_factory
    with TestClient(fresh) as bare:
        token, _ = register(bare)
        ids = _make_agent_and_version(bare, token)
        resp = _create_session(bare, token, ids["version"]["id"])
        assert resp.status_code == 503
        assert "livekit" in resp.text.lower()


def _post_internal(path: str, body: dict[str, Any]) -> dict[str, str]:
    return {
        "X-Internal-Token": "test_internal_token",
        "Content-Type": "application/json",
    }


def test_complete_returns_transcript_fields_and_latency_summary(client, session_factory):
    from sqlalchemy import select
    from app.models import Call

    token, user = register(client)
    ids = _make_agent_and_version(client, token)
    session = _create_session(client, token, ids["version"]["id"]).json()
    call_id = session["call_id"]

    turns_body = {
        "turns": [
            {
                "turn_index": 0,
                "speaker": "agent",
                "text": "Hello, I am an AI assistant calling about the absence.",
                "stt_final_ms": 0,
                "llm_first_token_ms": 210,
                "tts_first_audio_ms": 180,
                "e2e_ms": 640,
            },
            {
                "turn_index": 1,
                "speaker": "caller",
                "text": "He had a fever.",
                "stt_final_ms": 420,
                "e2e_ms": 700,
            },
        ]
    }
    posted = client.post(
        f"/internal/calls/{call_id}/transcript-turns",
        json=turns_body,
        headers={"X-Internal-Token": "test_internal_token"},
    )
    assert posted.status_code == 200, posted.text
    assert posted.json()["added"] == 2

    fields_posted = client.post(
        f"/internal/calls/{call_id}/extracted-fields",
        json={
            "fields": [
                {
                    "name": "reason_for_absence",
                    "value": "fever",
                    "confidence": 0.92,
                    "source_turn_index": 1,
                }
            ]
        },
        headers={"X-Internal-Token": "test_internal_token"},
    )
    assert fields_posted.status_code == 200, fields_posted.text

    completed = client.post(
        f"/api/playground/sessions/{call_id}/complete",
        json={},
        headers=auth_headers(token),
    )
    assert completed.status_code == 200, completed.text
    summary = completed.json()
    assert [t["text"] for t in summary["transcript"]] == [
        "Hello, I am an AI assistant calling about the absence.",
        "He had a fever.",
    ]
    assert len(summary["extracted_fields"]) == 1
    field = summary["extracted_fields"][0]
    assert field["field_name"] == "reason_for_absence"
    assert field["field_value"] == "fever"
    assert field["confidence"] > 0.9
    assert summary["latency"]["e2e_ms"]["n"] == 2
    assert summary["status"] == "completed"

    with session_factory() as db:
        call = db.get(Call, call_id)
        assert call.status == "completed"
        assert call.ended_at is not None


def test_complete_of_foreign_call_is_404(client):
    token_a, _ = register(client, org_name="Org A", email="a@example.test")
    token_b, _ = register(client, org_name="Org B", email="b@example.test")
    ids_a = _make_agent_and_version(client, token_a)
    session = _create_session(client, token_a, ids_a["version"]["id"]).json()

    foreign = client.post(
        f"/api/playground/sessions/{session['call_id']}/complete",
        json={},
        headers=auth_headers(token_b),
    )
    assert foreign.status_code == 404


def test_internal_endpoints_reject_bad_tokens(client):
    token, _ = register(client)
    ids = _make_agent_and_version(client, token)
    session = _create_session(client, token, ids["version"]["id"]).json()
    call_id = session["call_id"]

    no_token = client.post(
        f"/internal/calls/{call_id}/transcript-turns", json={"turns": []}
    )
    assert no_token.status_code == 401

    wrong = client.post(
        f"/internal/calls/{call_id}/transcript-turns",
        json={"turns": []},
        headers={"X-Internal-Token": "wrong-token"},
    )
    assert wrong.status_code == 401

    bad_turn = client.post(
        f"/internal/calls/{call_id}/transcript-turns",
        json={"turns": [{"turn_index": "x", "speaker": "robot", "text": ""}]},
        headers={"X-Internal-Token": "test_internal_token"},
    )
    assert bad_turn.status_code == 400
