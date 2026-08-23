"""Lane E — agent version immutability contract tests (Lane A backend).

Frozen contract (spec 2026-08-23 §3/§4):
- POST /api/agents/{id}/versions -> immutable row, version int bumps,
  agent.current_version_id advances
- DELETE /api/agents/{id} is a soft archive: hidden from list,
  but versions remain queryable

Skips with a precise reason while Lane A modules are unmerged.
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

import pytest

from _qa_contract import (
    api,
    build_test_client,
    create_agent,
    create_version,
    expect_merged,
    import_app,
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
def agent_with_two_versions(qa_client: Any) -> dict[str, Any]:
    owner, why_org = register_org(
        qa_client, org_name="Versions Org", email="versions-owner@example.com"
    )
    owner = expect_merged(owner, f"registration broken: {why_org}")
    token = owner["token"]
    agent, why_agent = create_agent(qa_client, token, f"immutable-{uuid.uuid4().hex[:8]}")
    agent = expect_merged(agent, f"agent creation unavailable: {why_agent}")

    v1, why_v1 = create_version(qa_client, token, agent["id"])
    v1 = expect_merged(v1, f"v1 creation unavailable: {why_v1}")
    v2, why_v2 = create_version(
        qa_client,
        token,
        agent["id"],
        overrides={"system_prompt": "You are an AI voice assistant for the alumni office. Updated persona."},
    )
    v2 = expect_merged(v2, f"v2 creation unavailable: {why_v2}")
    return {"token": token, "agent": agent, "v1": v1, "v2": v2}


def _version_id(version_row: dict[str, Any]) -> Any:
    return version_row.get("id") or version_row.get("version_id")


def _version_number(version_row: dict[str, Any]) -> Any:
    return version_row.get("version", version_row.get("version_number"))


def test_v1_row_unchanged_after_creating_v2(
    qa_client: Any, agent_with_two_versions: dict[str, Any]
) -> None:
    ctx = agent_with_two_versions
    v1_snapshot = copy.deepcopy(ctx["v1"])
    vid = _version_id(v1_snapshot)

    resp = api(qa_client, "GET", f"/api/agent-versions/{vid}", token=ctx["token"])
    assert resp.status_code == 200, f"fetching v1 failed {resp.status_code}: {resp.text[:300]}"
    fetched = resp.json()

    volatile = {"created_at", "updated_at"}
    for key, original in v1_snapshot.items():
        if key in volatile:
            continue
        assert fetched.get(key) == original, (
            f"v1 field '{key}' mutated after v2 creation: "
            f"{str(original)[:80]!r} -> {str(fetched.get(key))[:80]!r}"
        )


def test_versions_list_shows_immutable_history(
    qa_client: Any, agent_with_two_versions: dict[str, Any]
) -> None:
    ctx = agent_with_two_versions
    agent_id = ctx["agent"]["id"]
    resp = api(qa_client, "GET", f"/api/agents/{agent_id}/versions", token=ctx["token"])
    assert resp.status_code == 200, f"versions list failed {resp.status_code}: {resp.text[:300]}"
    rows = resp.json()
    rows = rows if isinstance(rows, list) else rows.get("items") or rows.get("versions") or []
    numbers = sorted(_version_number(row) for row in rows)
    assert numbers[:2] == [1, 2], f"expected versions [1, 2], got {numbers}"
    v1_ids = {_version_id(row) for row in rows}
    assert _version_id(ctx["v1"]) in v1_ids, "v1 id vanished from history"


def test_current_version_id_advances_to_latest(
    qa_client: Any, agent_with_two_versions: dict[str, Any]
) -> None:
    ctx = agent_with_two_versions
    agent_id = ctx["agent"]["id"]
    resp = api(qa_client, "GET", f"/api/agents/{agent_id}", token=ctx["token"])
    assert resp.status_code == 200, f"agent fetch failed {resp.status_code}: {resp.text[:300]}"
    detail = resp.json()
    current = detail.get("current_version_id")
    expected = _version_id(ctx["v2"]) or _version_number(ctx["v2"])
    assert current == expected, (
        f"current_version_id should point at v2 ({expected}), got {current}"
    )


def test_archived_agent_hidden_from_list_but_versions_queryable(
    qa_client: Any, agent_with_two_versions: dict[str, Any]
) -> None:
    ctx = agent_with_two_versions
    token = ctx["token"]
    agent_id = ctx["agent"]["id"]
    v1_id = _version_id(ctx["v1"])

    del_resp = api(qa_client, "DELETE", f"/api/agents/{agent_id}", token=token)
    assert del_resp.status_code in (200, 204), (
        f"soft delete failed {del_resp.status_code}: {del_resp.text[:300]}"
    )

    listing = api(qa_client, "GET", "/api/agents", token=token)
    assert listing.status_code == 200, f"listing after archive failed {listing.status_code}"
    body = listing.json()
    items = body if isinstance(body, list) else body.get("items") or body.get("agents") or []
    ids = {row.get("id") for row in items if isinstance(row, dict)}
    assert agent_id not in ids, "archived agent still visible in GET /api/agents"

    versions = api(qa_client, "GET", f"/api/agents/{agent_id}/versions", token=token)
    assert versions.status_code == 200, (
        f"archived agent's versions must remain queryable, got {versions.status_code}"
    )

    v1_fetch = api(qa_client, "GET", f"/api/agent-versions/{v1_id}", token=token)
    assert v1_fetch.status_code == 200, (
        f"archived agent's v1 must remain queryable by id, got {v1_fetch.status_code}"
    )
