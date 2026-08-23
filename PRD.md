# Product Requirements Document — AI Voice Calling Agent (India, English-first)

Status: Draft for build kickoff · Owner: [your name] · Last updated: 2026-08-15
Companion doc: `AI_Voice_Calling_Agent_India_Research.md` (market/vendor research this PRD is built on)

## 1. Problem & goal

Build a real-time AI voice calling platform that places outbound phone calls and conducts natural, low-latency conversations — not a basic IVR bot. Phase 1 ships English only. The platform must be **domain-independent**: the first proven use case is a college calling students who were absent and asking why, but the architecture must not hardcode that use case.

**Non-goals for Phase 1:** Telugu/multilingual support, authentication/authorization, human-agent handoff/live transfer, production-scale hardening, and self-hosting the voice infra (use managed LiveKit Cloud or Pipecat Cloud first).

## 2. Users

- **Administrator** — uploads a contact list, reviews it, launches a calling campaign, monitors call status, reads transcripts/summaries, exports results. No technical skill assumed.
- **Call recipient** — a person answering the phone. Never sees the admin UI. Must hear a clear AI-disclosure at call start (regulatory requirement, see §8).

## 3. Locked architecture decisions

These are **decided**, not open questions — do not re-litigate them without a documented reason. Rationale is in the research doc.

| Decision | Choice | Why (one line) |
|---|---|---|
| Voice pipeline architecture | **Cascaded** (STT → LLM with tool-calling → TTS), not speech-to-speech | Structured field extraction needs an auditable text layer and reliable tool-calling |
| Real-time orchestration | **LiveKit Agents** (fallback: Pipecat) | Solves session concurrency, WebRTC/SIP, turn-taking, barge-in as first-class primitives — don't rebuild this |
| Telephony (India) | **Plivo** for prototype (fallback: Exotel for compliance-handled option) | Cheapest, LiveKit/Pipecat-native, fast DID provisioning; avoid Twilio for India-domestic economics |
| STT (English) | **Deepgram** (Flux model for built-in turn detection; Nova-3 as fallback) | Purpose-built for voice agents, lowest end-of-speech latency |
| TTS (English) | **Cartesia Sonic** | Lowest time-to-first-audio of any mainstream provider |
| LLM | **Fast/cheap model by default** (Groq-hosted Llama 3.3-class or GPT-4o-mini-class), with deterministic escalation rules for ambiguous turns — not a large model on every turn | Latency + cost; the task is intent classification/slot-filling, not deep reasoning |
| Backend | **FastAPI** (Python) | Same language as the voice pipeline (LiveKit Agents/Pipecat are Python) |
| Database | **PostgreSQL** | Relational, reporting-heavy workload; no need for a vector DB at this stage |
| Session/queue state | **Redis** | Call session state + outbound dialer rate-limiting queue |
| Frontend | **React** admin dashboard | Standard, matches contractor/agent availability |
| Hosting region | **India (Mumbai)** cloud region | DPDP data-localization alignment |
| Telugu stack (Phase 2, not now) | **Sarvam AI** (Saaras v3 STT, Bulbul V3 TTS) | Only India-first vendor with real Telugu code-switching support — do not try to stretch the English stack to Telugu |

## 4. Functional requirements

### 4.1 Admin web app
- FR-1: Upload a CSV/XLSX contact list with configurable column mapping (name, phone, ID, custom fields).
- FR-2: Review/edit the parsed contact list before launching a campaign; flag rows with invalid phone numbers.
- FR-3: Define a **campaign** = contact list + a **call domain config** (see 4.3) + schedule window (must respect the 9 AM–9 PM calling-hours rule, see §8).
- FR-4: Launch, pause, and cancel a campaign.
- FR-5: Live campaign dashboard: per-contact status (queued / calling / answered / no-answer / busy / failed / completed), running counts.
- FR-6: Per-call detail view: transcript, AI-generated structured summary, audio recording link, duration, timestamps.
- FR-7: Export campaign results as CSV/XLSX with all structured fields plus status/duration/transcript-link columns.

### 4.2 Voice agent (real-time call handling)
- FR-8: Place outbound calls via the telephony provider; handle answered/no-answer/busy/failed states.
- FR-9: Conduct a conversation per the active call domain config: ask configured questions, listen, handle interruptions/barge-in, detect end-of-turn, hold context across turns.
- FR-10: Extract structured fields via LLM tool-calling per the call domain config's schema (e.g., `reason_for_absence`, `expected_return_date`).
- FR-11: Disclose at call start that the caller is speaking with an automated system (regulatory requirement).
- FR-12: Escalate to a defined fallback (end call gracefully, flag for human follow-up) when the LLM's confidence is low or the extraction schema can't be filled after N attempts — never fabricate a value.
- FR-13: Record the call (subject to consent/compliance rules in §8), generate a transcript and a structured summary, and write all of it to the database before marking the call complete.

### 4.3 Call domain config (this is what makes the platform domain-independent)
A domain config is a versioned JSON/YAML file, not code, containing: the question flow (ordered, with allowed branching), the structured-field extraction schema (name, type, required/optional), the disclosure/consent script, escalation rules, and a system-prompt template. The "absent student" use case is the first config, not a hardcoded flow. **Acceptance test for this requirement: adding a second call-domain use case must require zero changes to the voice-pipeline or backend code — only a new config file.**

### 4.4 Outbound campaign dialer
- FR-14: Rate-limit outbound call placement to the telephony provider's CPS/concurrency limit (configurable).
- FR-15: Retry policy for no-answer/busy (configurable max attempts, backoff).
- FR-16: Independent conversation state per concurrent call — no shared mutable state between calls.

## 5. Non-functional requirements

- NFR-1 (Latency): median end-of-caller-speech-to-start-of-agent-speech ≤ 900ms; P95 ≤ 1.5s. Instrument and log this per call from day one — it's a target to tune against, not a one-time check.
- NFR-2 (Concurrency): Phase 0/1 target = 10 concurrent calls without degradation. Design so raising this later is a config/infra change, not a rewrite (see LiveKit Agents choice above).
- NFR-3 (Reliability): a crashed/dropped call must not corrupt campaign state; partial call data (whatever was captured before the drop) must still be saved.
- NFR-4 (Auditability): every structured-field extraction must be traceable to the transcript turn(s) it came from.
- NFR-5 (Compliance): see §8 — DLT registration, consent capture, disclosure, data retention/deletion are launch-blocking, not post-launch hardening.
- NFR-6 (Cost visibility): log per-call cost (telephony + STT + LLM + TTS) so the admin dashboard can eventually show cost-per-campaign.

## 6. Data model (starting point — refine in `backend-agent`)

- `contacts` (id, campaign_id, name, phone, external_id, custom_fields jsonb, status)
- `campaigns` (id, name, domain_config_id, schedule_window, status, created_at)
- `domain_configs` (id, name, version, question_flow jsonb, extraction_schema jsonb, disclosure_script, escalation_rules jsonb)
- `calls` (id, contact_id, campaign_id, provider_call_id, status, started_at, ended_at, duration_seconds, recording_url)
- `call_events` (id, call_id, event_type, payload jsonb, timestamp) — raw provider webhook log
- `transcripts` (id, call_id, turn_index, speaker, text, timestamp)
- `extracted_fields` (id, call_id, field_name, field_value, source_turn_index, confidence)
- `consent_records` (id, contact_id or phone, consent_type, captured_at, source)

## 7. System architecture (text form)

```
Admin (browser) ──> Frontend (React) ──> Backend API (FastAPI)
                                              │
                          ┌───────────────────┼───────────────────┐
                          ▼                   ▼                   ▼
                     Postgres            Redis (session/     Outbound dialer
                  (contacts, calls,       queue state)         (rate-limited
                  transcripts, etc.)                            worker)
                                                                    │
                                                                    ▼
                                                          Telephony provider
                                                          (Plivo/Exotel)
                                                                    │
                                                                    ▼
                                                    Voice pipeline (LiveKit Agents)
                                                    STT (Deepgram) → LLM (tool-calling)
                                                    → TTS (Cartesia) → back to caller
                                                                    │
                                                                    ▼
                                                   Writes transcript/extracted fields
                                                   back to Postgres via Backend API
```

## 8. Compliance requirements (launch-blocking — do not defer)

- DLT Principal Entity registration and correct number-series classification before any real (non-test-number) outbound calling. The classification for "institutional/administrative call to an existing student" is a genuine gray area — confirm with the DLT-registration provider or counsel before the first real campaign (see research doc §10).
- Consent capture: build a consent flag into the contact/enrollment data model (`consent_records` table above) — do not call anyone without a recorded consent basis.
- Mandatory AI self-disclosure at the start of every call (FR-11).
- Calling-hours restriction: 9 AM–9 PM local time, enforced by the campaign scheduler, not left to the admin to remember.
- Data localization: audio/transcripts processed and stored in India (hosting decision in §3 already reflects this); verify each third-party API (STT/TTS/LLM provider) processes data in-region or document the exception.
- Defined retention period for recordings/transcripts with an automated deletion job — do not keep everything indefinitely by default.

## 9. Success metrics (Phase 0/1)

- ≥ 90% of test calls connect successfully (telephony reliability).
- Median turn-taking latency ≤ 900ms measured across ≥ 50 real test calls (not scripted demo calls).
- ≥ 85% of structured-field extractions match a human reviewer's read of the same transcript (accuracy check, run manually on a sample each sprint).
- False-interruption rate (agent talks over the caller) ≤ 10% on a 20-call real-conversation test set.
- Zero calls placed without a recorded consent basis.

## 10. Milestones

- **M0 — Scaffold**: repo structure, docker-compose local dev, all provider accounts created (Plivo/Exotel, Deepgram, Cartesia, LLM/Groq), `.env` wired, empty end-to-end call (agent says one line, hangs up) working on a real phone.
- **M1 — Single domain config, single call**: full "absent student" question flow working on one outbound test call, transcript + extraction + export working end-to-end.
- **M2 — Campaign dialer**: CSV upload → review → launch → concurrent calls (target 10) → live dashboard → export.
- **M3 — Compliance gate**: DLT registered, consent flow live, disclosure script live, retention job live. **This gates any real (non-test-number) campaign.**
- **M4 — Hardening**: latency/turn-detection tuning against real call recordings, eval harness, cost logging.
- **M5 (Phase 2, separate PRD)**: Telugu via Sarvam.

## 11. Open questions to resolve during build (not blocking scaffold)
- Exact DLT number-series classification for the education use case (needs provider/legal confirmation).
- Which LLM provider hosts the "fast/cheap" model in production (Groq vs. an OpenAI/Anthropic small model) — prototype both, decide on measured latency/accuracy on your own call audio, not vendor benchmarks alone.
- Recording retention period (needs an institutional policy decision, not just a technical default).
