# Design Spec — Enterprise Multi-Tenant Voice Agent Platform (Web-First Phase)

Date: 2026-08-23 · Status: Approved by owner (verbal directive: proceed without further approvals)

## 1. What this is

Transform the existing single-admin scaffold into an enterprise, organization-level platform where any company signs up, builds ("trains") voice agents by configuring them in the UI, tests them **entirely in-browser** (mic → STT → LLM → TTS, zero telephony minutes burned), and later launches real outbound campaigns. Domain-independent: sales, lead qualification, surveys, absent-student follow-up — all just configs.

Owner directives (binding):
1. No more approval gates — complete autonomously.
2. **Do NOT place any Twilio calls this phase** (preserve trial minutes). All testing via web playground.
3. Final deliverable = complete frontend from which EVERY feature is explorable, including dev-phase tools (API health checks, endpoint docs) clearly marked "dev-only, removed in production".
4. Latency is a first-class requirement (NFR-1: median ≤900ms, P95 ≤1.5s speech-to-speech).
5. English-only this phase; i18n later.

## 2. Locked decisions (unchanged from PRD §3 unless noted)

Cascaded STT→LLM→TTS on LiveKit Agents; Deepgram STT; Cartesia TTS; fast LLM (Groq preferred, OpenAI fallback) with tool-calling extraction; FastAPI+Postgres+Redis; React frontend; Mumbai region at production.

Changed/new decisions:
- **Telephony**: code stays provider-abstracted; Twilio adapter remains implemented-but-dormant this phase (no calls placed). Production India provider re-decided later (Plivo/Exotel).
- **Multi-tenancy + auth**: organizations, users (email/password, JWT), roles (owner/admin/member). Every entity org-scoped.
- **Agent = first-class DB entity** evolving today's `DomainConfig`: system prompt template, company context blocks, question flow, extraction schema, disclosure script, escalation rules, voice settings. Immutable `agent_versions`; campaigns pin a version.
- **Playground entry point**: browser mic → LiveKit WebRTC room → same pipeline worker used by phone path. Backend issues room tokens; test sessions recorded as `calls(kind='playground')`.
- **RAG-ready, RAG-later**: `knowledge_documents` table reserved now; runtime takes a context-block injection hook so retrieval plugs in without rework.
- **Training** this phase = saving a validated agent config version (v1, v2, …). No fine-tuning.

## 3. Data model delta

New tables:
- `organizations(id, name, slug unique, created_at)`
- `users(id, org_id FK, email unique, password_hash, role, created_at)`
- `agents(id, org_id, name, description, status draft|testing|live, current_version_id nullable, created_at, updated_at)`
- `agent_versions(id, agent_id, version int, system_prompt text, company_context jsonb, question_flow jsonb, extraction_schema jsonb, disclosure_script text, escalation_rules jsonb, voice_settings jsonb, created_by, created_at)`
- `knowledge_documents(id, org_id, filename, mime, storage_key, status)` — reserved, no UI logic yet
- `test_sessions` folded into `calls` via new columns `kind phone|playground`, `org_id`.

Altered tables: `campaigns.org_id`, `campaigns.agent_version_id` (+ legacy `domain_config_id` kept read-only), `contacts.org_id`, `calls.org_id/kind`, `transcripts`, `extracted_fields`, `consent_records` inherit org via call/campaign lineage (denormalized org_id added where queries need it).

## 4. API surface (contract — frontend & voice-agent build against THIS)

Auth (cookie-less JWT bearer):
- `POST /api/auth/register` {org_name,email,password} → org + owner user + token
- `POST /api/auth/login` → token; `GET /api/auth/me`
- All routes below require `Authorization: Bearer <jwt>`; org scoping enforced server-side.

Agents:
- `GET/POST /api/agents`, `GET/PATCH/DELETE /api/agents/{id}`
- `POST /api/agents/{id}/versions` {…config…} → validates (reuse domain_config_schema rules), returns immutable version
- `GET /api/agents/{id}/versions`, `GET /api/agent-versions/{vid}`

Playground:
- `POST /api/playground/sessions` {agent_version_id} → {room_name, livekit_token, call_id}; creates call row kind=playground
- `POST /api/playground/sessions/{call_id}/complete` → finalizes transcript+extraction summary response

Campaigns/contacts/export/dialer: existing routes, now org-scoped; campaign create accepts `agent_version_id`.

Dev-tools (marked dev-only):
- `GET /api/health` {db,redis,voice_agent,providers_configured}
- `GET /api/dev/status` — provider-key presence booleans (never values), calling-hours window, CPS limits
- `GET /api/docs` — FastAPI OpenAPI/Swagger (already free)

Voice-agent ↔ backend internal (existing pattern, service-token protected):
- `GET /internal/agent-config?version_id=` → full config for runtime
- `POST /internal/calls/{call_id}/transcript-turns`, `/extracted-fields`, `/latency-metrics`

## 5. Voice agent runtime (the big build)

`voice-agent/agent.py` entrypoint (livekit.agents Worker):
- Accepts jobs for rooms prefixed `playground-<org>-<uuid>` and (dormant) `twilio-*`.
- Pipeline: Deepgram STT (turn detection/end-of-speech) → LLM (Groq llama-3.3-70b versatile default; function tools `record_extracted_field(field,value,confidence)`, `end_call(summary)`) → Cartesia TTS. Barge-in via LiveKit VAD.
- Loads config by version_id from backend internal API (cached 30s); renders system prompt from template + company_context + disclosure script injected as mandatory first utterance.
- Extraction rule (FR-12): confidence <0.6 or unfilled required field after N=3 asks → graceful wrap + flag, never fabricate.
- Latency instrumentation per turn: stt_final_ms, llm_first_token_ms, tts_first_audio_ms, e2e_ms → POST to internal API; log line per turn.

## 6. Frontend (deliverable the owner reviews)

Pages: Login/Register → Dashboard (feature map cards explaining each area) → Agents (list/detail/builder wizard with step-by-step explanations) → Playground (mic connect via livekit-client, live captions, post-call transcript + extracted fields + latency panel) → Campaigns (list/detail/create w/ contact upload+mapping) → Calls (detail w/ transcript, fields, audio if any) → Dev Tools ("DEV ONLY — remove in production" banner: health checks w/ live status dots, endpoint catalog, provider config checklist, latency glossary). Every page carries one-paragraph plain-English explanation of what it does (owner requirement).

## 7. Error handling & testing

- Config validation errors surface inline in builder wizard (field-level messages from Pydantic schema).
- Playground failure modes: token fetch fail → retry banner; room disconnect → auto-reconnect once then error card; partial transcripts always saved (NFR-3).
- Tests: pytest for auth scoping (cross-org access = 404), agent version immutability, config validation; voice-agent unit test for prompt rendering + extraction escalation; manual web-test checklist in README.

## 8. Non-goals this phase

No Twilio outbound placement, no billing/plans, no SSO, no RAG ingestion UI, no Telugu/i18n, no DLT submission work beyond keeping consent fields intact.

## 9. Build lanes (parallel agents, contracts above are frozen)

A backend-agent: app factory wiring, auth/orgs/JWT, agents+versions CRUD, playground sessions, health/dev endpoints, org-scoping migration, sanitize .env.example.
B voice-pipeline-agent: agent.py runtime per §5 + latency metrics.
C frontend-agent: everything in §6 against §4 contract (mockable until A lands).
D devops-agent: Dockerfiles (backend/frontend), compose fix (working uvicorn target `app.main:app`), local LiveKit dev instructions, README runbook.
E qa-eval-agent: pytest suites per lane A/B contracts + latency harness script for playground turns.
Integration order: A+B merge first (internal API handshake), C rebases onto live API, D+E validate end-to-end web test.
