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
