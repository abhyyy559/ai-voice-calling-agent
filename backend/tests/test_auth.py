"""Auth & tenancy tests (Lane A).

Covers: register/login/me, token validation, and the KEY tenancy guarantee —
a user from org B must receive 404 (not 403) when touching org A's entities,
so the existence of foreign resources never leaks.
"""
from __future__ import annotations

from conftest import auth_headers, register


# --- registration / login -----------------------------------------------------


def test_register_returns_token_and_owner_user(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "org_name": "Acme University",
            "email": "owner@acme.test",
            "password": "supersecret1",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["token"]
    assert data["user"]["email"] == "owner@acme.test"
    assert data["user"]["role"] == "owner"
    assert data["user"]["org_id"]


def test_login_and_me_roundtrip(client):
    _, user = register(client, email="me@example.test")
    resp = client.post(
        "/api/auth/login",
        json={"email": "me@example.test", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    me = client.get("/api/auth/me", headers=auth_headers(token))
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "me@example.test"
    assert me.json()["org_id"] == user["org_id"]
    assert me.json()["role"] == "owner"


def test_login_unknown_email_rejected(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.test", "password": "whatever123"},
    )
    assert resp.status_code == 401


def test_login_wrong_password_rejected(client):
    register(client, email="me@example.test")
    resp = client.post(
        "/api/auth/login",
        json={"email": "me@example.test", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_duplicate_email_rejected(client):
    register(client, email="dupe@example.test")
    resp = client.post(
        "/api/auth/register",
        json={
            "org_name": "Another Org",
            "email": "dupe@example.test",
            "password": "supersecret1",
        },
    )
    assert resp.status_code == 409


def test_short_password_rejected(client):
    resp = client.post(
        "/api/auth/register",
        json={"org_name": "X Org", "email": "x@example.test", "password": "short"},
    )
    assert resp.status_code == 422


# --- tenancy of pre-existing routes (contract �4: "now org-scoped") ----------


def test_cross_org_campaign_access_returns_404(client, session_factory):
    """Org B must not see org A's campaigns either (404, never 403/200)."""
    from app.models import DomainConfig

    with session_factory() as db:
        db.add(DomainConfig(name="absent-student", display_name="Absent Student"))
        db.commit()

    token_a, _ = register(client, org_name="Org A", email="a@example.test")
    token_b, _ = register(client, org_name="Org B", email="b@example.test")

    created = client.post(
        "/api/campaigns",
        json={"name": "Aug follow-ups", "domain_config_id": 1},
        headers=auth_headers(token_a),
    )
    assert created.status_code == 201, created.text

    own = client.get("/api/campaigns/1", headers=auth_headers(token_a))
    assert own.status_code == 200
    foreign = client.get("/api/campaigns/1", headers=auth_headers(token_b))
    assert foreign.status_code == 404, (
        f"cross-org campaign access must be 404, got {foreign.status_code}"
    )
    listed = client.get("/api/campaigns", headers=auth_headers(token_b))
    assert listed.json() == [], "org B listing must be empty"


def test_campaign_routes_require_bearer(client):
    assert client.get("/api/campaigns").status_code == 401


def test_campaign_create_accepts_agent_version_id(client):
    token, user = register(client)
    from test_agents import version_payload

    agent = client.post(
        "/api/agents",
        json={"name": "Campaign Agent", "description": ""},
        headers=auth_headers(token),
    ).json()
    version = client.post(
        f"/api/agents/{agent['id']}/versions",
        json=version_payload(),
        headers=auth_headers(token),
    ).json()

    created = client.post(
        "/api/campaigns",
        json={"name": "Pinned campaign", "agent_version_id": version["id"]},
        headers=auth_headers(token),
    )
    assert created.status_code == 201, created.text
    assert created.json()["agent_version_id"] == version["id"]
    assert created.json()["org_id"] == user["org_id"]


def test_foreign_agent_version_campaign_rejected(client):
    token_a, _ = register(client, org_name="Org A", email="a@example.test")
    token_b, _ = register(client, org_name="Org B", email="b@example.test")
    from test_agents import version_payload

    agent = client.post(
        "/api/agents",
        json={"name": "A agent", "description": ""},
        headers=auth_headers(token_a),
    ).json()
    version = client.post(
        f"/api/agents/{agent['id']}/versions",
        json=version_payload(),
        headers=auth_headers(token_a),
    ).json()

    resp = client.post(
        "/api/campaigns",
        json={"name": "steal", "agent_version_id": version["id"]},
        headers=auth_headers(token_b),
    )
    assert resp.status_code == 404, resp.text


def test_cross_org_call_detail_is_404(client, session_factory):
    """calls.org_id / campaign lineage must gate call detail too."""
    from app.models import Call, Campaign, Contact, DomainConfig

    with session_factory() as db:
        db.add(DomainConfig(name="absent-student", display_name="Absent Student"))
        campaign = Campaign(name="A campaign", org_id=1, domain_config_id=1, status="draft")
        db.add(campaign)
        db.flush()
        contact = Contact(campaign_id=campaign.id, phone="+911234567890", status="queued")
        db.add(contact)
        db.flush()
        from app.models import Call

        call = Call(
            campaign_id=campaign.id,
            contact_id=contact.id,
            kind="phone",
            org_id=campaign.org_id,
            status="in_progress",
            started_at=None,
        )
        db.add(call)
        db.commit()
        call_id = call.id

    register(client, org_name="Org A", email="a@example.test")  # org id 1
    token_b, _ = register(client, org_name="Org B", email="b@example.test")

    foreign_call = client.get(f"/api/calls/{call_id}", headers=auth_headers(token_b))
    assert foreign_call.status_code == 404
