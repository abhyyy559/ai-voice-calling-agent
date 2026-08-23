# Enterprise Platform Transformation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the single-admin scaffold into an org-level multi-tenant platform where users build agents in the UI and test them end-to-end in-browser (mic → STT → LLM → TTS) without spending telephony minutes.

**Architecture:** Frozen API contract in `docs/superpowers/specs/2026-08-23-enterprise-platform-design.md` §4. Five independent lanes (backend, voice-runtime, frontend, infra, QA) built in parallel against that contract, integrated in order A+B → C → D+E.

**Tech Stack:** FastAPI/SQLAlchemy/JWT, LiveKit Agents (Python), Deepgram/Cartesia/Groq, React+Vite+livekit-client, Postgres/Redis, docker-compose.

## Global Constraints

- NEVER place a Twilio outbound call this phase. Twilio adapter stays implemented but dormant.
- No API keys in code — `.env` only; `.env.example` must stay synced and sanitized.
- Latency instrumentation logged per turn from day one (`stt_final_ms, llm_first_token_ms, tts_first_audio_ms, e2e_ms`).
- Extraction confidence <0.6 or required field unfilled after 3 asks → graceful wrap + flag. Never fabricate values.
- English-only UI/copy this phase. Type hints required (Python).
- Repo currently has no git history: Lane A Step 0 = `git init` + initial commit before any commits by other lanes.
- Windows host, PowerShell 5.1 shell. Python commands: `python -m pytest`. Node: `npm`.

---

## LANE A — backend-agent (Backend: tenancy, auth, agents, playground)

**Files:**
- Modify: `backend/main.py` (replace stub with app factory wiring `backend/app/routers/*`)
- Create: `backend/app/auth.py`, `backend/app/deps.py`, `backend/app/routers/auth.py`, `backend/app/routers/agents.py`, `backend/app/routers/playground.py`, `backend/app/routers/devtools.py`
- Create: `backend/app/models_additions.py` merged into `app/models.py`: `Organization`, `User`, `Agent`, `AgentVersion`; add columns `calls.kind/org_id`, `campaigns.org_id/agent_version_id`, `contacts.org_id`
- Create: `backend/migrations/versions/*tenancy_agents.py` (alembic)
- Test: `backend/tests/test_auth.py`, `test_agents.py`, `test_playground.py`, `conftest.py` (SQLite in-memory override of `get_db`)

**Interfaces (frozen):**
- `POST /api/auth/register {org_name,email,password}` → `{token,user:{id,email,role:"owner",org_id}}`; `POST /api/auth/login {email,password}` same shape; `GET /api/auth/me`.
- `deps.get_current_user` / `require_org(entity)` — all queries filtered by `user.org_id`; cross-org id → 404 (not 403, avoids existence leak).
- `POST /api/agents {name,description}`; `PATCH /api/agents/{id}` meta only; `DELETE` soft (status=archived); `POST /api/agents/{id}/versions {system_prompt,company_context,question_flow,extraction_schema,disclosure_script,escalation_rules,voice_settings}` → validate via existing `domain_config_schema` rules → immutable row, bump version int, set agent.current_version_id; `GET /api/agents/{id}/versions`; `GET /api/agent-versions/{vid}`.
- `POST /api/playground/sessions {agent_version_id}` → creates `calls(kind="playground", status="in_progress")`, issues LiveKit token (room `playground-{org_id}-{uuid4}`, TTL 1h) via livekit-api AccessToken with grant roomJoin, returns `{call_id, room_name, livekit_token, livekit_url}` (url from settings).
- `POST /api/playground/sessions/{call_id}/complete` → returns transcript turns, extracted_fields, latency metrics summary.
- `GET /api/health` → `{db:true|false, redis, voice_agent:"unknown"|..., providers:{deepgram,cartesia,groq,openai,twilio,livekit} bools}` (presence only, never values); `GET /api/dev/status` adds calling hours, CPS/concurrency limits, alembic head check.
- Internal (header `X-Internal-Token == settings.internal_api_token`): `GET /internal/agent-config?version_id=` → full AgentVersion JSON; `POST /internal/calls/{call_id}/transcript-turns` [{turn_index,speaker,text,timestamp,stt_final_ms,llm_first_token_ms,tts_first_audio_ms,e2e_ms}] append; `POST /internal/calls/{call_id}/extracted-fields`; `POST /internal/calls/{call_id}/complete`.

Steps: TDD per endpoint group (auth scoping test = register two orgs, org B GETs org A agent → expect 404). Seed script `backend/scripts/seed_demo.py`: demo org `demo@example.com`/`demo1234`, demo agent from `domain-configs/absent-student.json` as v1, 5 sample contacts + draft campaign. Sanitize `.env.example` Twilio lines to `your_twilio_account_sid` etc.; add `JWT_SECRET=change_me`, `INTERNAL_API_TOKEN=change_me_internal`, `LIVEKIT_URL=ws://localhost:7880`. Commit per green test group.

---

## LANE B — voice-pipeline-agent (LiveKit runtime)

**Files:**
- Create: `voice-agent/agent.py` (Worker entrypoint), `voice-agent/app/config.py`, `voice-agent/app/pipeline.py`, `voice-agent/app/extraction_tools.py`, `voice-agent/app/backend_client.py`, `voice-agent/requirements.txt` (update)
- Keep dormant: `voice-agent/app/twilio_protocol.py`

**Interfaces (frozen):**
- Job acceptance: rooms prefixed `playground-` (and `twilio-*` later). On job start: parse `version_id` from room metadata `{version_id, call_id}` (fallback: query backend by room name prefix pattern stored at session create — backend MUST put both keys in metadata; if absent, close gracefully).
- `BackendClient(base_url, internal_token)`: `get_agent_config(version_id)` (30s cache), `post_turns(call_id, turns)`, `post_fields(...)`, `post_complete(...)`.
- Pipeline (livekit.agents): `llm.FunctionTool`s: `record_extracted_field(field_name:str,value:str,confidence:float)`, `end_call(summary:str)`. STT=deepgram.STT(model="nova-3", language="en"), TTS=cartesia.TTS(), LLM=openai.LLM.with_groq(model="llama-3.3-70b-versatile") with OPENAI base-url fallback if GROQ key missing.
- System prompt render: disclosure script verbatim FIRST sentence block, then persona/company_context JSON dump, then question_flow numbered, extraction instructions incl. never-fabricate rule.
- Per-turn latency: wrap STT final event, LLM first token, TTS first audio callbacks; batch-post turns every turn.
- Graceful degradation: missing provider key → log + post_complete with error flag; worker stays alive.

Steps: unit-test prompt rendering + escalation logic offline (`pytest voice-agent/tests -v`, no network: fake BackendClient); smoke-run against local LiveKit (`livekit-server --dev`) documented in README section written here.

---

## LANE C — frontend-agent (React dashboard)

**Files:**
- Modify: `frontend/src/App.jsx` (routes below), `frontend/src/api.js` (JWT header injection + 401 redirect), `frontend/src/components/Layout.jsx` (nav: Dashboard, Agents, Playground, Campaigns, Dev Tools)
- Create pages: `Login.jsx`(register+login toggle), `DashboardPage.jsx` (feature-map cards, one-paragraph plain-English explanation each), `AgentsPage.jsx`, `AgentBuilderPage.jsx` (wizard steps: Basics→Context→Questions→Extraction schema→Voice→Review&Save-version; field-level validation errors), `PlaygroundPage.jsx` (livekit-client connect mic, AudioTrack subscribe, live caption area via data channel, post-call panel: transcript, extracted fields table, latency bars), `DevToolsPage.jsx`
- Create components: `VoiceSettingsForm.jsx`, `QuestionFlowEditor.jsx`, `ExtractionSchemaEditor.jsx`, `LatencyPanel.jsx`, `TranscriptView.jsx`, `HealthDot.jsx`

**Contract:** consumes exactly Lane A endpoints. Until A lands, gate calls behind `window.__MOCK__` fallbacks in `src/api.js` (mock module `mockApi.js`) so UI is demoable standalone.
Routes: `/login`, `/` (dashboard), `/agents`, `/agents/:id/edit`, `/playground/:agentVersionId?`, `/campaigns`, `/campaigns/:id`, `/calls/:id`, `/dev`.
DevToolsPage requirements (owner-mandated): top banner "DEV ONLY — hidden in production builds"; sections: Service health (poll `/api/health` 10s, HealthDot grid), Provider config checklist (`/api/dev/status` booleans + which env var to set), Full endpoint catalog grouped by router (method chips, one-line description, "Try" button firing sample request), latency glossary (what stt_final_ms etc. mean, NFR targets median ≤900ms P95 ≤1.5s). Hidden when `import.meta.env.PROD`.
Playground UX detail: mic permission prompt explainer card; state machine idle→connecting→in_call→ended; show elapsed timer + barge-in indicator; on disconnect auto-reconnect once then error card; partial results always kept in memory until posted.

Steps: `npm install livekit-client react-router-dom` (router exists); component tests optional, manual smoke checklist in README §Web Testing.

---

## LANE D — devops-agent

**Files:**
- Create: `backend/Dockerfile`, `frontend/Dockerfile` (node:20-alpine build → serve dist via vite preview or nginx), fix `infra/docker-compose.yml`: backend command `uvicorn app.main:app` (module path!) with env JWT_SECRET/INTERNAL_API_TOKEN passthrough, voice-agent command `python agent.py` (file exists after Lane B), add optional profile `livekit` service (`livekit/livekit-server --dev`, ports 7880/7881) so web testing works locally without cloud account
- Create: `scripts/dev-up.ps1`, `scripts/seed.ps1` wrappers; Update `README_SETUP.md` → full runbook: prerequisites, .env fill-in order, `docker compose --profile livekit up`, seed, login creds, web-test walkthrough, "how to add a second use case" (new agent version, zero code)

Acceptance: fresh clone + filled .env → `docker compose up` serves frontend :3000, API :8000, LiveKit :7880; `/api/health` all green except twilio (expected false/dormant).

---

## LANE E — qa-eval-agent

**Files:**
- Create: `backend/tests/test_tenancy_isolation.py`, `test_agent_versions_immutable.py`, `test_config_validation.py`, `voice-agent/tests/test_prompt_render.py`, `test_escalation.py`, `scripts/latency_report.py` (reads turns from DB, prints median/P95 vs NFR targets, exit non-zero if P95>1500ms on ≥10 samples)

Run full suite: `python -m pytest backend/tests voice-agent/tests -v` all green before integration sign-off.

---

## Integration Order

1. Lanes A–E run in parallel (C uses mocks).
2. After A+B land: verify handshake — start worker + backend, POST playground session, join from browser, complete session, assert rows in DB.
3. C rebases onto real API (delete mock gating).
4. D validates compose end-to-end; E runs suites + latency report; update PROJECT_LOG.md.
