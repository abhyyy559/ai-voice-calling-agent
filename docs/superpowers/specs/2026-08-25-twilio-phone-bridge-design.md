# Twilio Phone Bridge — Design

Date: 2026-08-25 · Status: Approved direction (owner: "Yes, build it now") · Scope: unlock real outbound calls

## Goal

Make `/api/test-call` dial a real phone number and connect it to the conversational
agent: caller hears the agent, agent hears the caller (STT/extraction/barge-in all
inherited from the playground pipeline), call ends cleanly, transcript + extracted
fields + recording land in the DB and XLSX export.

## Current state (audited today)

- `TwilioClient.place_call()` works (REST create, status/recording callbacks wired)
- `/twilio/voice` returns TwiML `<Connect><Stream url="{PUBLIC_WS_BASE_URL}/media">`
  — **nothing serves `/media`** → calls connect silent and drop
- Worker accepts ONLY `playground-*` rooms; phone path dormant by design comment
- Playground pipeline (run_session) is metadata-driven `{version_id, call_id, contact}`
  and fully reusable for phone rooms

## Architecture decision

**The bridge lives in the BACKEND**, not the voice-agent container.

Rationale: uvicorn natively supports WebSocket routes; the backend image already has
the `livekit` SDK (rtc + api); port 8000 is already published/tunnel-able. One public
tunnel then serves BOTH Twilio HTTP webhooks AND the wss media stream. No new
container ports, no second tunnel, no threading tricks in the LiveKit worker.

```
Twilio ──PSTN──> callee phone
   │ REST create (place_call)
   │ POST /twilio/voice  ──> TwiML <Connect><Stream wss://{PUBLIC_BASE_URL}/twilio/media>
   │ POST /twilio/status|recording
   └──WSS /twilio/media ──> TwilioMediaBridge ──rtc.Room("phone-{call_id}")──> DomainCallAgent session
```

## Components

### 1. `app/services/g711.py` (backend) — μ-law codec, pure functions
- `ulaw_to_pcm16(bytes) -> bytes` / `pcm16_to_ulaw(bytes) -> bytes` wrapping
  `audioop` (py3.11 stdlib; backend image = python:3.12-slim ✓)
- `downsample_pcm16(bytes, factor=6) -> bytes` naive decimation 48k→8k (agent track)
- Unit tests: silence roundtrip, known-vector roundtrip SNR sanity, length math

### 2. `app/routers/twilio.py` — add `WS /twilio/media`
Accepts Twilio Media Streams protocol:
- `connected` / `start` (grab `start.parameters.call_id`, streamSid) → validate Call row exists
- Join LiveKit room `phone-{call_id}` as identity `twilio-{sid8}` (token minted from settings)
- Publish `rtc.AudioSource(sample_rate=8000, channels=1)`; spawn two pumps:
  - **to-agent**: ws `media` events → b64 decode → ulaw_to_pcm16 → `source.capture_frame`
    (20 ms framing = 160 samples, Twilio sends exactly that)
  - **from-agent**: subscribe remote agent audio (48k mono PCM16 frames) →
    downsample ×6 → pcm16_to_ulaw → b64 → `{"event":"media","streamSid":…,"media":{"payload":…}}`
- `stop` event or ws disconnect → leave room, cancel pumps (per-call task registry,
  multiple simultaneous calls safe)

### 3. Worker accepts phone rooms — `voice-agent/agent.py`
- Extract pure helper `app/rooms.py`: `is_handled_room(name) -> bool`
  (True for `playground-*` and `phone-*`) + unit test (offline-importable)
- Entrypoint uses it; everything downstream (run_session) unchanged — metadata
  arrives identically because the backend packs it onto the room

### 4. Backend test-call flow — `routers/test_call.py`
- `TestCallRequest` += optional `agent_version_id`; resolution order: explicit →
  latest AgentVersion in caller's org → 404 if none
- After successful `place_call`:
  - resolved version persisted on the Call row (`calls.agent_version_id`)
  - room_name = `phone-{call.id}`; when Twilio answers and opens the media WS, the
    backend mints the bridge's join token carrying metadata
    `{"version_id", "call_id", "contact"}` — the bridge's implicit room join creates
    the LiveKit room, and `run_session`'s existing participant-metadata fallback
    picks the payload up (no separate create_room call needed)
  - failure of dial ⇒ call marked failed exactly as today
- Response += `room_name`

### 5. Config & env (backend Settings — names unchanged consumers)
- `PUBLIC_BASE_URL` (https tunnel) — feeds webhook URLs (existing)
- Media WS URL derived: existing `media_ws_base_url` property already falls back to
  `PUBLIC_BASE_URL` scheme-swapped → **no new env vars**
- Compose: no port changes (backend :8000 already published)

## Tunnel (owner-run, documented in run book)

Single tunnel suffices: `cloudflared tunnel --url http://localhost:8000` (or ngrok)
→ set `PUBLIC_BASE_URL=https://<given-host>` in `.env`, restart backend.

## Verification

1. New unit tests green: g711 roundtrips, media-event parser, room-name filter,
   test-call creates room (LiveKitAPI mocked)
2. Full backend suite stays green (84 → ~92)
3. Manual E2E (owner + credentials in `.env`): place call via UI Test page →
   owner's verified Indian mobile rings → answers → hears disclosure → conversation
   → either side hangs up → Call Detail shows transcript/fields/recording → export XLSX

## Out of scope (tracked elsewhere)

Six tester-feedback conversation fixes (opening flow, barge-in tuning, repetition,
STT latency, voice warmth) — separate approved queue, built after this lands.
Indian DID numbers (Plivo/Exotel) — production phase.
