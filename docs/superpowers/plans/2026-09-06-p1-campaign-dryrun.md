# P1 Campaign Dry-Run + Contact-Aware Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship text-mode campaign dry-runs with scripted caller personas, contact-aware Playground/TestCall, a protected agent-first greeting, and a real-estate preset — per `docs/superpowers/specs/2026-09-06-p1-campaign-dryrun-design.md`.

**Architecture:** Backend-first TDD: port token substitution to the backend, generalize the text prompt, extract the text-turn core for reuse by a dry-run runner that persists `kind="dry-run"` calls; voice gets alias tokens plus a deterministic opening spoken with interruptions disabled; frontend wires the already-capable APIs and adds the dry-run report UI.

**Tech Stack:** FastAPI + SQLAlchemy (backend), LiveKit Agents Python (voice-agent), React 18 + Vite (frontend), pytest with hermetic SQLite (backend tests), pytest (voice-agent tests), `npm run build` (frontend verification — no test runner).

## Global Constraints

- Type hints required in all Python (backend FastAPI + Pydantic; voice-agent standard layout).
- Never hardcode API keys — everything through `.env`; keep `.env.example` in sync (no new credentials in P1).
- P1 changes stay UI/test-contact + prompt/core-greeting: no latency tuning, no concurrency changes, no new providers (spec D7).
- Never fabricate a structured-field value on low confidence — escalate/flag per FR-12, don't guess.
- `DomainConfig.name` is globally unique with no org scoping — auto-created rows must namespace the name per agent.
- No real network in tests: Groq HTTP is monkeypatched via the `_FakeAsyncClient` pattern in `backend/tests/test_playground_text.py`.
- Backend tests run from `backend/` with `.\.venv\Scripts\python.exe -m pytest tests/<file>.py -q`.
- Voice-agent tests run from `voice-agent/` with `.\.venv\Scripts\python.exe -m pytest tests/<file>.py -q`.
- Frontend has no test runner — verify with `npm run build` from `frontend/`.
- TDD every task: failing test, minimal implementation, green, commit. One task = one commit, staged files only.
- Every call domain stays a config/preset file — never a code branch.

---

## File structure (what changes, and why)

- Create `backend/app/services/token_substitution.py` — backend port of the voice worker's token map (`build_token_map`, `apply_token_substitution`) plus lead-gen aliases. Single responsibility: bracket tokens in, clean text out.
- Modify `backend/app/routers/playground.py` — generic caller-context block, institution injection, substitution wiring, `_run_agent_turn` extraction, dry-run endpoint. Stays the owner of all text-mode conversation logic.
- Create `backend/app/services/dry_run.py` — personas as data (`PERSONAS`, `persona_reply`) plus the runner (`run_campaign_dry_run`, `_mask_phone`). No HTTP, no DB-session creation inside — takes `db`/`settings` as args so tests drive it directly.
- Modify `backend/app/schemas.py` — `TestCallRequest.domain_config_id` optional; new `DryRunCreate`/`DryRunContactResult`/`DryRunReport` models.
- Modify `backend/app/routers/test_call.py` — derive `domain_config_id` when omitted.
- Modify `backend/app/routers/agents.py` — `ensure_domain_config(db, agent, version)` helper (find-or-create namespaced row).
- Modify `voice-agent/app/prompting.py` — alias tokens, `lead_name` in `_first_name`, new `build_opening_line`.
- Modify `voice-agent/app/pipeline.py` — `_speak_opening` helper + 4-line wiring after `session.start`.
- Create `domain-configs/presets/real-estate-lead-qualification.json` — complete builder payload mirroring `lead-verification.json`.
- Create `frontend/src/components/LeadCardForm.jsx` — one lead-card form reused by Playground setup and TestCall.
- Create `frontend/src/components/DryRunReport.jsx` — per-contact accordion report with client-side CSV download.
- Modify `frontend/src/api.js`, `frontend/src/pages/PlaygroundPage.jsx`, `frontend/src/components/TextPlayground.jsx`, `frontend/src/pages/TestCallPage.jsx`, `frontend/src/pages/CampaignDetailPage.jsx` — pass `contact`, pick versions, dry-run button.
- Create `docs/superpowers/evaluations/p2-exit-gates.md` — the P2 gate checklist (empty results, filled during live verification).
- Tests: `backend/tests/test_token_substitution.py`, `backend/tests/test_playground_contact.py`, `backend/tests/test_testcall_contact.py`, `backend/tests/test_dry_run.py` (new); extend `backend/tests/test_agents.py` (preset assertion); `voice-agent/tests/test_opening_line.py` (new); extend `voice-agent/tests/test_token_substitution.py` (aliases).

Task order with parallel groups: Task 1 → Task 2 (backend chain). Task 3 and Task 6 are independent (start anytime after Task 1). Tasks 4 → 5 (voice chain, independent of backend). Task 7 needs Task 2's `_run_agent_turn`. Task 8 needs Task 7's endpoint. Task 9 needs Task 8. Task 10 closes.

---

### Task 1: Backend token-substitution service

**Files:**
- Create: `backend/app/services/token_substitution.py`
- Test: `backend/tests/test_token_substitution.py`

**Interfaces:**
- Consumes: nothing (pure functions, stdlib only).
- Produces: `build_token_map(contact: Optional[Mapping[str, Any]], institution: str = "", agent_name: str = "") -> dict[str, str]`; `apply_token_substitution(text: str, tokens: Optional[Mapping[str, str]] = None) -> str`; `KNOWN_TOKENS: tuple[str, ...]` — used by Task 2 (and mirrored by the voice worker's extended map in Task 4).

- [ ] **Step 1: Write the failing test**

```python
"""Bracket-token substitution ported from voice-agent/app/prompting.py."""
from __future__ import annotations

from app.services.token_substitution import (
    KNOWN_TOKENS,
    apply_token_substitution,
    build_token_map,
)


def test_known_tokens_cover_lead_gen_aliases() -> None:
    assert set(KNOWN_TOKENS) >= {
        "[Institution Name]",
        "[Company Name]",
        "[Student Name]",
        "[Lead Name]",
        "[Parent/Guardian Name]",
        "[Agent Name]",
        "[Expected Return Date]",
    }


def test_build_token_map_resolves_names_and_institution() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"}
    tokens = build_token_map(contact, institution="Demo School")
    assert tokens["[Student Name]"] == "Aarav Kumar"
    assert tokens["[Parent/Guardian Name]"] == "Suresh Kumar"
    assert tokens["[Institution Name]"] == "Demo School"
    assert tokens["[Company Name]"] == "Demo School"


def test_build_token_map_lead_style_contact() -> None:
    tokens = build_token_map({"lead_name": "Riya", "city": "Hyderabad"}, institution="Acme Realty")
    assert tokens["[Lead Name]"] == "Riya"
    assert tokens["[Student Name]"] == "Riya"


def test_build_token_map_agent_name_defaults_to_assistant() -> None:
    assert build_token_map({})["[Agent Name]"] == "an AI assistant"
    assert build_token_map({}, agent_name="Priya")["[Agent Name]"] == "Priya"


def test_apply_token_substitution_replaces_and_drops_empties() -> None:
    tokens = build_token_map({"student_name": "Aarav"}, institution="")
    out = apply_token_substitution(
        "Hello [Parent/Guardian Name], calling from [Institution Name] about [Student Name].",
        tokens,
    )
    assert "[Parent/Guardian Name]" not in out
    assert "[Institution Name]" not in out
    assert "Aarav" in out
    assert "  " not in out


def test_apply_token_substitution_strips_unknown_brackets() -> None:
    out = apply_token_substitution("See [Something Else] today.", {})
    assert "[" not in out and "]" not in out
    assert out == "See today."


def test_apply_token_substitution_falsy_passthrough() -> None:
    assert apply_token_substitution("", {}) == ""
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_token_substitution.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.token_substitution'` (or `ImportError`).

- [ ] **Step 3: Write minimal implementation**

```python
"""Bracket-token substitution ported from voice-agent/app/prompting.py.

Keep the two in sync: KNOWN_TOKENS here must cover the same placeholder
names the voice worker understands, plus the lead-gen aliases presets use
([Lead Name], [Company Name], [Agent Name]).
"""
from __future__ import annotations

import re
from typing import Any, Mapping, Optional

KNOWN_TOKENS: tuple[str, ...] = (
    "[Institution Name]",
    "[Company Name]",
    "[Student Name]",
    "[Lead Name]",
    "[Parent/Guardian Name]",
    "[Agent Name]",
    "[Expected Return Date]",
)

_BRACKET_ARTIFACT_RE = re.compile(r"\[[^\]]*\]")
_DOUBLE_SPACE_RE = re.compile(r"\s{2,}")

_NAME_KEYS = ("student_name", "name", "contact_name", "full_name", "lead_name")
_PARENT_KEYS = ("parent_name", "parent", "guardian", "contact_person")


def _first(contact: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = str(contact.get(key) or "").strip()
        if value:
            return value
    return ""


def build_token_map(
    contact: Optional[Mapping[str, Any]] = None,
    institution: str = "",
    agent_name: str = "",
) -> dict[str, str]:
    """Resolve known placeholder tokens to real values for this call."""
    card = contact if isinstance(contact, Mapping) else {}
    name = _first(card, _NAME_KEYS)
    parent = _first(card, _PARENT_KEYS)
    org = str(institution or "").strip()
    who = str(agent_name or "").strip() or "an AI assistant"
    return {
        "[Institution Name]": org,
        "[Company Name]": org,
        "[Student Name]": name,
        "[Lead Name]": name,
        "[Parent/Guardian Name]": parent,
        "[Agent Name]": who,
        "[Expected Return Date]": "",
    }


def apply_token_substitution(
    text: str, tokens: Optional[Mapping[str, str]] = None
) -> str:
    """Replace known bracket tokens; empties removed, leftovers stripped."""
    if not text:
        return text
    out = str(text)
    for token, value in (tokens or {}).items():
        out = out.replace(str(token), str(value) if value is not None else "")
    out = _BRACKET_ARTIFACT_RE.sub("", out)
    return _DOUBLE_SPACE_RE.sub(" ", out).strip()
```

- [ ] **Step 4: Run test to verify it passes**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_token_substitution.py -q`
Expected: `7 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/token_substitution.py backend/tests/test_token_substitution.py
git commit -m "feat: backend bracket-token substitution service with lead-gen aliases"
```

---

### Task 2: Generic caller context + institution + substitution in the text prompt

**Files:**
- Modify: `backend/app/routers/playground.py` (import `Organization`, `Campaign`, `Contact` from `app.models`; import `build_token_map`/`apply_token_substitution` from `app.services.token_substitution`; add `_render_caller_context`; extend `_render_text_system_prompt` with `institution="""` param and substitution; update the `create_turn` call site and kickoff lines)
- Test: `backend/tests/test_playground_contact.py`

**Interfaces:**
- Consumes: Task 1 (`build_token_map`, `apply_token_substitution`).
- Produces: `_render_caller_context(contact: dict[str, str], institution: str) -> str`; `_render_text_system_prompt(config: Any, contact: Optional[dict[str, str]] = None, institution: str = "") -> str` — used by Task 7's `_run_agent_turn` unchanged.

- [ ] **Step 1: Write the failing test**

```python
"""Generic caller context + token substitution in the text-mode prompt."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.routers.playground import _render_caller_context, _render_text_system_prompt


def _config(**overrides: Any) -> Any:
    base: dict[str, Any] = {
        "disclosure_script": "Hi, this is [Agent Name] calling from [Institution Name].",
        "system_prompt": "You call about [Student Name].",
        "company_context": {},
        "question_flow": [{"step": 1, "question": "Why was [Student Name] absent?"}],
        "extraction_schema": {},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_absent_student_card_names_and_institution() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar", "class_section": "10-A"}
    prompt = _render_text_system_prompt(_config(), contact=contact, institution="Demo School")
    assert "Aarav Kumar" in prompt
    assert "Suresh Kumar" in prompt
    assert "Demo School" in prompt
    assert "[Student Name]" not in prompt
    assert "[Institution Name]" not in prompt
    assert "Why was Aarav Kumar absent?" in prompt


def test_lead_style_card_generic_phrasing() -> None:
    contact = {"lead_name": "Riya", "city": "Hyderabad"}
    block = _render_caller_context(contact, "Acme Realty")
    assert "Riya" in block
    assert "Hyderabad" in block
    assert "the person Riya" in block
    assert "absent" not in block.lower()
    assert "class_section" not in block


def test_empty_contact_guards_against_invented_names() -> None:
    block = _render_caller_context({}, "")
    assert "NEVER invent or guess any name" in block
    prompt = _render_text_system_prompt(_config(), contact=None, institution="")
    assert "CALLER CONTEXT" in prompt
    assert "NEVER invent or guess any name" in prompt


def test_empty_institution_drops_cleanly() -> None:
    prompt = _render_text_system_prompt(_config(), contact={"student_name": "Aarav"}, institution="")
    assert "Aarav" in prompt
    assert "[Institution Name]" not in prompt
    # Scoped: the static HOW-TO-REPLY block intentionally uses two-space
    # indentation, so the no-gap check applies to substituted text only.
    disclosure_line = next(l for l in prompt.splitlines() if "AI assistant calling from" in l)
    assert "  " not in disclosure_line
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_playground_contact.py -q`
Expected: FAIL with `ImportError` (`_render_caller_context` does not exist yet).

- [ ] **Step 3: Write minimal implementation**

Apply these edits in `backend/app/routers/playground.py`:

(a) Extend the models import (line 31) and add the service import after the timeutil import (line 32):

```python
from app.models import Agent, AgentVersion, Call, Campaign, Contact, ExtractedField, Organization, Transcript, User
```

```python
from app.services.token_substitution import apply_token_substitution, build_token_map
```

(b) Insert `_render_caller_context` before `_render_text_system_prompt` (which starts at line 303):

```python
_GENERIC_SUBJECT_KEYS = ("full_name", "contact_name", "lead_name", "candidate_name", "name")
_GENERIC_PARENT_KEYS = ("parent_name", "parent", "guardian", "contact_person")


def _render_caller_context(contact: dict[str, str], institution: str) -> str:
    """CALLER CONTEXT block that works for any domain, not just absent-student.

    Known keys get human phrasing; every other supplied key is passed through
    as a fact so domain-specific cards (city, budget, form_source, ...) still
    reach the agent. With no contact, emits a do-not-invent-names guard.
    """
    lines = ["CALLER CONTEXT - who this specific call is about:"]
    if institution:
        lines.append(f"- You are calling from {institution}.")
    if not contact:
        lines.append(
            "- You were NOT given the callee's name: NEVER invent or guess any name; "
            "ask who you are speaking with."
        )
        return "\n".join(lines)

    student = contact.get("student_name") or ""
    parent = ""
    for key in _GENERIC_PARENT_KEYS:
        if contact.get(key):
            parent = contact[key]
            break
    subject = ""
    for key in _GENERIC_SUBJECT_KEYS:
        if contact.get(key):
            subject = contact[key]
            break
    about: list[str] = []
    if student:
        about.append(f"the student {student}")
    if contact.get("class_section"):
        about.append(f"class {contact['class_section']}")
    if contact.get("absent_date"):
        about.append(f"absent on {contact['absent_date']}")
    if subject and subject != student:
        about.append(f"the person {subject}")
    if about:
        lines.append("- You are calling about " + ", ".join(about) + ".")
    else:
        lines.append("- Details: " + json.dumps(contact, ensure_ascii=False))
    woven = {"student_name", "class_section", "absent_date", *_GENERIC_SUBJECT_KEYS, *_GENERIC_PARENT_KEYS}
    extras = {k: v for k, v in contact.items() if k not in woven}
    if extras:
        lines.append(
            "- Other details you may use if relevant: "
            + json.dumps(extras, ensure_ascii=False, sort_keys=True)
        )
    if parent:
        lines.append(f"- Ask to speak with {parent} (the parent/guardian).")
    elif subject:
        lines.append(f"- Ask for {subject} when the call is answered.")

    names: list[str] = []
    for value in [parent, student, subject]:
        if value and value not in names:
            names.append(value)
    if names:
        lines.append(
            "- SAY THE NAMES OUT LOUD: greet the person using their name. "
            f"Known name(s) on this record: {', '.join(names)}."
        )
        lines.append(
            "- NEVER say 'the parent or guardian of the student' or 'the person "
            "we are calling about' when you have a real name on this record."
        )
    lines.extend(
        [
            "- VERIFY RELATIONSHIP BEFORE DETAILS: confirm you are speaking with the "
            "right person before discussing any details.",
            "- If the person who answered is NOT that person, do not share any details: "
            "ask when they will be available, thank them politely, and end the call.",
        ]
    )
    return "\n".join(lines)
```

(c) Change the signature of `_render_text_system_prompt` (line 303) and wire substitution + the new block:

```python
def _render_text_system_prompt(
    config: Any,
    contact: Optional[dict[str, str]] = None,
    institution: str = "",
) -> str:
```

Inside, after `sections: list[str] = []`, insert:

```python
    card = contact or {}
    tokens = build_token_map(card, institution=institution)
```

Change the disclosure line (line 315) to substitute:

```python
    disclosure = apply_token_substitution(str(config.disclosure_script or "").strip(), tokens)
```

Change the persona handling (lines 327-330) to substitute and render the
creator's role as its own authoritative block, mirroring voice-agent
`render_system_prompt` §2b (this module is its slim server-side twin):

```python
    persona = apply_token_substitution(str(config.system_prompt or "").strip(), tokens)
    sections.append(
        "WHO YOU ARE:\n" + "\n".join(f"- {line}" for line in role_lines)
    )
    # 2b. Creator's role definition - authoritative, verbatim (not a bullet).
    if persona:
        sections.append(
            "ROLE & MISSION - defined by the agent creator (AUTHORITATIVE):\n"
            f"{persona}\n"
            "This role definition is authoritative for WHO you are and HOW you "
            "behave: where it differs from generic examples, follow the role "
            "definition."
        )
```

(Controller amendment 2026-09-06: the implementer's 2b structure was accepted
over the original one-line substitution — twin-parity with the voice worker,
persona still verbatim, regression suites green.)

Replace the whole 3b block (lines 349-407, the `if contact:` ... `sections.append("\n".join(context_lines))`) with:

```python
    # 3b. CALLER CONTEXT (P0-2, generic) — who this specific call is about.
    sections.append(_render_caller_context(card, institution))
```

Change the goals loop (line 423-424) to substitute each question:

```python
        text_value = apply_token_substitution(_question_text(item), tokens)
```

(d) Update the `create_turn` call site (lines 649-651) to pass the institution from the org row:

```python
    contact = (call.context or {}).get("contact") or {}
    org = db.get(Organization, call.org_id) if call.org_id else None
    institution = org.name if org and org.name else ""
    system_prompt = _render_text_system_prompt(version, contact=contact, institution=institution)
```

(e) Generalize the kickoff tail (lines 674-681) to use the token map so lead-style cards work:

```python
        contact = (call.context or {}).get("contact") or {}
        tokens = build_token_map(contact, institution)
        student = tokens["[Student Name]"]
        parent = tokens["[Parent/Guardian Name]"]
        if student:
            kickoff += (
                f" You are calling about {student}"
                + (f"; ask to speak with {parent}." if parent else ".")
            )
```

Note: `institution` is already in scope at (e) because (d) runs before the history query — keep (d) where the `system_prompt = ...` line is (line 649) so both uses share it. Lines 674's `contact = ...` re-fetch stays; only replace the `student = ...` / `parent = ...` lines with the token-map version.

- [ ] **Step 4: Run tests to verify they pass, plus the existing text-mode suite for regressions**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_playground_contact.py tests/test_playground_text.py tests/test_playground.py -q`
Expected: all pass (new 4 + existing suites unchanged).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/playground.py backend/tests/test_playground_contact.py
git commit -m "feat: generic caller context, institution and token substitution in text prompt"
```

---

### Task 3: Optional domain on test-call + auto-derived DomainConfig

**Files:**
- Modify: `backend/app/schemas.py` (`TestCallRequest.domain_config_id` optional), `backend/app/routers/test_call.py` (derive when omitted), `backend/app/routers/agents.py` (add `ensure_domain_config`)
- Test: `backend/tests/test_testcall_contact.py`

**Interfaces:**
- Consumes: `Agent`, `AgentVersion`, `DomainConfig` models; `normalize_phone`.
- Produces: `ensure_domain_config(db: Session, agent: Agent, version: AgentVersion) -> DomainConfig` in `app.routers.agents` — reused by Task 8's dry-run only indirectly (no direct reuse; documented for the phone path).

- [ ] **Step 1: Write the failing test**

```python
"""Contact-aware test calls: version pin + lead card + derived domain config."""
from __future__ import annotations

from typing import Any

from conftest import auth_headers, make_settings, register
from test_agents import version_payload
from test_playground import _make_agent_and_version


def _test_number_app(session_factory):  # type: ignore[no-untyped-def]
    from fastapi.testclient import TestClient

    from app.main import create_app

    fresh = create_app(
        make_settings(test_phone_number_list=["+919812345601"])
    )
    fresh.state.session_factory = session_factory
    return fresh


def test_test_call_forwards_version_and_contact(client, session_factory):
    from fastapi.testclient import TestClient

    from app.models import Call, Contact

    token, user = register(client)
    ids = _make_agent_and_version(client, token)
    version_id = ids["version"]["id"]
    with TestClient(_test_number_app(session_factory)) as numbered:
        resp = numbered.post(
            "/api/test-call",
            json={
                "to": "+919812345601",
                "agent_version_id": version_id,
                "contact": {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"},
            },
            headers=auth_headers(token),
        )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["provider_call_id"].startswith("CAfake")
    with session_factory() as db:
        call = db.get(Call, body["call_id"])
        assert call.agent_version_id == version_id
        contact = db.get(Contact, call.contact_id)
        assert contact.custom_fields["student_name"] == "Aarav Kumar"
        assert contact.custom_fields["parent_name"] == "Suresh Kumar"


def test_test_call_derives_domain_config_when_omitted(client, session_factory):
    from fastapi.testclient import TestClient

    from app.models import Call, DomainConfig

    token, _user = register(client)
    ids = _make_agent_and_version(client, token)
    with TestClient(_test_number_app(session_factory)) as numbered:
        resp = numbered.post(
            "/api/test-call",
            json={"to": "+919812345601", "agent_version_id": ids["version"]["id"]},
            headers=auth_headers(token),
        )
    assert resp.status_code == 200, resp.text
    with session_factory() as db:
        call = db.get(Call, resp.json()["call_id"])
        derived = db.get(DomainConfig, call.campaign.domain_config_id)
        assert derived is not None
        assert derived.name.startswith(f"agent-{ids['agent']['id']}-")
        assert "system_prompt" in (derived.config or {})
```

Note: `client` here is the default conftest app client (for register/agent setup); the POST goes to a second app instance whose settings carry `test_phone_number_list` so the allowlist check passes with consent enforcement on. Both apps share `session_factory`, so rows are visible to both. The default `client` fixture's telephony is the in-memory fake (no provider credentials in test settings), returning `CAfake{call_id:010d}`.

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_testcall_contact.py -q`
Expected: FAIL — `TestCallRequest` rejects the missing `domain_config_id` with 422.

- [ ] **Step 3: Write minimal implementation**

(a) `backend/app/schemas.py` — change the field (line 244):

```python
    domain_config_id: Optional[int] = None
```

(b) `backend/app/routers/agents.py` — append the helper (needs `AgentVersion`, `DomainConfig` imports; check the file's existing model imports and extend them to include both):

```python
def ensure_domain_config(db: Session, agent: Agent, version: AgentVersion) -> DomainConfig:
    """Find-or-create the legacy DomainConfig row anchoring an agent's phone path.

    The voice brain is version-based, but campaigns and /api/test-call still
    carry a ``domain_config_id`` FK. ``DomainConfig.name`` is globally unique,
    so the auto row is namespaced per agent and never collides across orgs.
    """
    wanted = f"agent-{agent.id}-phone"
    existing = db.scalar(select(DomainConfig).where(DomainConfig.name == wanted))
    if existing is not None:
        return existing
    row = DomainConfig(
        name=wanted,
        display_name=agent.name,
        config={
            "domain_id": wanted,
            "name": agent.name,
            "version": version.version,
            "system_prompt": version.system_prompt,
            "mandatory_disclosure": version.disclosure_script,
            "question_flow": version.question_flow or [],
            "extraction_schema": version.extraction_schema or {},
            "escalation_rules": version.escalation_rules or [],
            "voice_settings": version.voice_settings or {},
        },
    )
    db.add(row)
    db.flush()
    return row
```

Required imports in `agents.py`: `Session` (sqlalchemy.orm), `select` (sqlalchemy), `Agent`, `AgentVersion`, `DomainConfig` (app.models). Extend the existing import lines rather than adding duplicates.

(c) `backend/app/routers/test_call.py` — replace the domain check (lines 67-68):

```python
    from app.routers.agents import ensure_domain_config

    agent = db.get(Agent, version.agent_id) if version is not None else None
```

Wait — ordering: version resolution happens at lines 70-87, after the domain check. Restructure minimally: keep lines 70-87 as-is, then after the version block insert:

```python
    if payload.domain_config_id is not None:
        if db.get(DomainConfig, payload.domain_config_id) is None:
            raise HTTPException(status_code=422, detail="unknown domain_config_id")
        domain_config_id = payload.domain_config_id
    else:
        agent = db.get(Agent, version.agent_id)
        domain_config_id = ensure_domain_config(db, agent, version).id
```

Delete lines 67-68. Then replace both uses of `payload.domain_config_id` in the campaign block (lines 92, 96-97) with `domain_config_id`. Move the `from app.routers.agents import ensure_domain_config` import to the top of the file (line 19-24 import block) to avoid a function-level import.

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_testcall_contact.py -q`
Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/schemas.py backend/app/routers/test_call.py backend/app/routers/agents.py backend/tests/test_testcall_contact.py
git commit -m "feat: test-call accepts version+contact, derives domain config when omitted"
```

---

### Task 4: Voice token aliases + deterministic opening line

**Files:**
- Modify: `voice-agent/app/prompting.py` (`KNOWN_TOKENS`, `build_token_map` + `agent_name` param, `_first_name` gains `lead_name`, new `build_opening_line` + `_contact_parent`/`_contact_subject` helpers reused by `render_caller_context`)
- Test: `voice-agent/tests/test_opening_line.py` (new); extend `voice-agent/tests/test_token_substitution.py` (aliases)

**Interfaces:**
- Consumes: existing `apply_token_substitution`, `_disclosure_text`, `_question_text`.
- Produces: `build_token_map(contact=None, context=None, agent_name: str = "") -> dict[str, str]` (extended); `build_opening_line(config: Mapping[str, Any], tokens: Optional[Mapping[str, str]] = None, contact: Optional[Mapping[str, Any]] = None) -> str` — used by Task 5.

- [ ] **Step 1: Write the failing tests**

New file `voice-agent/tests/test_opening_line.py`:

```python
"""Deterministic protected opening line: disclosure + greeting + first question."""
from app.prompting import build_opening_line, build_token_map

CONFIG = {
    "disclosure_script": "Hi, this is [Agent Name] calling from [Company Name].",
    "question_flow": [{"question": "Why was [Student Name] absent?"}],
}


def _tokens(contact, institution="Demo School"):
    return build_token_map(contact=contact, context={"institution_name": institution})


def test_opening_line_school_card() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"}
    out = build_opening_line(CONFIG, _tokens(contact), contact)
    assert out.startswith("Hi, this is an AI assistant calling from Demo School.")
    assert "Suresh Kumar" in out
    assert "Aarav Kumar" in out
    assert "Why was Aarav Kumar absent?" in out
    assert "[" not in out and "]" not in out


def test_opening_line_lead_card() -> None:
    contact = {"lead_name": "Riya"}
    out = build_opening_line(CONFIG, _tokens(contact, "Acme Realty"), contact)
    assert "Riya" in out and "Acme Realty" in out
    assert "[" not in out and "]" not in out


def test_opening_line_no_names_no_invention() -> None:
    out = build_opening_line(CONFIG, _tokens({}), {})
    assert "Hello" in out
    assert "[" not in out and "]" not in out


def test_opening_line_empty_without_disclosure() -> None:
    assert build_opening_line({"question_flow": []}, {}, {}) == ""
```

Append to `voice-agent/tests/test_token_substitution.py`:

```python
def test_build_token_map_lead_gen_aliases() -> None:
    m = build_token_map(
        contact={"lead_name": "Riya"},
        context={"institution_name": "Acme Realty"},
        agent_name="Priya",
    )
    assert m["[Lead Name]"] == "Riya"
    assert m["[Company Name]"] == "Acme Realty"
    assert m["[Agent Name]"] == "Priya"
    assert m["[Student Name]"] == "Riya"


def test_build_token_map_agent_name_defaults_to_assistant() -> None:
    assert build_token_map()["[Agent Name]"] == "an AI assistant"
```

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `voice-agent/`): `.\.venv\Scripts\python.exe -m pytest tests/test_opening_line.py tests/test_token_substitution.py -q`
Expected: FAIL — `test_opening_line.py` errors on import (`build_opening_line` undefined); the two new alias tests fail (`TypeError: unexpected agent_name` / missing keys).

- [ ] **Step 3: Write minimal implementation**

(a) Extend `KNOWN_TOKENS` (prompting.py lines 45-50):

```python
KNOWN_TOKENS: tuple[str, ...] = (
    "[Institution Name]",
    "[Company Name]",
    "[Student Name]",
    "[Lead Name]",
    "[Parent/Guardian Name]",
    "[Agent Name]",
    "[Expected Return Date]",
)
```

(b) Add `"lead_name"` to `_first_name` keys (line 101):

```python
        for key in ("student_name", "name", "contact_name", "full_name", "lead_name"):
```

(c) Extend `build_token_map` (lines 108-127):

```python
def build_token_map(
    contact: Optional[Mapping[str, Any]] = None,
    context: Optional[Mapping[str, Any]] = None,
    agent_name: str = "",
) -> dict[str, str]:
    """(docstring unchanged, plus:)

    ``agent_name`` fills ``[Agent Name]``; empty falls back to
    "an AI assistant" so disclosures never dangle.
    """
    ctx = context if isinstance(context, Mapping) else {}
    ctx_contact = ctx.get("contact") if isinstance(ctx.get("contact"), Mapping) else {}
    institution = str(ctx.get("institution_name") or "").strip()
    name = _first_name(contact, ctx_contact)
    who = str(agent_name or "").strip() or "an AI assistant"
    return {
        "[Institution Name]": institution,
        "[Company Name]": institution,
        "[Student Name]": name,
        "[Lead Name]": name,
        "[Parent/Guardian Name]": name,
        "[Agent Name]": who,
        "[Expected Return Date]": "",
    }
```

Note: `[Parent/Guardian Name]` keeps its existing same-as-name behavior (unchanged semantics; the opening line resolves parent vs subject from the card, not the map).

(d) Add card helpers + `build_opening_line` after `build_token_map` (after line 127):

```python
_CARD_PARENT_KEYS = ("parent_name", "parent", "guardian", "contact_person")
_CARD_SUBJECT_KEYS = ("student_name", "full_name", "contact_name", "lead_name", "candidate_name", "name")


def _card_value(card: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = str(card.get(key) or "").strip()
        if value:
            return value
    return ""


def build_opening_line(
    config: Mapping[str, Any],
    tokens: Optional[Mapping[str, str]] = None,
    contact: Optional[Mapping[str, Any]] = None,
) -> str:
    """Deterministic opening: disclosure + greeting + first question.

    Everything is token-substituted, so no ``[...]`` placeholder can ship.
    Returns "" when there is no disclosure script — the caller then falls
    back to the prompt-driven auto-turn.
    """
    tok = dict(tokens or {})
    disclosure = apply_token_substitution(_disclosure_text(config), tok)
    if not disclosure:
        return ""
    card = contact if isinstance(contact, Mapping) else {}
    parent = _card_value(card, _CARD_PARENT_KEYS)
    subject = _card_value(card, _CARD_SUBJECT_KEYS)
    institution = tok.get("[Institution Name]", "") or tok.get("[Company Name]", "")
    who = tok.get("[Agent Name]", "") or "an AI assistant"
    if parent and subject and parent != subject:
        if institution:
            greet = f"Hello {parent}, this is {who} calling from {institution} about {subject}."
        else:
            greet = f"Hello {parent}, this is {who} calling about {subject}."
    elif subject:
        if institution:
            greet = f"Hello {subject}, this is {who} calling from {institution}."
        else:
            greet = f"Hello {subject}, this is {who} calling."
    elif institution:
        greet = f"Hello, this is {who} calling from {institution}."
    else:
        greet = "Hello."
    first_question = ""
    flow = config.get("question_flow") if isinstance(config, Mapping) else []
    if isinstance(flow, list):
        for item in flow:
            text_value = apply_token_substitution(_question_text(item), tok)
            if text_value:
                first_question = text_value
                break
    opening = f"{disclosure} {greet}"
    if first_question:
        opening += f" {first_question}"
    return scrub_speech_text(opening)
```

- [ ] **Step 4: Run tests to verify they pass, plus existing voice prompt suites**

Run (workdir `voice-agent/`): `.\.venv\Scripts\python.exe -m pytest tests/test_opening_line.py tests/test_token_substitution.py tests/test_prompt_render.py tests/test_call_context.py -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add voice-agent/app/prompting.py voice-agent/tests/test_opening_line.py voice-agent/tests/test_token_substitution.py
git commit -m "feat: voice token aliases and deterministic opening line builder"
```

---

### Task 5: Speak the protected opening in the voice session

**Files:**
- Modify: `voice-agent/app/pipeline.py` (import `build_opening_line`; add `_speak_opening`; call after `session.start`)
- Test: extend `voice-agent/tests/test_opening_line.py` (fake-session test of `_speak_opening`)

**Interfaces:**
- Consumes: Task 4 (`build_opening_line`, `build_token_map`).
- Produces: `_speak_opening(session: Any, config: Mapping[str, Any], tokens: Mapping[str, str], contact: Optional[Mapping[str, Any]]) -> bool` — async; `True` when the opening was spoken.

- [ ] **Step 1: Write the failing test**

Append to `voice-agent/tests/test_opening_line.py`:

```python
import pytest

from app import pipeline as pipeline_module


class _FakeSession:
    def __init__(self) -> None:
        self.said: list[tuple[str, bool]] = []

    async def say(self, text: str, allow_interruptions: bool = True) -> None:
        self.said.append((text, allow_interruptions))


@pytest.mark.asyncio
async def test_speak_opening_protected_and_first() -> None:
    session = _FakeSession()
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"}
    tokens = build_token_map(contact=contact, context={"institution_name": "Demo School"})
    spoken = await pipeline_module._speak_opening(session, CONFIG, tokens, contact)
    assert spoken is True
    assert len(session.said) == 1
    text, allow_interruptions = session.said[0]
    assert allow_interruptions is False
    assert text.startswith("Hi, this is an AI assistant calling from Demo School.")
    assert "Suresh Kumar" in text and "Aarav Kumar" in text
    assert "[" not in text and "]" not in text


@pytest.mark.asyncio
async def test_speak_opening_skips_without_disclosure() -> None:
    session = _FakeSession()
    spoken = await pipeline_module._speak_opening(session, {"question_flow": []}, {}, {})
    assert spoken is False
    assert session.said == []
```

Check first whether `pytest-asyncio` (or anyio) is available in the voice-agent venv: the existing voice-agent tests are sync. If no async plugin is installed, write the test with `asyncio.run(...)` instead of the marker:

```python
import asyncio
...
def test_speak_opening_protected_and_first() -> None:
    ...
    spoken = asyncio.run(pipeline_module._speak_opening(session, CONFIG, tokens, contact))
```

Use whichever the venv supports — check with `.\.venv\Scripts\python.exe -c "import pytest_asyncio"` (or `anyio`); if the import fails, use the `asyncio.run` form. (Do not add new test dependencies in P1.)

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `voice-agent/`): `.\.venv\Scripts\python.exe -m pytest tests/test_opening_line.py -q`
Expected: FAIL with `AttributeError: module 'app.pipeline' has no attribute '_speak_opening'`.

- [ ] **Step 3: Write minimal implementation**

(a) Extend the prompting import in `pipeline.py` (find the line importing `render_system_prompt`, `build_token_map` — used at lines 674-678) to include `build_opening_line`. It reads (verify exact names at edit time; the shape is):

```python
from app.prompting import LOW_CONFIDENCE_THRESHOLD, build_opening_line, build_token_map, render_system_prompt
```

Keep every previously imported name; only add `build_opening_line`.

(b) Add the helper just before `run_session` (before line 608):

```python
async def _speak_opening(
    session: Any,
    config: Mapping[str, Any],
    tokens: Mapping[str, str],
    contact: Optional[Mapping[str, Any]],
) -> bool:
    """Speak the composed opening with interruptions disabled.

    Returns True when spoken; False (fall back to the prompt-driven
    auto-turn) when there is no disclosure script to anchor it.
    """
    opening = build_opening_line(config, tokens, contact)
    if not opening:
        return False
    await session.say(opening, allow_interruptions=False)
    return True
```

`Any`, `Mapping`, `Optional` are already imported in `pipeline.py` (verify at edit time; add to the typing import if missing).

(c) Wire it after `session.start` (line 727):

```python
        agent = DomainCallAgent(instructions=instructions, tools_impl=tools_impl)
        await session.start(room=ctx.room, agent=agent)
        # Agent speaks first: the composed opening cannot be barged by
        # background noise, and names are real (token-substituted).
        await _speak_opening(
            session,
            config,
            build_token_map(contact=parsed.contact, context=call_context),
            parsed.contact,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `voice-agent/`): `.\.venv\Scripts\python.exe -m pytest tests/test_opening_line.py -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add voice-agent/app/pipeline.py voice-agent/tests/test_opening_line.py
git commit -m "feat: voice session speaks protected opening first"
```

---

### Task 6: Real-estate lead-qualification preset

**Files:**
- Create: `domain-configs/presets/real-estate-lead-qualification.json`
- Modify: `backend/tests/test_agents.py` (preset-id assertion set)

**Interfaces:**
- Consumes: `validate_agent_version_payload` (already enforced by `GET /api/agents/presets`).
- Produces: the preset file, served automatically by the presets endpoint (no code change).

- [ ] **Step 1: Write the failing test**

Edit `backend/tests/test_agents.py` line 56-57 — extend the expected set:

```python
    assert {"lead-verification", "appointment-confirmation", "feedback-survey",
            "absent-student-followup", "real-estate-lead-qualification"} <= ids
```

And after the per-preset loop (find where the loop over `presets` ends — extend with a targeted check; insert right after the loop):

```python
def test_real_estate_preset_has_qualification_schema(client):
    token, _user = register(client)
    presets = client.get("/api/agents/presets", headers=auth_headers(token)).json()
    payload = next(p for p in presets if p["preset_id"] == "real-estate-lead-qualification")["version_payload"]
    assert set(payload["extraction_schema"]) >= {
        "interest_level", "budget_band", "locality_preference",
        "possession_timeline", "visit_date_preference", "call_outcome",
        "escalation_needed",
    }
    assert len(payload["question_flow"]) == 5
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_agents.py -q`
Expected: FAIL — `real-estate-lead-qualification` missing from preset ids.

- [ ] **Step 3: Write the preset file**

Create `domain-configs/presets/real-estate-lead-qualification.json`, mirroring `lead-verification.json` field-for-field (same keys, same threshold style). Use `[Company Name]` / `[Lead Name]` / `[Agent Name]` tokens — all covered by the Task 1/4 maps:

```json
{
  "preset_id": "real-estate-lead-qualification",
  "name": "Real-Estate Lead Qualification Agent",
  "description": "Calls people who enquired about a property, confirms genuine interest, qualifies budget/locality/timeline, and books the next step (site visit or call-back).",
  "version_payload": {
    "system_prompt": "# ROLE\nYou are a lead qualification agent for [Company Name], a real-estate brokerage. You call people who recently enquired about a property (website form, listing, or referral).\n\n# OBJECTIVE\nConfirm the person is genuinely interested, understand their requirement (budget band, preferred locality, possession timeline), and agree a concrete next step: a site visit or a call-back. Your job is qualification, NOT closing the sale.\n\n# PERSONA & TONE\nWarm, professional, unhurried. The whole call should take 2-3 minutes. Never pushy, never argue.\n\n# OPENING\n\"Hi [Lead Name], this is [Agent Name] calling from [Company Name] regarding the property enquiry you submitted recently. Do you have a couple of minutes?\"\n\n# THINGS TO FIND OUT\n1. Confirm they actually made the enquiry (if not, apologise politely and end the call).\n2. Confirm their interest in the property type is still current.\n3. Understand the requirement: budget band, preferred locality, possession timeline.\n4. Agree the next step: site visit date or a better time to call back.\n\n# ANSWERING PROPERTY QUESTIONS\nAnswer only basic property questions whose facts are in your company knowledge (size, price band, amenities, location). If a fact is not in your knowledge, say you will have a specialist confirm it — never quote a number you were not given.\n\n# OBJECTIONS & FAQ\n- \"I never enquired.\" -> Apologise sincerely, mention the enquiry source if you have it, and end the call politely. Flag the lead as invalid.\n- \"Just send me the details on WhatsApp.\" -> Offer to have the team send details after this quick qualification.\n- \"I'm busy right now.\" -> Ask for a better time, note it, thank them, and end the call.\n- \"How did you get my number?\" -> \"You shared it in the enquiry you submitted.\"\n\n# DO NOT\n- Never quote prices, offers, or possession dates beyond your company knowledge.\n- Never share other people's information.\n- Never continue the call if the person says they are not interested - thank them and end it.",
    "company_context": {"company_name": "[Company Name]", "price_bands": "[Price bands served]", "areas_served": "[Areas served]", "sample_listing_facts": "[Size / price band / amenities of the featured property]"},
    "question_flow": [
      {"step": 1, "question": "Did you recently enquire about a property with [Company Name]?"},
      {"step": 2, "question": "Are you still looking to buy?"},
      {"step": 3, "question": "What budget band and locality are you considering?"},
      {"step": 4, "question": "By when are you hoping to take possession?"},
      {"step": 5, "question": "Would you like to schedule a site visit, or should I call back at a better time?"}
    ],
    "extraction_schema": {
      "interest_level": {"type": "string", "description": "Lead interest: hot, warm, cold, or not_interested.", "validation": "required", "confidence_threshold": 0.8},
      "budget_band": {"type": "string", "description": "Budget band exactly as the lead stated it.", "validation": "required", "confidence_threshold": 0.8},
      "locality_preference": {"type": "string", "description": "Preferred locality or area.", "validation": "required", "confidence_threshold": 0.8},
      "possession_timeline": {"type": "string", "description": "When the lead hopes to take possession.", "validation": "optional", "confidence_threshold": 0.7},
      "visit_date_preference": {"type": "string", "description": "Preferred site-visit date/time, if offered.", "validation": "optional", "confidence_threshold": 0.7},
      "call_outcome": {"type": "string", "description": "Outcome: qualified, callback_requested, not_interested, or invalid_lead.", "validation": "required", "confidence_threshold": 0.8},
      "escalation_needed": {"type": "boolean", "description": "True when a human must review (abuse, legal question, contradiction).", "validation": "optional", "confidence_threshold": 0.9}
    },
    "disclosure_script": "Hello, this is [Agent Name] calling from [Company Name]. I am an AI voice assistant calling about your property enquiry. This call is recorded for quality purposes.",
    "escalation_rules": [
      {"trigger": "Caller asks a detailed pricing, legal, or availability question.", "action": "flag"},
      {"trigger": "Caller requests to opt out of all calls.", "action": "end_call"},
      {"trigger": "Caller is angry or abusive.", "action": "end_call"},
      {"trigger": "Caller asks to speak with a human representative.", "action": "flag"}
    ],
    "voice_settings": {"language": "en", "stt_language": "en", "speaking_rate": 1.0, "llm_model": "", "tts_voice_id": "", "voices_by_language": {"en": ""}}
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_agents.py -q`
Expected: all pass (the presets endpoint validates the new payload via `validate_agent_version_payload` — a malformed file fails here, not silently).

- [ ] **Step 5: Commit**

```bash
git add domain-configs/presets/real-estate-lead-qualification.json backend/tests/test_agents.py
git commit -m "feat: real-estate lead-qualification preset"
```

---

### Task 7: Turn-core extraction + dry-run personas

**Files:**
- Modify: `backend/app/routers/playground.py` (extract `_run_agent_turn` from `create_turn`; endpoint keeps auth/checks and delegates)
- Create: `backend/app/services/dry_run.py` (`PERSONAS`, `PERSONA_ORDER`, `persona_reply`, `validate_persona`)
- Test: `backend/tests/test_dry_run.py` (persona unit tests; refactor regression runs the existing suites)

**Interfaces:**
- Consumes: Task 2 (`_render_text_system_prompt` with new signature — the extracted helper calls it the same way `create_turn` does today).
- Produces: `_run_agent_turn(db: Session, settings: Settings, call: Call, version: AgentVersion, *, user_text: str, start_event: bool) -> dict[str, Any]` returning `{"reply_text", "done", "extracted_fields", "turn_index"}`; `persona_reply(persona_name: str, agent_text: str, turn_no: int, contact: dict[str, str]) -> Optional[str]`; `PERSONA_ORDER: tuple[str, ...]` — used by Task 8's runner.

- [ ] **Step 1: Write the failing test (personas)**

```python
"""Dry-run personas: scripted callers behind the text-mode campaign dry-run."""
from __future__ import annotations

import pytest

from app.services.dry_run import PERSONA_ORDER, persona_reply, validate_persona


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
```

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_dry_run.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.dry_run'`.

- [ ] **Step 3: Write minimal implementation**

(a) Create `backend/app/services/dry_run.py`:

```python
"""Scripted caller personas for the text-mode campaign dry-run.

Personas are positional scripts: reply N answers the agent's Nth utterance.
They deliberately do NOT track conversation state — the point is stressing
the agent's confirmation loop, extraction precision, and wind-down behavior,
not passing a Turing test. ``None`` means the persona has nothing left to
say (runner stops the simulation for that lead).
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

PERSONA_ORDER: tuple[str, ...] = ("cooperative", "terse", "distracted", "refuses", "clueless")

_PERSONA_SCRIPTS: dict[str, list[str]] = {
    "cooperative": [
        "Yes, speaking.",
        "He has had fever since yesterday.",
        "He should be back on Monday.",
        "Yes, I can submit the medical certificate tomorrow.",
        "Thank you, goodbye.",
    ],
    "terse": ["Yes.", "Fever.", "Monday.", "Yes.", "Bye."],
    "distracted": [
        "Yes, speaking — sorry, the TV is loud, one second.",
        "Fever since yesterday. Ask my wife if you need the exact time, she tracks all that.",
        "Monday, I think. Unless the doctor says rest longer, then Tuesday maybe.",
        "Yes, certificate tomorrow. Anyway the traffic today was terrible.",
        "Okay bye now.",
    ],
    "refuses": [
        "I don't want to talk about this, please don't call again.",
        "Please remove our number. Goodbye.",
    ],
    "clueless": [
        "I don't know.",
        "Not sure, you'd have to ask someone else.",
        "I really couldn't say.",
        "No idea. Is there anything else?",
    ],
}


def validate_persona(name: str) -> str:
    """Return the persona name or raise ValueError for unknown names."""
    if name not in _PERSONA_SCRIPTS:
        raise ValueError(f"unknown dry-run persona: {name!r}")
    return name


def persona_reply(
    persona_name: str,
    agent_text: str,
    turn_no: int,
    contact: Mapping[str, Any],
) -> Optional[str]:
    """Next scripted caller line, or None when the persona is done."""
    script = _PERSONA_SCRIPTS[validate_persona(persona_name)]
    if turn_no < 0 or turn_no >= len(script):
        return None
    return script[turn_no]
```

(`agent_text` and `contact` are accepted so later tasks can make personas reactive without changing the signature.)

(b) Extract `_run_agent_turn` in `backend/app/routers/playground.py`. Move the body of `create_turn` from the `system_prompt = _render_text_system_prompt(...)` line (line 649) through the `return {...}` (line 769-774) into:

```python
async def _run_agent_turn(
    db: Session,
    settings: Settings,
    call: Call,
    version: AgentVersion,
    *,
    user_text: str,
    start_event: bool,
) -> dict[str, Any]:
    """One text-mode agent turn: build prompt, call Groq, run tools, persist.

    Shared by the HTTP turns endpoint and the campaign dry-run runner so
    simulated calls go through byte-identical conversation logic.
    """
    <moved body, with `call`, `version`, `user_text`, `start_event` as params>
```

And shrink `create_turn` to the checks plus delegation:

```python
    call = _get_own_playground_call(db, call_id, user)  # 404 unless own playground row
    if call.status != "in_progress":
        raise HTTPException(status_code=409, detail="This session has already ended.")
    version = db.get(AgentVersion, call.agent_version_id) if call.agent_version_id else None
    if version is None:
        raise HTTPException(status_code=409, detail="Session has no agent version configured.")

    start_event = payload.event == "start"
    user_text = "" if start_event else payload.text.strip()
    if not start_event and not user_text:
        raise HTTPException(status_code=422, detail="'text' must not be empty.")

    return await _run_agent_turn(
        db, settings, call, version, user_text=user_text, start_event=start_event
    )
```

The moved body keeps everything else identical, including the institution lookup from Task 2 (it lives where `system_prompt` is built). No behavior change — existing `test_playground_text.py` is the regression net.

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_dry_run.py tests/test_playground_text.py tests/test_playground.py tests/test_playground_contact.py -q`
Expected: all pass (persona unit tests + zero regressions from the extraction).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routers/playground.py backend/app/services/dry_run.py backend/tests/test_dry_run.py
git commit -m "feat: extract text-turn core and add dry-run caller personas"
```

---

### Task 8: Dry-run runner + endpoint + schemas

**Files:**
- Modify: `backend/app/schemas.py` (dry-run models), `backend/app/routers/playground.py` (endpoint), `backend/app/services/dry_run.py` (runner + mask)
- Test: extend `backend/tests/test_dry_run.py` (runner integration with scripted Groq)

**Interfaces:**
- Consumes: Task 2/7 (`_run_agent_turn`, `_clean_contact`), Task 3 (nothing new), existing `complete_session` shape for the report.
- Produces: `POST /api/playground/campaigns/{campaign_id}/dry-run`; `run_campaign_dry_run(...) -> dict[str, Any]`; `_mask_phone(phone: str) -> str` — used by Task 9's UI (via HTTP only).

- [ ] **Step 1: Confirm the `calls.kind` column accepts a new value**

Run (workdir repo root): `grep -rn "CheckConstraint\|check=" backend/app/models.py | Select-String "kind"` — PowerShell: `Select-String -Path backend\app\models.py -Pattern "kind"`.

Expected: the `kind` column is a plain `String` with no CHECK constraint (statuses are enforced in code, kinds are `"phone"`/`"playground"` by convention), so persisting `kind="dry-run"` rows needs no migration. If a constraint exists, extend it in this task before proceeding.

- [ ] **Step 2: Write the failing test**

Append to `backend/tests/test_dry_run.py`:

```python
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
```

With module helpers in the same test file (place before the tests):

```python
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
```

Imports needed at the top of the new test code: `from sqlalchemy import select`; `from conftest import auth_headers, register`. (`groq_client`, `script`, `chat`, `tool_call` are imported from `test_playground_text` — same directory, importable: `from test_playground_text import chat, groq_client, script, tool_call`. Note: importing the `groq_client` fixture works in pytest.)

Script accounting for the test above: contact 1 consumes 4 scripted replies (opening chat, tool record, follow-up chat, end_call tool — the end_call fires inside the same `_run_agent_turn` round loop, then the loop's final forced-text call... trace carefully: turn 0 (start): round 1 chat → no tools → reply "Hello...". Persona reply 1 → turn 1: round 1 tool record → round 2 chat "Thanks..." → reply. Persona reply 2 → turn 2: round 1 end_call tool → done → round 2 forced text? After end_call, loop continues: `done=True`, next round calls `_groq_chat` again (round 2 < 3) → consumes the 4th scripted message... wait no.

Re-trace `_run_agent_turn` with the script [chat(Hello), tool(record), chat(Thanks), tool(end_call), chat(Hello2), tool(end_call2)]:
- Turn 0 start: round0 → chat(Hello) no tools → reply Hello. Consumed 1.
- Persona[1] → turn 1: round0 → tool(record) → execute → round1 → chat(Thanks) no tools → reply Thanks. Consumed 2 (total 3).
- Persona[2] → turn 2: round0 → tool(end_call) → done → round1 → needs another Groq call → consumes chat(Hello2)?? That's wrong — Hello2 was meant for contact 2.

Fix the script: after end_call the loop still calls Groq once more (round1 < _MAX_TOOL_ROUNDS-1=2, so include_tools=True). Hmm: `for round_no in range(3): message = await _groq_chat(... include_tools=round_no < 2)`. After end_call at round0, round1 calls Groq again and consumes a scripted reply. In real usage that's a live call; in the test it eats the next scripted message. To keep the test deterministic, add a spare chat message after each end_call: script = [chat(H0), tool(rec), chat(T), tool(end), chat(spare1), chat(H2), tool(end2), chat(spare2)]. Turn 2 round1 consumes spare1 (assistant text discarded? No — `assistant_text` gets overwritten: round1 returns chat(spare1) with no tools → assistant_text = spare1, break. So the persisted agent reply for turn 2 is spare1, not empty. Fine — the test only asserts fields/status/transcript length, not exact reply text. And donor: contact 2 start consumes chat(H2)... wait after contact 1's runner loop ends (done=True → break), contact 2 starts fresh: turn 0 consumes chat(H2) → reply. Persona[0]="Yes, speaking." → turn 1: tool(end2) → done → round1 consumes spare2. 

So script order: chat(H0), tool(rec), chat(T), tool(end), chat(spare1), chat(H2), tool(end2), chat(spare2). Update the test's script() call accordingly (8 entries). The runner must stop the per-contact loop when `done` is True (it will, after turn 2 for contact 1 and turn 1 for contact 2 — total Groq calls: 1+2+3? no: contact1: turn0(1 call) + turn1(2 calls) + turn2(2 calls) = 5; contact2: turn0(1) + turn1(2) = 3; total 8 scripted. Matches.)

- [ ] **Step 3: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_dry_run.py -q`
Expected: FAIL — `POST .../dry-run` returns 404 (no such route; `validate_persona` test for "sarcastic" expects 422 from the endpoint — currently 404).

- [ ] **Step 4: Write minimal implementation**

(a) `backend/app/schemas.py` — append:

```python
# --- campaign dry-run (text-mode simulation) ---------------------------------


class DryRunCreate(BaseModel):
    persona: Optional[str] = None  # one of dry_run.PERSONA_ORDER; None = round-robin
    contact_limit: int = Field(default=20, gt=0, le=100)


class DryRunTranscriptTurn(BaseModel):
    role: str
    text: str


class DryRunContactResult(BaseModel):
    contact_id: int
    name: str
    phone: str  # masked
    persona: str
    transcript: list[DryRunTranscriptTurn]
    extracted_fields: list[dict[str, Any]]
    status: str
    outcome: Optional[str] = None
    turns: int


class DryRunReport(BaseModel):
    campaign_id: int
    persona: Optional[str] = None
    contacts_total: int
    contacts_run: int
    results: list[DryRunContactResult]
```

Check `schemas.py` imports `Field`, `Optional`, `Any` — `Field` is used elsewhere? `TestCallRequest` uses `Optional` (line 243-249) so `Optional`/`Any` are imported. Verify `Field` import at edit time; add if missing.

(b) `backend/app/services/dry_run.py` — append runner:

```python
_MAX_DRY_RUN_TURNS = 6


def _mask_phone(phone: str) -> str:
    text = str(phone or "")
    if len(text) <= 4:
        return "****"
    return f"{text[:4]}****{text[-2:]}"


def _contact_card(contact: Any) -> dict[str, str]:
    card: dict[str, str] = {}
    for key, value in ((contact.custom_fields or {}) if contact else {}).items():
        name = str(key).strip()
        if not name or isinstance(value, (dict, list)):
            continue
        text = str(value).strip()
        if text:
            card[name] = text
    return card


async def run_campaign_dry_run(
    db: Any,
    settings: Any,
    run_turn: Any,
    *,
    campaign: Any,
    version: Any,
    contacts: list[Any],
    persona_names: list[str],
) -> dict[str, Any]:
    """Simulate one text-mode call per contact against scripted personas.

    Persists each simulation as a ``Call(kind="dry-run")`` so transcripts and
    fields stay inspectable through the existing call-detail path. ``run_turn``
    is ``_run_agent_turn`` injected for testability.
    """
    from app.models import Call, ExtractedField, Transcript  # local: avoids import cycles

    results: list[dict[str, Any]] = []
    for index, contact in enumerate(contacts):
        persona = persona_names[index % len(persona_names)]
        card = _contact_card(contact)
        call = Call(
            kind="dry-run",
            status="in_progress",
            org_id=campaign.org_id,
            campaign_id=campaign.id,
            contact_id=contact.id,
            agent_version_id=version.id,
            started_at=utcnow(),
            context={"contact": card} if card else None,
        )
        db.add(call)
        db.flush()

        turns_used = 0
        reply = await run_turn(db, settings, call, version, user_text="", start_event=True)
        turns_used += 1
        while not reply.get("done") and turns_used < _MAX_DRY_RUN_TURNS:
            caller_line = persona_reply(persona, reply.get("reply_text") or "", turns_used, card)
            if not (caller_line or "").strip():
                break
            reply = await run_turn(db, settings, call, version, user_text=caller_line, start_event=False)
            turns_used += 1
        if call.status == "in_progress":
            call.status = "completed"
            call.ended_at = utcnow()
        db.commit()

        rows = db.scalars(
            select(Transcript).where(Transcript.call_id == call.id).order_by(Transcript.turn_index)
        ).all()
        fields = db.scalars(
            select(ExtractedField).where(ExtractedField.call_id == call.id).order_by(ExtractedField.id)
        ).all()
        results.append(
            {
                "contact_id": contact.id,
                "name": contact.name,
                "phone": _mask_phone(contact.phone),
                "persona": persona,
                "transcript": [
                    {"role": ("agent" if r.speaker == "agent" else "caller"), "text": r.text}
                    for r in rows
                ],
                "extracted_fields": [
                    {"field_name": f.field_name, "field_value": f.field_value, "confidence": f.confidence}
                    for f in fields
                ],
                "status": call.status,
                "outcome": call.outcome,
                "turns": turns_used,
            }
        )
    return {"results": results}
```

Required imports in `dry_run.py`: `select` (sqlalchemy), `utcnow` (app.timeutil). `turns_used` counts *agent turns*, matching the persona script index (`turns_used` after the opening is 1 → persona script[1]... wait: opening turn consumes no persona line; first persona line used is script[1]? Trace: turn 0 start → turns_used=1 → loop: persona_reply(persona, reply, 1, card) → script[1]. So script[0] ("Yes, speaking.") is NEVER used. Fix: pass `turns_used - 1`... but then turn index 0 = opening agent text → persona replies script[0]. Yes: `persona_reply(persona, ..., turns_used - 1, card)`. Update the call accordingly. (The unit tests in Task 7 call persona_reply directly with explicit indices — unaffected.)

Hmm wait, also persona "refuses" test asserted `persona_reply("refuses", ..., 5, {}) is None` — script len 2, index 5 → None. Good.

(c) `backend/app/routers/playground.py` — append the endpoint (after `create_turn`, end of file):

```python
@router.post("/campaigns/{campaign_id}/dry-run")
async def dry_run_campaign(
    campaign_id: int,
    payload: DryRunCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """SIMULATION ONLY: run campaign contacts through text-mode turns.

    No telephony, no dialer. Each contact gets a scripted caller persona and
    a persisted ``Call(kind="dry-run")`` for inspection via call detail.
    """
    from app.services.dry_run import PERSONA_ORDER, run_campaign_dry_run, validate_persona

    settings: Settings = request.app.state.settings
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=503,
            detail="Text mode needs GROQ_API_KEY configured on the backend.",
        )
    campaign = db.get(Campaign, campaign_id)
    if campaign is None or campaign.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="not found")
    version = None
    if campaign.agent_version_id:
        version = db.get(AgentVersion, campaign.agent_version_id)
    if version is None:
        version = db.scalar(
            select(AgentVersion)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(Agent.org_id == user.org_id)
            .order_by(AgentVersion.id.desc())
        )
    if version is None:
        raise HTTPException(status_code=422, detail="no agent versions in org")
    if payload.persona is not None:
        try:
            persona_names = [validate_persona(payload.persona)]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    else:
        persona_names = list(PERSONA_ORDER)
    contacts = list(
        db.scalars(
            select(Contact)
            .where(
                Contact.campaign_id == campaign.id,
                Contact.status.in_(["queued", "pending_review"]),
            )
            .order_by(Contact.id)
            .limit(payload.contact_limit)
        ).all()
    )
    report = await run_campaign_dry_run(
        db, settings, _run_agent_turn,
        campaign=campaign, version=version,
        contacts=contacts, persona_names=persona_names,
    )
    return {
        "campaign_id": campaign.id,
        "persona": payload.persona,
        "contacts_total": len(contacts),
        "contacts_run": len(report["results"]),
        "results": report["results"],
    }
```

Imports: `DryRunCreate` from `app.schemas` (playground.py currently imports no schemas — add `from app.schemas import DryRunCreate`). `Campaign`/`Contact` already imported via Task 2's import change. `select` already imported (line 25). Route-ordering caution: `/campaigns/{campaign_id}/dry-run` vs `/sessions/{call_id}/...` — distinct prefixes, no conflict.

- [ ] **Step 5: Run tests to verify they pass**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_dry_run.py -q`
Expected: all pass. Then regression: `.\.venv\Scripts\python.exe -m pytest tests -q` (full backend suite).

- [ ] **Step 6: Commit**

```bash
git add backend/app/schemas.py backend/app/routers/playground.py backend/app/services/dry_run.py backend/tests/test_dry_run.py
git commit -m "feat: text-mode campaign dry-run endpoint with scripted personas"
```

---

### Task 9: Lead-card form + contact-aware Playground/TestCall UI

**Files:**
- Modify: `frontend/src/api.js` (`startSession` accepts contact; add `runDryRun`), `frontend/src/pages/PlaygroundPage.jsx` (lead-card state + setup section + pass-through), `frontend/src/components/TextPlayground.jsx` (pass-through), `frontend/src/pages/TestCallPage.jsx` (agent/version pickers + lead card)
- Create: `frontend/src/components/LeadCardForm.jsx`

**Interfaces:**
- Consumes: Task 8's endpoint (only `runDryRun` added here; UI use in Task 10).
- Produces: `LeadCardForm` (`{value, onChange, defaults}` props); contact-aware session/test-call flows.

- [ ] **Step 1: Read the two exact insertion areas**

Read `frontend/src/pages/PlaygroundPage.jsx` lines 700-800 (setup phase: agent/version picker state names) and `frontend/src/components/TextPlayground.jsx` lines 1-110 (session start + turn loop). Record the state variable names (`selectedVersionId`, phase constants) for the edits below.

- [ ] **Step 2: Extend the API surface**

Edit `frontend/src/api.js` lines 159-172:

```javascript
export const playgroundApi = {
  startSession: (agentVersionId, contact) =>
    apiFetch('/api/playground/sessions', {
      method: 'POST',
      body: JSON.stringify(
        contact && Object.keys(contact).length
          ? { agent_version_id: agentVersionId, contact }
          : { agent_version_id: agentVersionId }
      ),
    }),
  completeSession: (callId) => apiFetch(`/api/playground/sessions/${callId}/complete`, { method: 'POST' }),
  // Text mode: one conversational turn (or {event:'start'} for the opening line).
  sendTurn: (callId, body) =>
    apiFetch(`/api/playground/sessions/${callId}/turns`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  // SIMULATION ONLY: run campaign contacts through text-mode turns. No telephony.
  runDryRun: (campaignId, body) =>
    apiFetch(`/api/playground/campaigns/${campaignId}/dry-run`, {
      method: 'POST',
      body: JSON.stringify(body || {}),
    }),
};
```

No test runner — verification is the production build in Step 6.

- [ ] **Step 3: Create the shared lead-card form**

Create `frontend/src/components/LeadCardForm.jsx`:

```jsx
import React from 'react';

export const ABSENT_STUDENT_DEFAULTS = {
  student_name: '',
  parent_name: '',
  class_section: '',
  absent_date: '',
};

/** Generic key/value lead card ("who are we calling?").
 * Props: {value: object, onChange: (next) => void, defaults?: object}
 */
export default function LeadCardForm({ value, onChange, defaults }) {
  const rows = Object.entries(value || {});
  const set = (next) => onChange(next);

  function updateRow(index, key, val) {
    const entries = Object.entries(value || {});
    entries[index] = [key, val];
    const next = {};
    for (const [k, v] of entries) {
      if (String(k).trim()) next[String(k).trim()] = v;
    }
    set(next);
  }

  function removeRow(index) {
    const entries = Object.entries(value || {});
    entries.splice(index, 1);
    set(Object.fromEntries(entries));
  }

  function addRow() {
    set({ ...(value || {}), [`field_${rows.length + 1}`]: '' });
  }

  function loadDefaults() {
    set({ ...(defaults || {}) });
  }

  return (
    <div className="lead-card">
      {rows.map(([k, v], i) => (
        <div className="form-row" key={i}>
          <input
            aria-label="Field name"
            value={k}
            placeholder="field name"
            onChange={(e) => updateRow(i, e.target.value, v)}
          />
          <input
            aria-label="Field value"
            value={v}
            placeholder="value"
            onChange={(e) => updateRow(i, k, e.target.value)}
          />
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => removeRow(i)}>
            Remove
          </button>
        </div>
      ))}
      <div className="form-actions">
        <button type="button" className="btn btn-secondary btn-sm" onClick={addRow}>
          Add field
        </button>
        {defaults && (
          <button type="button" className="btn btn-secondary btn-sm" onClick={loadDefaults}>
            Reset defaults
          </button>
        )}
      </div>
      <p className="hint">Only non-empty values are sent. The agent uses these names instead of asking who it is calling.</p>
    </div>
  );
}
```

Use existing CSS classes only (`form-row`? verify at edit time — the codebase uses `field`, `form-actions`, `btn`, `hint`. If `form-row` does not exist in styles.css, use `field` divs instead. Check with a grep for `form-row` in `frontend/src/styles.css` before writing; fall back to `field`.)

- [ ] **Step 4: Wire the Playground (voice + text)**

In `frontend/src/pages/PlaygroundPage.jsx`:
1. Import: `import LeadCardForm, { ABSENT_STUDENT_DEFAULTS } from '../components/LeadCardForm.jsx';`
2. Add state near `selectedVersionId`: `const [contactCard, setContactCard] = useState({ ...ABSENT_STUDENT_DEFAULTS });`
3. In the SETUP-phase JSX (near the agent/version pickers found in Step 1), add a collapsible section:

```jsx
<details className="card" open>
  <summary>Who are we calling? (optional lead card)</summary>
  <LeadCardForm value={contactCard} onChange={setContactCard} defaults={ABSENT_STUDENT_DEFAULTS} />
</details>
```

4. Line 335: `sess = await playgroundApi.startSession(Number(selectedVersionId));` →

```javascript
      sess = await playgroundApi.startSession(Number(selectedVersionId), contactCard);
```

In `frontend/src/components/TextPlayground.jsx` (line 56 area):
1. Same import; add `contactCard` state initialized from `ABSENT_STUDENT_DEFAULTS`; render the same `<details>` block above the chat UI.
2. Line 56: `const sess = await playgroundApi.startSession(Number(versionId));` →

```javascript
        const sess = await playgroundApi.startSession(Number(versionId), contactCard);
```

(Adjust variable naming to the file's actual locals found in Step 1.)

- [ ] **Step 5: Make TestCall version- and contact-aware**

Rewrite the state + payload parts of `frontend/src/pages/TestCallPage.jsx` (keep the result banner and styling):

```jsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { agentsApi, api } from '../api.js';
import LeadCardForm, { ABSENT_STUDENT_DEFAULTS } from '../components/LeadCardForm.jsx';
import StatusBadge from '../components/StatusBadge.jsx';

export default function TestCallPage() {
  const [domains, setDomains] = useState([]);
  const [domainsError, setDomainsError] = useState(null);
  const [domainId, setDomainId] = useState('');
  const [agents, setAgents] = useState([]);
  const [agentId, setAgentId] = useState('');
  const [versions, setVersions] = useState([]);
  const [versionId, setVersionId] = useState('');
  const [contactCard, setContactCard] = useState({ ...ABSENT_STUDENT_DEFAULTS });
  const [to, setTo] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [placedWith, setPlacedWith] = useState(null);

  useEffect(() => {
    api.listDomainConfigs().then((list) => {
      setDomains(Array.isArray(list) ? list : []);
      setDomainsError(null);
    }).catch((e) => setDomainsError(e.message));
    agentsApi.list().then((list) => {
      setAgents(Array.isArray(list) ? list : []);
    }).catch(() => setAgents([]));
  }, []);

  useEffect(() => {
    if (!agentId) {
      setVersions([]);
      setVersionId('');
      return;
    }
    agentsApi.listVersions(agentId).then((list) => {
      const arr = Array.isArray(list) ? list : [];
      setVersions(arr);
      setVersionId(arr.length ? String(arr[arr.length - 1].id) : '');
    }).catch(() => {
      setVersions([]);
      setVersionId('');
    });
  }, [agentId]);

  async function placeCall() {
    setBusy(true);
    setError(null);
    setResult(null);
    const payload = {};
    if (domainId) payload.domain_config_id = Number(domainId);
    if (versionId) payload.agent_version_id = Number(versionId);
    const card = Object.fromEntries(
      Object.entries(contactCard || {}).filter(([, v]) => String(v || '').trim())
    );
    if (Object.keys(card).length) payload.contact = card;
    const trimmed = to.trim();
    if (trimmed) payload.to = trimmed;
    try {
      const res = await api.placeTestCall(payload);
      setResult(res || {});
      setPlacedWith(versionId ? `agent version ${versionId}` : 'latest agent version');
    } catch (e) {
      setError(e.message || 'Could not place test call.');
    } finally {
      setBusy(false);
    }
  }
  // ... keep the existing JSX, with these changes:
  // - domain select label becomes "Call domain (optional — derived from the agent version when blank)"
  //   and the Place button requires (domainId || versionId)
  // - add agent select + version select fields after the domain field
  // - add the LeadCardForm <details> block before the destination field
  // - result banner shows "Placed with {placedWith}."
}
```

Verify `agentsApi.list` and `agentsApi.listVersions` exist in `api.js` (lines 150-157: yes — `list`, `listVersions`). Verify the versions list response shape (`[{id, ...}]`) at edit time via `agentsApi.listVersions` consumer `AgentDetailPage.jsx` if needed.

- [ ] **Step 6: Verify with the production build**

Run (workdir `frontend/`): `npm run build`
Expected: `vite build` completes with no errors (`✓ built in ...`).

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api.js frontend/src/components/LeadCardForm.jsx frontend/src/components/TextPlayground.jsx frontend/src/pages/PlaygroundPage.jsx frontend/src/pages/TestCallPage.jsx
git commit -m "feat: contact-aware playground and test-call UI"
```

---

### Task 10: Campaign dry-run UI + exit gates + full verification

**Files:**
- Create: `frontend/src/components/DryRunReport.jsx`, `docs/superpowers/evaluations/p2-exit-gates.md`
- Modify: `frontend/src/pages/CampaignDetailPage.jsx` (SIMULATION panel)
- Verify: full backend suite, full voice-agent suite, frontend build

**Interfaces:**
- Consumes: Task 8's endpoint (via `playgroundApi.runDryRun`), Task 9's patterns.
- Produces: nothing downstream — this task closes P1. Note one deliberate spec deviation: dry-run export is a client-side CSV download from the report JSON (server-side XLSX waits for persisted reports, spec §9 stretch).

- [ ] **Step 1: Create the report component**

Create `frontend/src/components/DryRunReport.jsx`:

```jsx
import React from 'react';
import StatusBadge from './StatusBadge.jsx';

/** Per-contact accordion for a DryRunReport. Includes a client-side CSV download. */
export default function DryRunReport({ report }) {
  if (!report) return null;
  const results = report.results || [];

  function downloadCsv() {
    const header = ['contact_id', 'name', 'phone', 'persona', 'status', 'outcome', 'turns', 'fields'];
    const lines = [header.join(',')];
    for (const r of results) {
      const fields = (r.extracted_fields || [])
        .map((f) => `${f.field_name}=${f.field_value}`)
        .join('; ')
        .replace(/"/g, '""');
      lines.push(
        [r.contact_id, `"${r.name || ''}"`, r.phone, r.persona, r.status, `"${r.outcome || ''}"`, r.turns, `"${fields}"`].join(',')
      );
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dry-run-campaign-${report.campaign_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="card">
      <div className="page-head">
        <div>
          <h3 className="page-title">Dry-run report (SIMULATION — no calls placed)</h3>
          <p className="page-sub">
            {report.contacts_run} of {report.contacts_total} contacts simulated
            {report.persona ? ` · persona: ${report.persona}` : ' · personas: round-robin'}.
          </p>
        </div>
        <div className="form-actions">
          <button className="btn btn-secondary btn-sm" onClick={downloadCsv}>
            Download CSV
          </button>
        </div>
      </div>
      {results.map((r) => (
        <details key={r.contact_id} className="card">
          <summary>
            {r.name} · {r.phone} · <StatusBadge status={r.status} /> · {r.persona} · {r.turns} turns
          </summary>
          <h4>Transcript</h4>
          {(r.transcript || []).map((t, i) => (
            <p key={i}>
              <strong>{t.role === 'agent' ? 'Agent' : 'Caller'}:</strong> {t.text}
            </p>
          ))}
          <h4>Extracted fields</h4>
          {(r.extracted_fields || []).length === 0 && <p className="hint">No fields recorded.</p>}
          <ul>
            {(r.extracted_fields || []).map((f, i) => (
              <li key={i}>
                <code>{f.field_name}</code>: {String(f.field_value)} ({Math.round((f.confidence || 0) * 100)}%)
              </li>
            ))}
          </ul>
          {r.outcome && (
            <p>
              Outcome: <code>{r.outcome}</code>
            </p>
          )}
        </details>
      ))}
    </div>
  );
}
```

Verify `StatusBadge` accepts arbitrary status strings (it renders call/contact statuses already; `dry-run`/`completed` pass through — check `StatusBadge.jsx` at edit time; add `dry-run` styling only if the component has an exhaustive map that would break).

- [ ] **Step 2: Add the SIMULATION panel to CampaignDetailPage**

In `frontend/src/pages/CampaignDetailPage.jsx`, near the Launch/Pause/Export header actions (lines 363-391):
1. Imports: `import { api, campaignExportUrl, playgroundApi } from '../api.js';` (extend line 3) and `import DryRunReport from '../components/DryRunReport.jsx';`
2. State: `const [dryRunPersona, setDryRunPersona] = useState(''); const [dryRunReport, setDryRunReport] = useState(null); const [dryRunBusy, setDryRunBusy] = useState(false); const [dryRunError, setDryRunError] = useState(null);`
3. Handler:

```javascript
  async function runDryRun() {
    setDryRunBusy(true);
    setDryRunError(null);
    setDryRunReport(null);
    try {
      const body = dryRunPersona ? { persona: dryRunPersona } : {};
      const report = await playgroundApi.runDryRun(id, body);
      setDryRunReport(report || null);
    } catch (e) {
      setDryRunError(e.message || 'Dry run failed.');
    } finally {
      setDryRunBusy(false);
    }
  }
```

(`id` is the campaign id already in scope on that page — verify the param name at edit time; the page calls `api.launchCampaign(id)`, so `id` is correct.)

4. JSX after the Export buttons:

```jsx
<div className="card">
  <h3 className="page-title">Test campaign (text simulation)</h3>
  <p className="page-sub">Runs every queued contact against scripted caller personas. No real calls, no minutes.</p>
  <div className="field">
    <label htmlFor="dryrun-persona">Persona</label>
    <select id="dryrun-persona" value={dryRunPersona} onChange={(e) => setDryRunPersona(e.target.value)}>
      <option value="">Round-robin (all five)</option>
      <option value="cooperative">Cooperative</option>
      <option value="terse">Terse</option>
      <option value="distracted">Distracted</option>
      <option value="refuses">Refuses</option>
      <option value="clueless">Clueless</option>
    </select>
  </div>
  {dryRunError && <div className="banner banner-error">{dryRunError}</div>}
  <div className="form-actions">
    <button className="btn primary" disabled={dryRunBusy} onClick={runDryRun}>
      {dryRunBusy ? 'Simulating…' : 'Run text dry-run'}
    </button>
  </div>
</div>
{dryRunReport && <DryRunReport report={dryRunReport} />}
```

- [ ] **Step 3: Create the P2 exit-gate checklist**

Create `docs/superpowers/evaluations/p2-exit-gates.md`:

```markdown
# P2 Exit Gates (must all record a result before P2 starts)

P2 = web-call concurrency/interruption tuning. Real calls to real numbers are
also gated on items 1-3 and 6.

| # | Gate | How to verify | Result | Date | Evidence |
|---|------|---------------|--------|------|----------|
| 1 | Agent speaks first, names real | Web test call; no `[...]` in speech/transcript | | | |
| 2 | Agent only responds to the caller | Web test call with background noise / second voice; count false turns | | | |
| 3 | Extraction persists + exports | Web test call → fields on Call Detail → Excel export has rows | | | |
| 4 | Latency measured, decision recorded | Fresh STT p50/p95 + E2E p50/p95 vs NFR-1 (900/1500 ms) | | | |
| 5 | No echo/replay | TTS→STT loopback check with current knobs | | | |
| 6 | Compliance | Disclosure-first, consent recorded, calling-hours enforced, DLT/DPDP sign-off | | | |
```

- [ ] **Step 4: Full verification — both suites green plus frontend build**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests -q`
Expected: all pass (163 baseline + Task 1-3, 6-8 additions).

Run (workdir `voice-agent/`): `.\.venv\Scripts\python.exe -m pytest tests -q`
Expected: all pass (69 baseline + Task 4-5 additions).

Run (workdir `frontend/`): `npm run build`
Expected: `✓ built in ...`, no errors.

Then run the P1 acceptance probes from the spec §7 that are automatable: dry-run the seeded sample campaign via the endpoint in a dev shell is manual; record the outcome in the handoff message.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/DryRunReport.jsx frontend/src/pages/CampaignDetailPage.jsx docs/superpowers/evaluations/p2-exit-gates.md
git commit -m "feat: campaign dry-run report UI and P2 exit-gate checklist"
```

---

## Self-review (run after writing, before handoff)

**1. Spec coverage:** §4.1 → Tasks 1, 2, 9. §4.2 → Tasks 3, 9. §4.3 → Tasks 4, 5. §4.4 → Task 6. §4.5 → Tasks 7, 8, 10 (with one recorded deviation: client-side CSV instead of server XLSX — server export waits on persisted reports, spec §9 stretch). §4.6 → Task 10 Step 3. Spec §5 API table → Tasks 3, 7, 8. Spec §7 acceptance 1-8 → Tasks 8, 7, 9, 3, 6, 5, 10, 10-Step-4. No gaps.

**2. Placeholder scan:** no TBD/TODO/later; every step has exact paths, code, commands, expected output. Two honest read-first steps (Task 8 Step 1 constraint check; Task 9 Step 1 insertion-area read) are explicit actions with expected outcomes, not placeholders.

**3. Type consistency:** `build_token_map(contact, institution, agent_name)` backend vs `(contact, context, agent_name)` voice — intentionally different second params (institution string vs context mapping); each task uses its own consistently. `_run_agent_turn(db, settings, call, version, *, user_text, start_event)` signature matches both the endpoint call and the runner's `run_turn` injection. `persona_reply(persona_name, agent_text, turn_no, contact)` matches unit tests and runner call (with `turns_used - 1` index fix noted in Task 8). `ensure_domain_config(db, agent, version)` matches test-call use. Dry-run response keys match `DryRunReport` schema and `DryRunReport.jsx` props (`results[].contact_id/name/phone/persona/transcript/extracted_fields/status/outcome/turns`).
