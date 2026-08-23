"""Lane E — tenancy isolation contract tests (Lane A backend).

Frozen contract (spec 2026-08-23 §4/§7):
- POST /api/auth/register {org_name,email,password} -> {token,user}
- All queries org-scoped; cross-org GET by id -> 404 (not 403, no existence leak)
- JWT bearer required; tokens without org context rejected
- Roles: owner/admin/member; members must not delete agents

Skips with a precise reason while Lane A modules are unmerged so the suite
stays runnable in CI.
"""
from __future__ import annotations

from typing import Any

import pytest

from _qa_contract import (
    api,
    build_test_client,
    create_agent,
    expect_merged,
    import_app,
    mint_token_without_org,
    provision_member,
    register_org,
)


@pytest.fixture(scope="module")
def qa_client() -> Any:
    app, why_app = import_app()
    if app is None:
        pytest.skip(f"[Lane A] backend app not merged yet: {why_app}")
    client, why_client = build_test_client(app)
    if client is None:
        pytest.skip(f"[Lane A] test harness unavailable: {why_client}")
    with client as entered:
        yield entered


@pytest.fixture(scope="module")
def two_orgs(qa_client: Any) -> dict[str, dict[str, Any]]:
    org_a, why_a = register_org(qa_client, org_name="Org A", email="owner-a@example.com")
    org_a = expect_merged(org_a, f"org A registration broken: {why_a}")
    org_b, why_b = register_org(qa_client, org_name="Org B", email="owner-b@example.com")
    org_b = expect_merged(org_b, f"org B registration broken: {why_b}")
    return {"a": org_a, "b": org_b}


@pytest.fixture(scope="module")
def agent_of_org_a(qa_client: Any, two_orgs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    agent, why = create_agent(qa_client, two_orgs["a"]["token"], "A-private-agent")
    return expect_merged(agent, f"agent creation unavailable: {why}")


def test_org_b_listing_hides_org_a_agents(
    qa_client: Any, two_orgs: dict[str, dict[str, Any]], agent_of_org_a: dict[str, Any]
) -> None:
    resp = api(qa_client, "GET", "/api/agents", token=two_orgs["b"]["token"])
    assert resp.status_code == 200, f"listing failed: {resp.status_code} {resp.text[:300]}"
    body = resp.json()
    items = body if isinstance(body, list) else body.get("items") or body.get("agents") or []
    ids = {row.get("id") for row in items if isinstance(row, dict)}
    assert agent_of_org_a.get("id") not in ids, (
        f"org B can see org A's agent id={agent_of_org_a.get('id')} in listing"
    )
    assert len(items) == 0, f"fresh org B should have zero agents, saw {len(items)}"


def test_cross_org_get_agent_returns_404(
    qa_client: Any, two_orgs: dict[str, dict[str, Any]], agent_of_org_a: dict[str, Any]
) -> None:
    resp = api(
        qa_client,
        "GET",
        f"/api/agents/{agent_of_org_a.get('id')}",
        token=two_orgs["b"]["token"],
    )
    assert resp.status_code == 404, (
        "cross-org GET must be 404 (existence-leak guard), got "
        f"{resp.status_code}: {resp.text[:300]}"
    )


def test_request_without_auth_is_rejected(qa_client: Any) -> None:
    resp = qa_client.get("/api/agents")
    assert resp.status_code in (401, 403), (
        f"unauthenticated request must be rejected, got {resp.status_code}: {resp.text[:300]}"
    )


def test_jwt_without_org_context_is_rejected(
    qa_client: Any, two_orgs: dict[str, dict[str, Any]]
) -> None:
    user_id = (two_orgs["a"]["user"] or {}).get("id", "1")
    token, why = mint_token_without_org(user_id)
    if token is None:
        pytest.skip(f"[Lane A] cannot mint an org-less JWT: {why}")
    resp = api(qa_client, "GET", "/api/agents", token=token)
    assert resp.status_code in (401, 403), (
        "JWT lacking org context must be rejected, got "
        f"{resp.status_code}: {resp.text[:300]}"
    )
    assert resp.status_code != 200


def test_member_cannot_delete_agent(
    qa_client: Any, two_orgs: dict[str, dict[str, Any]], agent_of_org_a: dict[str, Any]
) -> None:
    member, why_member = provision_member(qa_client, two_orgs["a"])
    if member is None:
        pytest.skip(f"[Lane A] member provisioning unavailable: {why_member}")
    resp = api(
        qa_client,
        "DELETE",
        f"/api/agents/{agent_of_org_a.get('id')}",
        token=member["token"],
    )
    assert resp.status_code == 403, (
        f"member DELETE must be 403 Forbidden, got {resp.status_code}: {resp.text[:300]}"
    )
    still_there = api(
        qa_client,
        "GET",
        f"/api/agents/{agent_of_org_a.get('id')}",
        token=two_orgs["a"]["token"],
    )
    assert still_there.status_code == 200, "member must not be able to archive/delete either"


def test_owner_can_see_own_agent(
    qa_client: Any, two_orgs: dict[str, dict[str, Any]], agent_of_org_a: dict[str, Any]
) -> None:
    resp = api(
        qa_client,
        "GET",
        f"/api/agents/{agent_of_org_a.get('id')}",
        token=two_orgs["a"]["token"],
    )
    assert resp.status_code == 200, f"owner lost access to own agent: {resp.status_code}"
