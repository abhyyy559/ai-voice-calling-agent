# Real-Estate Verification + Quotation-Callback Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the shipped real-estate preset into the full verification→quotation-callback agent from the design spec, and prove it end-to-end with an automated dry-run gate.

**Architecture:** Config-only (no code changes): rewrite the preset's prompt/flow/schema with confirm-loop discipline, then drive it through the existing P1 machinery (agent versions, campaign dry-run with scripted personas) and assert structural correctness.

**Tech Stack:** JSON preset + pytest with hermetic SQLite (backend tests), Groq HTTP monkeypatched via the `_FakeAsyncClient` pattern in `backend/tests/test_playground_text.py`.

## Global Constraints

- Type hints required in all Python test code.
- Never hardcode API keys — no credentials in this plan (no new `.env` entries).
- Config-only: no backend, voice-agent, or frontend code changes. No latency tuning, no concurrency changes, no new providers.
- Never fabricate a structured-field value on low confidence — the confirm loop records only caller-confirmed values (FR-12).
- Every call domain stays a config/preset file — never a code branch.
- Backend tests run from `backend/` with `.\.venv\Scripts\python.exe -m pytest tests/<file>.py -q`.
- TDD every task: failing test, minimal implementation, green, commit. One task = one commit, staged files only.
- Validator rules that bind the preset JSON (`backend/domain_config_schema.py`): `system_prompt` min 10 chars; `question_flow` min 1 step, numbered sequentially from 1; each extraction field needs `type` ∈ {string, date, boolean, number}, `description`, `validation` ∈ {required, optional}, `confidence_threshold` 0.0–1.0; `disclosure_script` min 10 chars; `escalation_rules` min 1 with `action` ∈ {transfer, flag, end_call}; `voice_settings.language`/`stt_language` ∈ {en, te, hi}.

---

## File structure (what changes, and why)

- Modify `domain-configs/presets/real-estate-lead-qualification.json` — full rewrite of `version_payload` only (`preset_id`/`name` stay stable): confirm-loop system prompt, 6-step flow, 10-field schema with `quotation_callback_slot`, updated disclosure/escalation/company scaffolding.
- Modify `backend/tests/test_agents.py` — extend the RE preset assertions (10-field set, 6 steps, confirm-loop markers).
- Create `sample_real_estate_contacts.csv` (repo root, next to `sample_campaign_contacts.csv`) — 4 sample RE leads for manual import + dry-run.
- Create `backend/tests/test_real_estate_dry_run.py` — preset-content tests (mapped-tokens-only, rendering check) + automated dry-run gate (structural assertions).

Task order: Task 1 → Task 2 (Task 2 consumes the upgraded preset).

---

### Task 1: Upgrade the RE preset to verification + quotation-callback

**Files:**
- Modify: `domain-configs/presets/real-estate-lead-qualification.json`
- Test: `backend/tests/test_agents.py` (extend RE assertions)

**Interfaces:**
- Consumes: `validate_agent_version_payload` (enforced by `GET /api/agents/presets` — a malformed file fails the endpoint test loudly).
- Produces: upgraded preset served by the presets endpoint; Task 2 builds an agent version from `version_payload`.

- [ ] **Step 1: Write the failing test**

In `backend/tests/test_agents.py`, replace the existing `test_real_estate_preset_has_qualification_schema` body (added in P1 Task 6) with:

```python
def test_real_estate_preset_has_qualification_schema(client):
    token, _user = register(client)
    presets = client.get("/api/agents/presets", headers=auth_headers(token)).json()
    payload = next(p for p in presets if p["preset_id"] == "real-estate-lead-qualification")["version_payload"]
    assert set(payload["extraction_schema"]) >= {
        "enquiry_confirmed", "still_interested", "property_type", "budget_band",
        "locality_preference", "possession_timeline", "quotation_callback_slot",
        "visit_date_preference", "call_outcome", "escalation_needed",
    }
    assert len(payload["question_flow"]) == 6
    prompt = payload["system_prompt"].lower()
    assert "repeat" in prompt and "confirmation" in prompt and "quotation" in prompt
```

(Keep the preset-id set assertion from Task 6 unchanged.)

- [ ] **Step 2: Run test to verify it fails**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_agents.py -q`
Expected: FAIL — extraction-schema set mismatch (old 7-field schema) and `len(question_flow) == 5`, not 6.

- [ ] **Step 3: Rewrite the preset payload**

Replace the entire `version_payload` object in `domain-configs/presets/real-estate-lead-qualification.json` with the JSON below. Keep `preset_id`, `name` as-is; update `description` to the new text shown. Use only mapped tokens (`[Company Name]`, `[Lead Name]`, `[Agent Name]`) in `system_prompt`, `disclosure_script`, and `question_flow` — company-knowledge scaffolding keeps `[Price bands served]`-style fill-ins (builder user replaces them; matches the shipped lead-verification convention).

```json
{
  "preset_id": "real-estate-lead-qualification",
  "name": "Real-Estate Lead Qualification Agent",
  "description": "Verifies property enquiries are genuine, collects the full requirement with per-value confirmation, and commits to a quotation-callback slot. Never quotes prices — the human specialist delivers the quotation on callback.",
  "version_payload": {
    "system_prompt": "# ROLE\nYou are a verification and qualification agent for [Company Name], a real-estate brokerage. You call people who recently enquired about a property (website form, listing, or referral).\n\n# OBJECTIVE\nConfirm the enquiry is genuine, collect the full requirement (property type, budget band, preferred locality, possession timeline), and agree an EXACT day and time for a specialist to call back with a detailed quotation. Your job is verification and commitment, NOT closing the sale and NEVER quoting prices.\n\n# PERSONA & TONE\nWarm, professional, unhurried. The whole call should take 2-3 minutes. Never pushy, never argue.\n\n# OPENING\n\"Hi [Lead Name], this is [Agent Name] calling from [Company Name] regarding the property enquiry you submitted recently. Do you have a couple of minutes?\"\n\n# CONFIRM LOOP (follow on every requirement answer)\n1. Ask ONE thing per turn.\n2. When the caller answers, repeat the value back (\"Just to confirm, your budget is around 80 lakhs, correct?\") and record it ONLY after explicit confirmation (yes / correct / right).\n3. On correction: update the value, repeat it back again, and re-confirm.\n4. Ask callers to spell out names of people and localities; never guess a spelling.\n5. NEVER record a value the caller has not confirmed. If unsure, ask a short clarifying question instead of recording.\n6. For the callback slot: propose a day and time, negotiate if needed, confirm the EXACT slot, read it back once more, then record it.\n\n# THINGS TO FIND OUT\n1. Confirm they actually made the enquiry (if not, apologise politely and end the call).\n2. Confirm their interest in buying is still current.\n3. Requirement, one item per turn: property type, then budget band, then preferred locality — each confirmed before moving on.\n4. Possession timeline.\n5. Quotation-callback slot: exact agreed day and time.\n6. Wrap up: thank them and restate the commitment (\"We will call you back on {slot} with your quotation\"). If the caller asks for a site visit instead, note the preferred date and wrap up the same way.\n\n# ANSWERING PROPERTY QUESTIONS\nAnswer only basic property questions whose facts are in your company knowledge (size, price band, amenities, location). If a fact is not in your knowledge, say a specialist will confirm it on the callback — never quote a number you were not given.\n\n# OBJECTIONS & FAQ\n- \"I never enquired.\" -> Apologise sincerely, mention the enquiry source if you have it, and end the call politely. Flag the lead as invalid.\n- \"Just send me the details on WhatsApp.\" -> Offer to have the specialist send details on the quotation callback, after this quick verification.\n- \"I'm busy right now.\" -> Ask for a better time, note it, thank them, and end the call.\n- \"How did you get my number?\" -> \"You shared it in the enquiry you submitted.\"\n\n# DO NOT\n- Never quote prices, offers, or possession dates beyond your company knowledge.\n- Never share other people's information.\n- Never continue the call if the person says they are not interested - thank them and end it.\n- Never record unconfirmed values - an empty field with a clarifying question beats a guessed value every time.",
    "company_context": {"company_name": "[Company Name]", "price_bands": "[Price bands served]", "areas_served": "[Areas served]", "sample_listing_facts": "[Size / price band / amenities of the featured property]"},
    "question_flow": [
      {"step": 1, "question": "Did you recently enquire about a property with [Company Name]?"},
      {"step": 2, "question": "Are you still looking to buy?"},
      {"step": 3, "question": "What type of property are you looking for?"},
      {"step": 4, "question": "What budget band and locality are you considering?"},
      {"step": 5, "question": "By when are you hoping to take possession?"},
      {"step": 6, "question": "Our specialist can call you back with a detailed quotation — what day and time works for you?"}
    ],
    "extraction_schema": {
      "enquiry_confirmed": {"type": "boolean", "description": "Whether the caller confirms making the enquiry.", "validation": "required", "confidence_threshold": 0.8},
      "still_interested": {"type": "boolean", "description": "Whether buying interest is still current.", "validation": "required", "confidence_threshold": 0.8},
      "property_type": {"type": "string", "description": "Property type exactly as stated (2BHK, plot, villa).", "validation": "required", "confidence_threshold": 0.7},
      "budget_band": {"type": "string", "description": "Budget band exactly as stated and confirmed.", "validation": "required", "confidence_threshold": 0.8},
      "locality_preference": {"type": "string", "description": "Preferred locality, confirmed and spelled out.", "validation": "required", "confidence_threshold": 0.8},
      "possession_timeline": {"type": "string", "description": "When they hope to take possession.", "validation": "optional", "confidence_threshold": 0.7},
      "quotation_callback_slot": {"type": "string", "description": "REQUIRED whenever call_outcome is qualified_callback: the exact agreed day/time for the quotation callback.", "validation": "optional", "confidence_threshold": 0.8},
      "visit_date_preference": {"type": "string", "description": "Preferred site-visit date/time, only if the caller asks for a visit.", "validation": "optional", "confidence_threshold": 0.7},
      "call_outcome": {"type": "string", "description": "Outcome: qualified_callback, qualified_visit, not_interested, or invalid_lead.", "validation": "required", "confidence_threshold": 0.8},
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

Notes the implementer must respect:
- `quotation_callback_slot` is `validation: "optional"` deliberately: the schema language has no conditional-required, and refuses/invalid calls must not flag a missing slot. The REQUIRED-when-callback rule lives in its description + the confirm loop (§6 of the prompt), which is the enforcement point.
- Steps stay sequential 1-6; thresholds stay 0.8 required / 0.7 optional / 0.9 escalation (confirm loop, not lowered bars, is the reliability fix).
- Write the file with UTF-8 encoding, no BOM, no trailing commas. Validate JSON parses before running pytest.

- [ ] **Step 4: Run test to verify it passes**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_agents.py -q`
Expected: all pass (the presets endpoint runs `validate_agent_version_payload` on the new file — a malformed file fails here, not silently).

- [ ] **Step 5: Commit**

```bash
git add domain-configs/presets/real-estate-lead-qualification.json backend/tests/test_agents.py
git commit -m "feat: upgrade RE preset to verification plus quotation-callback agent"
```

---

### Task 2: Sample RE leads + automated dry-run gate

**Files:**
- Create: `sample_real_estate_contacts.csv` (repo root)
- Test: `backend/tests/test_real_estate_dry_run.py` (new)

**Interfaces:**
- Consumes: Task 1 (upgraded preset via `GET /api/agents/presets`); P1 `POST /api/playground/campaigns/{id}/dry-run`, `_render_text_system_prompt` (backend router).
- Produces: nothing downstream — this task is the verification gate. Manual follow-up (user roleplay + real dry-run in the deployed UI) is outside this plan.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_real_estate_dry_run.py`:

```python
"""Real-estate agent gate: preset tokens, prompt rendering, dry-run structure."""
from __future__ import annotations

import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from conftest import auth_headers, register

_PRESET = Path(__file__).resolve().parents[2] / "domain-configs" / "presets" / "real-estate-lead-qualification.json"

# Tokens the Task 1/4 maps resolve (backend build_token_map + voice map).
_MAPPED_TOKENS = {
    "[Institution Name]", "[Company Name]", "[Student Name]", "[Lead Name]",
    "[Parent/Guardian Name]", "[Agent Name]", "[Expected Return Date]",
}


def _payload() -> dict[str, Any]:
    return json.loads(_PRESET.read_text(encoding="utf-8"))["version_payload"]


def test_preset_spoken_regions_use_only_mapped_tokens() -> None:
    payload = _payload()
    spoken = "\n".join(
        [
            payload["disclosure_script"],
            payload["system_prompt"],
            *[step["question"] for step in payload["question_flow"]],
        ]
    )
    tokens = set(re.findall(r"\[[^\]]*\]", spoken))
    assert tokens, "expected at least the Company/Lead/Agent tokens"
    assert tokens <= _MAPPED_TOKENS, f"unmapped spoken tokens: {tokens - _MAPPED_TOKENS}"


def test_preset_renders_with_real_names() -> None:
    from app.routers.playground import _render_text_system_prompt

    payload = _payload()
    config = SimpleNamespace(
        disclosure_script=payload["disclosure_script"],
        system_prompt=payload["system_prompt"],
        company_context={},
        question_flow=payload["question_flow"],
        extraction_schema=payload["extraction_schema"],
    )
    contact = {"lead_name": "Riya Sharma", "city": "Hyderabad", "budget_band": "80 lakhs"}
    prompt = _render_text_system_prompt(config, contact=contact, institution="Acme Realty")
    assert "Riya Sharma" in prompt
    assert "Acme Realty" in prompt
    assert "Hyderabad" in prompt
    assert "[Lead Name]" not in prompt
    assert "[Company Name]" not in prompt
    leftovers = set(re.findall(r"\[[^\]]*\]", prompt))
    # [REQUIRED] is a platform marker the renderer adds for required fields,
    # not a placeholder leak — it is the only bracket token permitted here.
    assert leftovers <= {"[REQUIRED]"}, f"unsubstituted tokens in rendered prompt: {leftovers}"
```

Then the dry-run gate test (append to the same file):

```python
def test_real_estate_dry_run_structural_gate(groq_client, session_factory):
    from sqlalchemy import select

    from app.models import Call, Campaign, Contact
    from test_playground_text import chat, script, tool_call

    client = groq_client
    token, user = register(client)
    payload = _payload()
    agent = client.post(
        "/api/agents", json={"name": "RE Gate Agent", "description": ""},
        headers=auth_headers(token),
    )
    assert agent.status_code == 201, agent.text
    version = client.post(
        f"/api/agents/{agent.json()['id']}/versions", json=payload,
        headers=auth_headers(token),
    )
    assert version.status_code in (200, 201), version.text
    version_id = version.json()["id"]

    with session_factory() as db:
        campaign = Campaign(
            name="RE Gate", org_id=user["org_id"],
            agent_version_id=version_id, status="draft",
        )
        db.add(campaign)
        db.flush()
        for name, phone, custom in [
            ("L1", "+919812345611", {"lead_name": "Riya Sharma", "city": "Hyderabad"}),
            ("L2", "+919812345612", {"lead_name": "Arjun Rao", "city": "Bengaluru"}),
            ("L3", "+919812345613", {"lead_name": "Meera Iyer", "city": "Chennai"}),
        ]:
            db.add(Contact(
                campaign_id=campaign.id, name=name, phone=phone,
                status="pending_review", custom_fields=custom,
            ))
        db.commit()
        campaign_id = campaign.id

    # Personas answer positionally; the gate asserts STRUCTURE (persistence,
    # markup absence, schema membership), not content. Script accounting: each
    # contact consumes opening chat + record tool + follow-up chat + end_call
    # tool + spare chat = 5 Groq calls (round-robin personas never end early).
    script(
        chat("Hello, disclosure line. Am I speaking with Riya?"),
        tool_call("record_extracted_field", {"field_name": "budget_band", "value": "80 lakhs", "confidence": 0.9}),
        chat("Thanks, noted."),
        tool_call("end_call", {"summary": "done 1"}),
        chat("Goodbye."),
        chat("Hello, disclosure line. Am I speaking with Arjun?"),
        tool_call("record_extracted_field", {"field_name": "locality_preference", "value": "Madhapur", "confidence": 0.85}),
        chat("Thanks, noted."),
        tool_call("end_call", {"summary": "done 2"}),
        chat("Goodbye."),
        chat("Hello, disclosure line. Am I speaking with Meera?"),
        tool_call("record_extracted_field", {"field_name": "property_type", "value": "2BHK", "confidence": 0.8}),
        chat("Thanks, noted."),
        tool_call("end_call", {"summary": "done 3"}),
        chat("Goodbye."),
    )
    resp = client.post(
        f"/api/playground/campaigns/{campaign_id}/dry-run",
        json={},
        headers=auth_headers(token),
    )
    assert resp.status_code == 200, resp.text
    report = resp.json()
    assert report["contacts_run"] == 3
    assert report["results"][0]["extracted_fields"][0]["field_name"] == "budget_band"
    assert all(r["status"] == "completed" for r in report["results"])
    schema_keys = set(payload["extraction_schema"])
    with session_factory() as db:
        for result in report["results"]:
            for turn in result["transcript"]:
                assert "[" not in turn["text"] and "]" not in turn["text"]
                assert "<tool_call>" not in turn["text"]
            for field in result["extracted_fields"]:
                assert field["field_name"] in schema_keys
        rows = db.scalars(select(Call).where(Call.campaign_id == campaign_id)).all()
        assert len(rows) == 3 and all(c.kind == "dry-run" for c in rows)
```

Imports needed at the top of the new test file: `from test_playground_text import chat, groq_client, script, tool_call` (fixture import works in pytest — same pattern as P1 Task 8). Note: `groq_client` is a fixture — importing it makes it available. `start_session` is NOT needed (custom agent/campaign seeding inline).

- [ ] **Step 2: Run tests to verify they fail**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_real_estate_dry_run.py tests/test_agents.py -q`
Expected: FAIL — schema set + flow-length mismatch on the old preset (token/render tests pass on old content; the gate test fails at the version-build or schema assertions — either way red before green).

- [ ] **Step 3: Create the sample CSV**

Create `sample_real_estate_contacts.csv` (repo root):

```csv
name,phone,lead_name,city,property_interest,budget_band
Riya Sharma,+919812345611,Riya Sharma,Hyderabad,2BHK apartment,60-80 lakhs
Arjun Rao,+919812345612,Arjun Rao,Bengaluru,3BHK apartment,1-1.3 crore
Meera Iyer,+919812345613,Meera Iyer,Chennai,Residential plot,40-60 lakhs
Karan Mehta,+919812345614,Karan Mehta,Pune,2BHK apartment,70-90 lakhs
```

(Headers mirror `sample_campaign_contacts.csv` conventions: name,phone + domain keys. Numbers use the +91981234561x sandbox range, distinct from the absentee sample's 601–610.)

- [ ] **Step 4: Run tests to verify they pass**

Run (workdir `backend/`): `.\.venv\Scripts\python.exe -m pytest tests/test_real_estate_dry_run.py tests/test_agents.py -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add sample_real_estate_contacts.csv backend/tests/test_real_estate_dry_run.py
git commit -m "feat: RE sample leads and automated dry-run gate"
```
