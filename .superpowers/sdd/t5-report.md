# Task 5 Report: test-call dispatch — agent_version_id + room_name

**Status:** COMPLETE — full suite green (96 passed = 92 baseline + 4 new).

## Files changed
- `backend/app/schemas.py` — `TestCallRequest` gained `agent_version_id: Optional[int] = None`; `TestCallOut` gained required `room_name: str`.
- `backend/app/routers/test_call.py` — route now authenticated (`user: User = Depends(get_current_user)`); resolves `AgentVersion` (explicit id → else latest version joined through agents filtered by `user.org_id`, both 422 on miss); stamps `Call.agent_version_id=version.id`; returns `room_name = f"{PHONE_ROOM_PREFIX}{call.id}"`.
- `backend/tests/test_call_flow.py` — NEW, 4 tests (auth required / unknown version 422 / happy path stamps version + room_name / omitted id falls back to latest org version).

## TDD evidence
- Step 2 red run: 4/4 failed for the intended reasons (`422 != 401` pre-auth; unknown-version returned 200; `KeyError: 'room_name'`; `agent_version_id None == 1`).
- Step 4 green run: `tests\test_call_flow.py` 4 passed; full suite `pytest -q` → **96 passed**, no regressions.

## Adaptations from brief (conftest/model reality)
1. **`AgentVersion.created_by` IS nullable** (models.py:147) → dropped `created_by` and the raw-SQL owner-id lookup from the seed fixture entirely.
2. **`DomainConfig` has no `question_flow`/`extraction_schema` columns** (those live on AgentVersion; DomainConfig is name/version/display_name/config) → seeded `DomainConfig(name="call-flow-test", version=1)` and pass its actual id to the POSTs instead of hardcoding 1.
3. **Consent enforcement defaults ON with an empty allowlist in test settings** (`consent_enforcement=True`, `test_phone_numbers=""` in conftest's `make_settings`; conftest.py out of scope) → added an in-module `allowlisted` fixture that sets `app.state.settings.test_phone_numbers = "+919391470646"`, mirroring production allowlist semantics.
4. Imports trimmed to what conftest actually provides (`auth_headers`, `register`; `make_settings` unused by tests).

## Pre-existing tests broken by auth change
None. Grep for "test-call"/"test_call"/"place_test_call" across `backend/tests` found only unrelated names (`test_calls_index.py`, `test_call_detail.py`) — no prior coverage hit `/api/test-call`, so nothing needed updating.

## Concerns
- The endpoint still auto-creates/reuses a shared "Test Calls" campaign without `org_id`; tenancy scoping of that campaign row was out of scope here but may deserve a follow-up.
- Fallback ("latest org version") resolution orders by `AgentVersion.id.desc()`, not per-agent recency — matches the locked brief interface; noting it as intentional.
