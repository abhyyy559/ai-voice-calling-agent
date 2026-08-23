# Project Log

## 2026-08-23

- Created `absent-student.json` in `domain-configs` directory.
- Created `schema.json` in `domain-configs` directory.
- Created `domain_config_schema.py` in `backend` directory.

---

# AI Voice Calling Agent Project Log

## Project Overview
- **Objective**: Build a domain-independent AI voice calling platform for India (English-first).
- **Phase**: Phase 0 - Scaffolding (Milestone M0 completed).
- **Next Milestone**: M1 - Single domain config, single call.
- **Tech Stack**: FastAPI, LiveKit Agents, Twilio, Deepgram, Cartesia, PostgreSQL, Redis.

## Current Progress (2026-08-23)

### Completed Tasks (M0 - Scaffolding)
1. **Repo Structure & Setup**
   - Created directory structure: `/backend`, `/voice-agent`, `/frontend`, `/domain-configs`, `/infra`.
   - Generated `.env.example` with all required environment variables.
   - Configured `.gitignore` for Python/Node.js development.

2. **Infrastructure**
   - Docker Compose setup for Postgres, Redis, and services.

3. **Backend (FastAPI)**
   - SQLAlchemy models for PRD entities (`contacts`, `campaigns`, `calls`, etc.).
   - Basic `main.py` with DB session setup.
   - Alembic migration script for initial schema.

4. **Voice Pipeline (LiveKit Agents)**
   - Agent connects to "test-room" and speaks TTS line via Cartesia.
   - Docker-ready with `Dockerfile` and `requirements.txt`.

5. **Telephony (Twilio - migrated from Plivo)**
   - Webhook endpoint and API route for outbound test calls.
   - Voice-agent integration for call audio handling.
   - Twilio trial account created, test call placed successfully.

### Completed Tasks (M1 - Single Domain Config & Call Pipeline) - IN PROGRESS
1. **Domain Configuration System** ✅
   - Created `domain-configs/absent-student.json` - First use case: "Absent Student Follow-up"
   - Created `backend/domain_config_schema.py` - Pydantic validator for domain configs
   - Includes: system_prompt, mandatory AI disclosure (FR-11), question_flow, extraction_schema, escalation_rules, fallback_responses

### Next Immediate Steps
1. **Task 2**: Build cascaded STT-LLM-TTS pipeline in LiveKit Agents service
   - Integrate Deepgram STT
   - Integrate Groq/OpenAI LLM with function calling for extraction
   - Integrate Cartesia TTS
   - Load domain config at runtime
   - Handle end-of-turn detection and barge-in

2. **Task 3**: Implement backend call session & extraction API endpoints
   - Domain-config CRUD endpoints
   - Single-call trigger endpoint
   - Twilio webhook integration with database recording
   - Call event, transcript, and extraction field recording

3. **Task 4**: Implement campaign dialer with Redis queue and rate limiting
   - Redis-backed queue
   - CPS rate-limiting
   - Concurrency control
   - Calling-hours enforcement (9AM-9PM IST)
   - Retry logic

4. **Task 5**: Build React frontend admin dashboard
   - Contact upload (CSV/XLSX)
   - Campaign creation/launch
   - Test call trigger
   - Live campaign status view
   - Call transcript/extracted fields viewer
   - CSV export

## Time Estimates
- **Total Project Duration**: 6-8 weeks (from scaffold start).
- **Time Remaining**: ~5-7 weeks (after M0 completion).
- **M1 Estimate**: 1-2 weeks (single-call workflow).

## Troubleshooting & Notes
- **Docker/Docker Compose**: Ensure Docker Desktop is installed and running. Use `docker compose up` (without hyphen) if using Docker 20.0+.
- **LiveKit Agent**: Ensure LiveKit server is running and accessible.
- **Twilio Integration**: Requires valid test phone number. User provided: `+919391470646`
- **Database**: Run migrations after Docker setup (`alembic upgrade head`).

## Preview & Artifacts
- **Docker Compose**: `infra/docker-compose.yml`.
- **Backend Code**: `backend/models.py`, `backend/main.py`, `backend/twilio.py`, `backend/domain_config_schema.py`.
- **Voice Agent**: `voice-agent/agent.py`, `voice-agent/twilio_media.py`.
- **Domain Configs**: `domain-configs/absent-student.json`.
- **Telephony**: `backend/twilio.py`.

## User Actions Needed
- ✅ **Test phone number** provided: `+919391470646`
- ✅ **Twilio trial account created** with Gmail (`abhyyy559@gmail.com`)
- ✅ **Test call placed** from Twilio trial number `+17372508034` → `+919391470646` (status: queued)
- ✅ **Telephony code refactored to Twilio** (replaced Plivo integration)
- **Next**:
  1. **Add Twilio credentials** to `.env` (SID, Auth Token, Phone Number)
  2. **Add Deepgram API Key** to `.env`
  3. **Add Cartesia API Key** to `.env`
  4. **Add Groq API Key** to `.env`
  5. **Add LiveKit credentials** to `.env`
  6. **Start services** via Docker Compose: `docker compose -f infra/docker-compose.yml up --build`
  7. **Place test call** via Twilio Console or API

---

## Telephony Provider Change (2026-08-15)
- **From**: Plivo (requires corporate email - blocked)
- **To**: Twilio (accepts personal Gmail, $15 trial credit, India numbers available)
- **Status**:
  - Twilio trial call successfully placed via Console (call SID: `CA63cbe92c0a74513f880bd7b52f45f2a7`)
  - Backend and voice-agent refactored to use Twilio SDK
  - Docker Compose ready for local testing

## Domain Config Architecture (NEW - 2026-08-23)
Per user requirements: The platform is **domain-independent**. Users can:
1. **Configure agents** via web UI (system prompt, question flow, extraction schema, escalation rules)
2. **Test agents** in-browser via simulated calls
3. **Launch campaigns** with contact lists
4. **Use cases**: Sales, lead qualification, surveys, appointment reminders, debt collection, absent student follow-up, etc.

The `domain-configs/` directory holds versioned JSON configs. The `backend/domain_config_schema.py` validates them. The voice agent loads configs at runtime - no code changes needed for new use cases.

---

## Enterprise Platform Lanes Merged + Real-Key Local Stack (2026-08-24)
- **Merged**: all enterprise-platform lanes (auth/tenancy, agents + immutable versions, in-browser playground, campaigns, dev tools) into `master`; frontend design language extended across auth/wizard/playground/dev-tools screens.
- **Real-key local stack (no Docker) brought up**:
  - LiveKit server binary vendored at `tools/livekit/livekit-server.exe`, running on :7880 with devkey credentials from root `.env`.
  - FastAPI backend on :8000 against SQLite (`backend/voice_agent.db`), voice-agent worker registered with LiveKit (logs: `worker_out.log`), React app on :3000.
  - New one-command launcher: `scripts/dev-local.ps1` (idempotent — skips anything already listening; polls `/api/health`; PS 5.1 compatible).
- **Campaign-launch 422 fixed**: root cause was NOT a request/body mismatch — `POST /api/campaigns/{id}/launch` takes no body and the 422s were the endpoint's own guards firing after a post-midnight-IST test click (calling window is 09:00–21:00 IST). Frontend now pre-checks the IST window + empty roster, disables Launch with a plain-English banner, and translates server guard details to friendly messages. Contract pinned by new tests in `backend/tests/test_campaign_launch.py`.
- **Docs**: beginner-friendly golden-path guide added at **`docs/USER_GUIDE.md`**.
- **Known limitations**:
  - Redis is absent locally → dialer queue features degraded (no distributed rate-limiting / queue backpressure).
  - Twilio integration dormant pending owner go-signal (code present, credentials not wired for outbound).
  - `OPENAI_API_KEY` is a placeholder in `.env` — Groq (`llama-3.3-70b-versatile`) is the LLM actually used.

---

**Log Format**: This file will be updated after each major conversation/milestone with:
- Clear task completion status.
- Technical decisions made.
- Troubleshooting steps.
- Time estimates and progress tracking.
- User actions required.

**Last Updated**: 2026-08-24 by Claude Code.