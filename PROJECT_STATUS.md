# Project Status — AI Voice Calling Agent ("VocalIQ")

Last updated: 2026-08-25 · Phase: **1 COMPLETE (closed out)** · See `git log` for head.

---

## 1. What works TODAY (all verified end-to-end)

| Capability | Proof |
|---|---|
| Multi-tenant orgs + JWT auth, per-org isolation | 77 backend tests green |
| Agent builder (6-step wizard → immutable versions) | Adding a use case = new version, zero code |
| **Voice playground**: mic → Deepgram STT → Groq LLM (tool-calling) → Cartesia TTS on LiveKit; agent speaks first; live captions | E2E harness PASS |
| **Text playground** (typed testing) | Live curl verified incl. extraction |
| Field extraction in both modes | voice: 3 fields @0.8–0.9 conf; text: 2 fields |
| Personalization inputs per contact | `sample_campaign_contacts.csv` ships `student_name/parent_name/class_section` columns for prompt injection |
| Campaign import w/ auto column-mapping, 9–9 IST guardrails, transcripts, export | UI flow complete |
| Analytics overview + Vapi-style dark UI (sidebar shell, agent workspace split-view, call history table) | `/api/analytics/summary` live |
| Voice & model pickers per agent (8 Cartesia presets + LLM choice) | persisted via `voice_settings` |
| Anti-noise interruption hardening | stricter VAD (0.6 threshold), min_interruption 350ms, resume_false_interruption |
| Dev Tools console (health, provider checklist, full endpoint catalog) | footer "Dev" link, hidden in prod builds |

## 2. Latency — measured vs targets (your last session)

| Metric | Your avg | Target | Diagnosis / next fix |
|---|---|---|---|
| STT final | 1671ms (p95 2674) | ≤900 | Dominated by end-of-speech detection silence + Deepgram finalization. Next: tune Deepgram `endpointing`, consider nova-2 streaming config, and measure `transcription_delay` separately from EOU delay |
| LLM first token | 1393ms (p95 2867) | ≤400 | qwen+no-reasoning median is ~260–900ms; p95 spike = Groq free-tier variance/cold calls. Next: Groq Dev tier + keep tool-loop to 1 step (`max_tool_steps=1`) |
| TTS first audio | 126ms | ✅ | Cartesia is fine |
| **End-to-end** | 2739ms (p95 3707) | ≤1500 | Sum of above; STT is the biggest lever |

Also noted from transcript: the demo agent addressed a non-parent as parent ("your child") because seeded config lacks the verify-step + personalized context wiring — see P0-2.

## 3. Pending — P0 (this phase)

- [x] **P0-1 STT latency**: DONE — Deepgram `endpointing_ms=200` shipped (commit `7d28763`); EOU vs transcription delay split logged in turn_latency. Fresh live measurement still owed at next test-call session.
- [x] **P0-2 Personalized opening**: DONE end-to-end (commit `6b24f86`) — contact fields persist on calls.context, packed into room/token metadata, CALLER CONTEXT prompt section + verify-relationship rule in voice + text modes, migration 0003.
- [x] **P0-3 Strict-guardrails block** in every prompt: refuse off-topic questions ("Who is India's PM?"), never disclose other students' data, wrap up fast (calls cost money), offer human handoff when caller drifts or demands more help
- [x] **P0-4 Caption lag in audio mode**: publish partial transcripts (not just finals) over the data channel
- [ ] **P0-5 Groq Dev tier** (owner action) to remove p95 spikes + TPM 429s

## 4. Pending — P1

- [ ] Parallel outbound calling demo (3–4 simultaneous) — BLOCKED on owner: Twilio keys/tunnel; dialer concurrency already built
- [x] Cost dashboard: org-scoped GET /api/analytics/costs + "Est. Spend" card on Overview ($/min constants in analytics.PRICING_USD_PER_MINUTE — update per invoice)
- [x] Export v2 columns: call status/duration/extracted fields/custom fields + E2E Latency column (shipped commit `0d3087f`)
- [x] Landing page motion pass: scroll-reveal + glassmorphism accents, prefers-reduced-motion safe (public mic demo intentionally deferred — new auth surface)
- [x] Frontend container healthcheck IPv6 false-negative fix

## 5. Phase 2 roadmap (agreed, not started)

1. **Telugu + Indian regional languages** via Sarvam (Saaras STT / Bulbul TTS) — separate pipeline profile per language
2. **Bring-your-own providers**: org-level settings page where users paste their own STT/TTS/LLM API keys (Deepgram/Cartesia/Groq/OpenAI/Sarvam/ElevenLabs…) — runtime resolves per-org provider chain; positions product as fully open-source, vendor-neutral alternative to ₹2–12/min incumbents
3. Phone-number purchasing flows per org (Plivo/Exotel re-evaluation for India domestic)
4. Human-agent live transfer
5. Auth hardening (SSO, roles granularity), production hosting (Mumbai region), DLT registration workflow assistant

## 6. Skills note

- `ui-ux-pro-max` skill IS installed locally and informed the current dark design tokens.
- An "Apple-design" replica skill does not exist in this environment's registry; Apple HIG principles (generous whitespace, depth via layering not borders, restrained accent color) should guide the next frontend polish pass manually.
- All developer tools are visible at **footer → "Dev"** in dev builds (endpoint catalog = full feature surface). In production builds they are compiled out by design.

## 7. File-cleanup candidates — AWAITING OWNER APPROVAL (nothing deleted)

| File(s) | Purpose | Recommendation |
|---|---|---|
| `uvicorn_out.log` / `uvicorn_err.log` / `worker_out.log` / `worker_err.log` / `livekit_out.log` / `livekit_err.log` | runtime debug logs from local bring-up | delete + gitignore `*.log` |
| `caller.wav` / `caller2.wav` | E2E harness fixtures (regenerable) | keep (small, used by tests) |
| `frontend/dist/*` | committed build artifact | remove from git, add dist/ to .gitignore |
| `backend/models.py` + `backend/main.py` + `backend/twilio.py` (repo-root legacy stubs duplicating `backend/app/*`) | pre-refactor shims kept for compose compat | review then delete shims after compose path check |
| `test_validate.py` | early manual validator | delete after confirming unused |

Reply with which rows to delete and I'll execute.

## 8. Run book (quick)

```
docker compose -f infra/docker-compose.yml up -d --build   # everything
# app :3000 · API :8000/docs · LiveKit :7880
login: demo@example.com / demo1234
E2E test: voice-agent\.venv\Scripts\python.exe scripts\e2e_caller.py --wav caller.wav --wav2 caller2.wav --hold 60
```

## Update 2026-08-25
- [x] P0-3 guardrails block live in all prompts
- [x] P0-4 partial captions streaming (final:false on partials)
- [x] P1 healthcheck IPv6 fix (frontend now healthy)
- [x] Cleanup executed per approval (logs, dist untracked, test_validate.py removed; .gitignore hardened)
- [ ] Still open this phase: P0-1 STT endpointing tuning, P0-2 personalized opening + parent-verify wiring, P0-5 Groq Dev tier (owner), P1 cost dashboard + export v2 + landing motion pass; parallel-calls demo waits on Twilio keys.

## Update 2026-08-25 (closeout #2)

- [x] P0-1/P0-2 marked done (were committed in `7d28763` / `6b24f86`; doc lagged)
- [x] P1 cost dashboard shipped: `/api/analytics/costs` + Overview "Est. Spend" card (81 backend tests green, vite build clean)
- [x] P1 landing motion pass shipped (`useReveal` hook + CSS reveal layer, zero deps, reduced-motion safe)
- [ ] Owner-blocked: P0-5 Groq Dev tier, Twilio keys for parallel-calls demo
- [ ] Queued next: external tool bindings (calendar / appointment booking via agent tool-calling) — design pass pending; Phase 2 roadmap starts in a few days


