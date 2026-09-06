"""Dry-run personas: scripted callers behind the text-mode campaign dry-run."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from app.services.dry_run import PERSONA_ORDER, persona_reply, validate_persona
from conftest import auth_headers, register
from test_playground_text import chat, groq_client, script, tool_call  # noqa: F401  (pytest fixture import)


def _seed_campaign_with_contacts(session_factory, org_id, version_id):  # type: ignore[no-untyped-def]
    from app.models import Campaign, Contact

    with session_factory() as db:
        campaign = Campaign(name="Dry-run Seeds", org_id=org_id, agent_version_id=version_id, status="draft")
        db.add(campaign)
        db.flush()
        ids = []
        for name, phone, custom in [
            ("C1", "+919812345601", {"student_name": "Aarav", "parent_name": "Suresh"}),
            ("C2", "+919812345602", {"student_name": "Ananya", "parent_name": "Rajesh"}),
        ]:
            contact = Contact(campaign_id=campaign.id, name=name, phone=phone, status="pending_review", custom_fields=custom)
            db.add(contact)
            db.flush()
            ids.append(contact.id)
        db.commit()
        return campaign.id, ids


def test_persona_order_covers_five_behaviors() -> None:
    assert set(PERSONA_ORDER) == {"cooperative", "terse", "distracted", "refuses", "clueless"}


def test_cooperative_answers_from_script() -> None:
    reply = persona_reply("cooperative", "Why was Aarav absent?", 1, {"student_name": "Aarav"})
    assert reply
    assert "Aarav" not in reply  # caller answers; never parrots the agent's question


def test_refuses_ends_early() -> None:
    first = persona_reply("refuses", "Hello?", 0, {})
    assert first is not None and "not" in first.lower()
    assert persona_reply("refuses", "Why?", 5, {}) is None


def test_terse_is_short() -> None:
    reply = persona_reply("terse", "Why was Aarav absent?", 1, {})
    assert reply is not None and len(reply.split()) <= 3


def test_unknown_persona_rejected() -> None:
    with pytest.raises(ValueError):
        validate_persona("sarcastic")


def test_mask_phone() -> None:
    from app.services.dry_run import _mask_phone

    assert _mask_phone("+919812345601") == "+919****01"
    assert _mask_phone("123") == "****"


def test_dry_run_runs_contacts_and_records_fields(groq_client, session_factory):
    from test_agents import version_payload
    from test_playground import _make_agent_and_version
    from test_playground_text import chat, script, tool_call

    from app.models import Call

    client = groq_client
    token, user = register(client)
    ids = _make_agent_and_version(client, token)
    campaign_id, contact_ids = _seed_campaign_with_contacts(
        session_factory, user["org_id"], ids["version"]["id"]
    )

    # NB: after each end_call tool the round loop makes one more Groq call
    # before returning, so every end_call needs a trailing spare chat message.
    script(
        chat("Hello, disclosure line. Am I speaking with Suresh?"),
        tool_call("record_extracted_field", {"field_name": "reason_for_absence", "value": "fever", "confidence": 0.9}),
        chat("Thanks, noted the fever."),
        tool_call("end_call", {"summary": "fever; back Monday"}),
        chat("Noted, goodbye."),
        chat("Hello, disclosure line. Am I speaking with Suresh?"),
        tool_call("end_call", {"summary": "refused"}),
        chat("Understood, goodbye."),
    )
    resp = client.post(
        f"/api/playground/campaigns/{campaign_id}/dry-run",
        json={"persona": "cooperative"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    report = resp.json()
    assert report["contacts_run"] == 2
    first, second = report["results"]
    assert first["extracted_fields"] and first["extracted_fields"][0]["field_name"] == "reason_for_absence"
    assert first["phone"].endswith("01") and "****" in first["phone"]
    assert len(first["transcript"]) >= 2
    assert report["results"][1]["status"] == "completed"
    with session_factory() as db:
        rows = db.scalars(select(Call).where(Call.campaign_id == campaign_id)).all()
        assert rows and all(c.kind == "dry-run" for c in rows)


def test_dry_run_rejects_unknown_persona(groq_client, session_factory):
    from test_playground import _make_agent_and_version

    client = groq_client
    token, user = register(client)
    ids = _make_agent_and_version(client, token)
    campaign_id, _ = _seed_campaign_with_contacts(session_factory, user["org_id"], ids["version"]["id"])
    resp = client.post(
        f"/api/playground/campaigns/{campaign_id}/dry-run",
        json={"persona": "sarcastic"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422
