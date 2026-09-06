# P1 — Text-mode campaign dry-run + contact-aware testing — Design

**Date:** 2026-09-06 (IST)
**Status:** Approved (design approval given during brainstorming; build starts after implementation-plan approval)
**Scope:** P1 only. P2 (web-call concurrency/interruption optimization) and real phone calls to real numbers are gated behind the exit checklist in §6.

---

## 1. Context

EchoSarathi's call pipeline already supports per-lead outbound calls (dialer, statuses, retry, export). What is missing is the *testing/product loop* the user asked for:

- Testing an agent **before any telephony** — today a text-playground session is strictly 1:1 and knows nothing of campaigns; there is **no way to simulate calling a 10-lead campaign**.
- Making the agent **aware of whom it is calling** — the API supports a `contact` card, but the frontend never sends it (see §2, decision matrix).
- Making the agent **speak first with real names** — the opening is currently driven by an interruptible auto-turn; placeholder tokens and a domain-locked caller-context block leave gaps on both voice and text paths.
- Giving the user a **new agent type end-to-end** (real-estate lead qualification) as proof the system is domain-independent.
- Enforcing a **strict exit gate** so we do not optimize voice concurrency / place real calls before core behavior and compliance are verified.

Out of scope for P1 (Beta V2): website/form-call triggers, Telugu, phone-concurrency tuning, new telephony providers.

## 2. Decisions (approved during brainstorming)

| # | Decision | Rationale |
|---|---|---|
| D1 | Test a whole campaign in **text-mode dry-run** with **scripted caller personas**, before any voice/web-call optimization | Deterministic, network-free, no babysitting 10 back-and-forths; doubles as cheap pre-flight; matches the "caller just answers" mental model |
| D2 | Agent **speaks first**; adds **contact-aware greeting** with real names; caller only answers | Direct user requirement; fixes verbatim `[Student Name]` style placeholders |
| D3 | Frontend **sends `contact`** to playground sessions and `agent_version_id`+`contact` to test-call; reuse one lead-card form | API already supports both; only the UI is missing |
| D4 | **Strict interruption discipline** for "only listen to me" — recorded as a **P2 constraint**, not implemented in P1 | User chose strict (fewer false turns; may ignore a quick "yes") over sensitive barge-in; needs live verification anyway, which P1 cannot do |
| D5 | New agents are **DB-backed versions**; add a **real-estate preset JSON** so the builder prefills; auto-derive a legacy `DomainConfig` row so phone/test-call paths work | Exploration (§3) proved the brain is version-based but the *phone path* still needs a `domain_config_id` FK |
| D6 | P1 ships a recorded **exit-gate checklist**; P2 may not start until it is filled | Protects against optimizing before core behavior + compliance verified |
| D7 | P1 changes stay UI/test-contact + prompt/core-greeting; **no latency tuning, no concurrency changes, no new providers** | YAGNI guardrail; those are P2 |

## 3. Evidence (from codebase exploration, 2026-09-06)

- **Playground contact gap:** `frontend/src/api.js:160-164` `playgroundApi.startSession(agentVersionId)` sends only `{agent_version_id}`; `TextPlayground.jsx:56` and `PlaygroundPage.jsx:334` pass only the version id. Backend `POST /api/playground/sessions` already accepts `contact` (`routers/playground.py:46-50`), sanitized by `_clean_contact` (`:53-65`).
- **Text prompt is domain-locked:** `_render_text_system_prompt` (`routers/playground.py:303-462`) hard-codes `student_name/parent_name/class_section/absent_date` phrasing in the CALLER CONTEXT block (`:349-407`) and does **not** inject `institution_name` (org name only reaches the voice path via `GET /internal/calls/{id}/context`, `internal.py:63-101`).
- **No token substitution on the text path:** voice has `apply_token_substitution`/`build_token_map` (`voice-agent/app/prompting.py`); the backend text path renders user-authored `system_prompt`/`question_flow` verbatim — `[Institution Name]`/`[Student Name]` would be spoken literally.
- **Voice opening is an interruptible auto-turn:** `run_session` calls `session.start(...)` (`voice-agent/app/pipeline.py:727`) with no explicit greeting; the only `session.say(..., allow_interruptions=False)` in the codebase is the apology path (`pipeline.py:772`). "Speaks first" is prompt-only today.
- **Test-call API lags UI:** `POST /api/test-call` supports `agent_version_id` + `contact` (`routers/test_call.py:37-165`, schema `schemas.py:242-249`); `TestCallPage.jsx:25-40` sends only `{domain_config_id, to?}`. `domain_config_id` is required (`:67-68`).
- **Campaign infra already exists:** CSV/XLSX import → `pending_review`/`invalid` → `launch` flips `pending_review→queued` (`routers/campaigns.py:173-181`) → `DialerService` dials with retry/backoff (`services/dialer.py:42-187`) → statuses visible (contacts table + dashboard tiles + recent calls) → campaign export CSV/XLSX. **No campaign-level dry-run exists** (grep `dry_run|bulk.*test|batch.*playground` → nothing).
- **Voice knobs today (for the §6 record):** `min_endpointing_delay=0.35`, `max_endpointing_delay=1.5`, `min_interruption_duration=0.5`, `false_interruption_timeout=2.0`, `resume_false_interruption=False`, `discard_audio_if_uninterruptible=True` (`pipeline.py:693-713`); Silero VAD loaded with **all defaults** (`:699`); Deepgram `endpointing_ms=300` (`:154`); `enable_diarization=False`; no browser `noiseSuppression`/`echoCancellation`/`autoGainControl` in `PlaygroundPage.jsx:323`.

## 4. Design

### 4.1 Contact-aware Playground

**Goal:** when testing an agent (text or web-call), the agent knows whom it is calling; the caller-context prompt is generic, not domain-locked.

**UI**
- New shared component `frontend/src/components/LeadCardForm.jsx` (key/value rows, add/remove) reused in Playground setup and TestCall. Preloads a sensible default set (mirrors `sample_campaign_contacts.csv` headers: `student_name, parent_name, class_section, absent_date`) when the selected agent is the absent-student domain; otherwise starts from the agent's `company_context.question_field_hints` when present.
- `PlaygroundPage.jsx` setup panel: add "Who are we calling?" collapsible section bound to the form. Forward the flat dict via `startSession(versionId, contact)` from `api.js`.
- `TextPlayground.jsx` and the voice `startCall` both pass the contact through.

**Backend**
- `_render_text_system_prompt` CALLER CONTEXT block reworked to be generic:
  - Known-key map: `{name, student_name, student}` → "the person the call is about"; `{parent_name, parent, guardian}` → "the parent/guardian"; `{class_section, class}` → "the class"; `{absent_date}` → "the absence date". Other supplied keys are read as generic facts.
  - "Say the names out loud" only when a name key is present; otherwise instruct the model: **do not invent or guess any name**.
  - Verify-relationship guardrail generalized (if the person who answered is not the named parent/guardian, ask who is speaking).
- Inject `institution_name` into the text prompt (org name → campaign name → `""`), mirroring `internal.py:63-101` logic.
- Port token substitution to the backend: `backend/app/services/token_substitution.py` with `build_token_map(contact, institution)` and `apply_token_substitution(text, tokens)` covering `[Institution Name]`/`[Company Name]` → institution, `[Student Name]`/`[Lead Name]` → primary name, `[Parent/Guardian Name]` → parent name, `[Agent Name]` → agent display name; empty values drop the token's sentence fragment; safety-net strips any leftover `[...]`. Applied to disclosure, system prompt, and each question-flow question before rendering. (Deliberate small duplication of the voice-agent helper — two services, two codebases; noted in §9.) The same extended map is used by the voice path's `build_opening_line` (§4.3) so existing presets that use `[Company Name]`/`[Lead Name]` render cleanly in both services.

### 4.2 Contact-aware Test Call

**Goal:** test a *specific version* of an agent against a specific lead on a real phone number.

- `TestCallPage.jsx`: add an **agent-version picker** (options = versions in the org, default = latest) and the **LeadCardForm**; send `{domain_config_id, agent_version_id, contact, to}`. Show which version spoke on the result.
- Schema `POST /api/test-call`: make `domain_config_id` optional; when omitted, derive it from the chosen `agent_version_id` via a new `ensure_domain_config(agent)` helper — find-or-create a `DomainConfig` row from the version payload (name, system_prompt, disclosure, extraction_schema, voice_settings). Keeps backward compatibility (if both given, use the given `domain_config_id`).

### 4.3 Agent speaks first, protected greeting, real names

**Voice path** (`voice-agent`):
- New `build_opening_line(...)` in `prompting.py` + tests: composes `opening = disclosure + personalized greeting + first question`, all token-substituted via the extended map from §4.1. Greeting is a single deterministic sentence of the form *"Hello {parent/guardian}, I'm calling from {institution} about {student}."* (falling back gracefully when a name/institution is absent — no invented names).
- `run_session` speaks it explicitly: `await session.say(opening, allow_interruptions=False)` right after `session.start` (pattern already proven at `pipeline.py:772`). This guarantees (a) agent speaks first, (b) background noise cannot barge the greeting, (c) names are real. When no disclosure/context exists, fall back to the current prompt-driven auto-turn.
- Verify the pre-rolled opening reaches `TurnTelemetry` captions/transcript (it should, via `conversation_item_added`).

**Text path**: already agent-first (`event:'start'` kickoff at `playground.py:666-682`); covered by §4.1 substitution + generic context. No structural change.

### 4.4 Real-estate lead-qualification agent (preset)

- New `domain-configs/presets/real-estate-lead-qualification.json` — a complete builder `version_payload` (ships via `GET /api/agents/presets` automatically; `routers/agents.py:32-36` reads the presets dir):
  - **system_prompt:** brokerage agent calling a prospect who submitted a form / requested info on a property; confirm genuine interest; qualify (requirement, budget band, locality, possession timeline); propose a concrete next step (site visit / call-back); answer *basic* property questions from `company_context` only; never quote unverified numbers; low-confidence values escalate/flag, never fabricate (FR-12).
  - **company_context:** scaffolding keys for brokerage name, price bands, areas served, property facts, plus the "basic info to end user" the user wants (size, price band, amenities — only from supplied facts).
  - **question_flow:** opener/consent → confirm interest in the property → requirement (budget & timeline) → visit preference → wrap-up commitment.
  - **extraction_schema:** `interest_level, budget_band, locality_preference, possession_timeline, visit_date_preference, call_outcome, escalation_needed` (types, required flags, confidence thresholds 0.7–0.9).
  - **disclosure** (consent line), **escalation_rules**, **voice_settings** (en, Cartesia default).
- No code branches: the user proves domain-independence by filling the builder from this preset or typing their own.

### 4.5 Campaign dry-run (text, scripted personas)

**Endpoint:** `POST /api/playground/campaigns/{id}/dry-run`

- Uses the campaign's pinned `agent_version_id` (fallback = latest org version), iterates its contacts (`queued` + `pending_review`, run cap e.g. 20 per call, query param to override), runs each lead through the existing text-turn loop (`_turn_loop`, `playground.py:616-674`) against a **scripted persona**, and returns a per-lead report.
- **Personas** (defined as data in `backend/app/services/dry_run.py`), the simulated callers:
  1. **cooperative** — answers every question cleanly.
  2. **terse** — 1–2 word answers (stresses the agent's confirmation loop + concision).
  3. **distracted** — adds filler/off-topic asides between real answers (stresses extraction precision).
  4. **refuses** — consent refusal / "not interested"; expects clean wind-down + refused outcome.
  5. **clueless** — "I don't know" to all questions (stresses escalation/no-fabrication).
- **Runner** (`services/dry_run.py`): per contact — persona selected round-robin (or explicit `persona` param); simulate up to N agent turns (cap 6); agent utterance = LLM reply given the chat; persona reply = resolver over scripted slots (blank → skip turn); reuse the same extraction registrar as real turns so extracted fields + status/outcome semantics match production. Record per-turn latency/cost.
- **Response** (`schemas.py`): `DryRunReport {campaign_id, persona, contacts_total, contacts_run, results: [DryRunContactResult {contact_id, name, phone (masked), transcript: [{role, text}], extracted_fields, status, outcome, turns, latency_ms, cost_usd}]}`. Synchronous (10-ish contacts × ≤6 turns on a fast model is acceptable; risk noted in §9).
- **Frontend** (`CampaignDetailPage.jsx`): "Test campaign (text)" button (clearly **SIMULATION** state, separate from real Launch) → persona picker + run → new `DryRunReport` component: per-contact accordion (transcript, extracted-field chips, status badge, latency/cost), plus Export CSV/XLSX for the dry-run report (reuse `export_service` patterns).
- **No new DB table in P1.** Dry-run results live in the HTTP response; per-call campaign history is unchanged. (Persisted reports = stretch, §10.)

### 4.6 Exit-gate checklist (gates P2)

New file `docs/superpowers/evaluations/p2-exit-gates.md` — checklist table with **How to verify | Result | Date | Evidence**, filled per item while the product is exercised. P2 (web-call concurrency/interruption tuning) **and** real calls to real numbers may not start until each funded item records a result:

1. **Agent speaks first, names real** — web test call; no `[placeholders]` in speech/transcript.
2. **Agent only responds to the caller** — web test call with background noise / a second voice; count false turns. P2 will implement strict-discipline tuning (Silero threshold above default 0.5, higher `min_interruption_duration`, optional `min_interruption_words`, browser EC/NS/AGC constraints in `PlaygroundPage.jsx:323`).
3. **Extraction persists & exports** — web test call → structured fields visible on Call Detail → Excel export has rows.
4. **Latency measured & decision recorded** — fresh STT p50/p95 + E2E p50/p95 vs NFR-1 (900/1500 ms); proceed-or-tune decision written (P2 scope).
5. **No echo/replay** — TTS→STT loopback check with current knobs (endpointing 300 ms, interruption 0.5 s).
6. **Compliance** — disclosure-first in speech/transcript, consent recorded, calling-hours enforced, DLT/DPDP status confirmed (`compliance-agent` sign-off).

## 5. API / schema changes

| Endpoint / model | Change |
|---|---|
| `POST /api/playground/sessions` | no schema change; frontend now sends `contact` |
| `POST /api/playground/campaigns/{id}/dry-run` | **new**: `DryRunCreate {persona?}`, `DryRunReport` (above) |
| `POST /api/test-call` | `domain_config_id` becomes optional (derived via `ensure_domain_config`); `agent_version_id`/`contact` already supported |
| `backend/app/services/token_substitution.py` | **new** helper (ported) |
| `backend/app/services/dry_run.py` | **new**: personas + runner |
| `backend/app/routers/agents.py` | `ensure_domain_config(agent)` helper |
| `voice-agent/app/prompting.py` | `build_opening_line(...)` |
| `voice-agent/app/pipeline.py` | explicit `session.say(opening, allow_interruptions=False)` after start |

## 6. Files touched

- `backend/app/routers/playground.py`, `backend/app/schemas.py`, `backend/app/routers/agents.py`, `backend/app/routers/test_call.py` (schema only)
- `backend/app/services/token_substitution.py`, `backend/app/services/dry_run.py` (new)
- `backend/tests/` → `test_playground_contact.py`, `test_token_substitution.py`, `test_dry_run.py`, `test_testcall_contact.py`, `test_agents_domain_config.py` (new)
- `voice-agent/app/prompting.py`, `voice-agent/app/pipeline.py` + their tests
- `frontend/src/api.js`, `frontend/src/pages/PlaygroundPage.jsx`, `frontend/src/pages/TestCallPage.jsx`, `frontend/src/pages/CampaignDetailPage.jsx`
- `frontend/src/components/LeadCardForm.jsx`, `frontend/src/components/DryRunReport.jsx` (new)
- `domain-configs/presets/real-estate-lead-qualification.json` (new)
- `docs/superpowers/evaluations/p2-exit-gates.md` (new — gate record)

## 7. Acceptance criteria (how we know it works)

1. `POST /api/playground/campaigns/{id}/dry-run` on `sample_campaign_contacts.csv` (10 leads) returns per-lead transcript + extracted fields + status/outcome; text prompt contains substituted names + institution, never `[Student Name]`.
2. Persona "refuses" produces a clean wind-down with refused/opted-out-style outcome, no fabricated fields (FR-12).
3. Playground text session with a contact card greets the lead by real name; with no contact, produces no invented names.
4. `TestCallPage` sends `agent_version_id`+`contact`; backend derives `domain_config_id` when omitted.
5. Real-estate preset appears in `GET /api/agents/presets`; a version built from it runs the text dry-run with its own extraction schema.
6. Voice `session.say(opening, allow_interruptions=False)` is exercised by a unit test (monkeypatched), and `build_opening_line` output is interruption-safe + placeholder-free.
7. Exit-gate checklist exists and P2 has not started.
8. Backend suite green (163 + new), voice-agent suite green (69 + new), frontend builds clean.

## 8. Risks / mitigations

- **Groq free-tier latency on a 10-lead sequential dry-run** (10 × ≤6 turns) — acceptable for P1 (pre-flight, run asynchronously in the UI while user watches); concurrency is a P2 optimization.
- **Scripted personas miss real-world variance** — mitigated by covering refusal, terse, distracted, clueless; user's real calls remain the ground truth (§6 checklist).
- **Domain-config drift between DB agent brain and legacy phone path** — mitigated by `ensure_domain_config` auto-derive.
- **Behavior change of explicit opening vs auto-turn** — fallback to auto-turn when no disclosure/context; opening is verified via transcript in item 1 of the gate.
- **Deliberate helper duplication (token substitution) across two service codebases** — accepted for P1; consolidated only when the services unify.
- **Scope creep into P2** — §6 gate + the D7 guardrail.

## 9. Stretch / backlog

- Persist dry-run reports (disk/DB) + campaign-level dry-run export.
- `min_interruption_words` + stricter VAD threshold (P2 strict-discipline package).
- Personas run concurrently / persona library grows.
- Website/form-call triggers (Beta V2). Telugu (Beta V2).

## 10. P2 constraints (recorded now, implemented later)

Tuning limit for "agent only listens to the caller": Silero `activation_threshold` above default 0.5, `min_interruption_duration` raised, `min_consecutive_speech_delay`/`min_interruption_words` enabled, browser `noiseSuppression`/`echoCancellation`/`autoGainControl` on the web path, and/or Deepgram `vad_events`/`keywords` gating. Decision: **strict discipline** (may ignore a quick mid-speech "yes") per user choice.