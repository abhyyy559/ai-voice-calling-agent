# Cost-Cutter Overhaul — Implementation Approach

**Author:** senior-ai-engineer · **Date:** 2026-08-26 · **Status:** APPROVED direction, ready for orchestration dispatch
**Mandate:** beat the ₹3.5/min multilingual competitor using open-source-first components — multilingual (English + Telugu + Tenglish) calls at ≤₹2/min all-in on Plivo India legs, same product surface.
**Inputs grounded:** `docs/research/telephony-alternatives.md`, `docs/research/multilingual.md`, actual code (`backend/app/services/{telephony,twilio_bridge,g711}.py`, `backend/app/routers/{twilio,test_call}.py`, `backend/app/services/{dialer,calls_service}.py`, `backend/app/main.py`, `backend/app/config.py`, `voice-agent/app/{pipeline,config}.py`, `frontend/src/components/VoiceSettingsForm.jsx`, `.env.example`) + live vendor-doc verification (Plivo `<Stream>`, Sarvam chat-completions) performed 2026-08-26.

---

## 0. Research-vs-code conflicts found while reading — read these first

1. **Sarvam-M is DEPRECATED (multilingual.md §2 recommendation is stale).** Official docs fetched today state: *"Sarvam-M (24B) has been deprecated and is no longer available through the Chat Completions API. Please migrate to Sarvam-30B or Sarvam-105B"* (docs.sarvam.ai Chat Completions Overview, accessed 2026-08-26). This plan targets **`sarvam-105b`** (non-think mode) everywhere multilingual.md says "Sarvam-M".
2. **The two research docs disagree on Plivo cost.** multilingual.md §5 assumes telephony ≈ ₹0.80/min; telephony-alternatives.md lands **₹0.38/min all-in** (plivo.com/voice/pricing/in, Aug 2026, streaming + recording included). This plan uses **₹0.38**; multilingual.md's Σ rows are therefore conservative by ~₹0.42/min.
3. **`voice_settings.stt_language` and `speaking_rate` are dead config today.** The frontend saves them (`frontend/src/components/VoiceSettingsForm.jsx:87` shape `{tts_voice_id, speaking_rate, stt_language, llm_model}`), `/internal/agent-config` returns them (`backend/app/routers/internal.py:114`), but `pipeline._voice_overrides()` (`voice-agent/app/pipeline.py:114-123`) reads only `llm_model` and `tts_voice_id`, and Deepgram language is hardcoded `"en"` (`pipeline.py:144`). Phase B makes these live.
4. **`main.py::_should_run_dialer()` hardcodes the Twilio credential gate** (`backend/app/main.py:34-40`). If we only provisioned Plivo credentials, the dialer silently wouldn't start. Must be made provider-aware in Phase A.
5. **Plivo `<Stream>` bidirectional support: VERIFIED.** Official docs confirm two-way audio for voice-AI: `<Stream bidirectional="true" keepCallAlive="true" contentType="audio/x-mulaw;rate=8000">wss://…</Stream>`; outbound audio via `{"event":"playAudio","media":{"contentType":"audio/x-l16|x-mulaw","sampleRate":8000,"payload":"<base64>"}}`; barge-in flush via `clearAudio` control event; Plivo retries a dropped WS twice before disconnecting (plivo.com/docs/voice/xml/audio-streaming; plivo.com/docs/voice-agents/audio-streaming/xml/stream, upd. 2026-07-17; old-support.plivo.com Audio Stream FAQ). Constraints: with `bidirectional=true`, `audioTrack` cannot be `outbound`/`both` (caller-audio only); **default contentType is `audio/x-l16;rate=8000` PCM, NOT mulaw** — we set mulaw explicitly so `g711.py` is reused unchanged; **`extraHeaders` allows only `[A-Za-z0-9]` (max 512 B)** — underscore illegal, so `call_id` rides the answer_url query string instead (we generate the answer XML per call, same pattern as `_voice_webhook()` today).
6. **Protocol deltas vs Twilio Media Streams** (drives Phase A parser work): no `"connected"` greeting frame (first frame is `start`); metadata lives at `start.callId` / `start.streamId` (not `streamSid`/customParameters); outbound event is `playAudio` (not `media`); signature header is `X-Plivo-Signature-V3` (not `X-Twilio-Signature`). Structurally still "base64 8 kHz mulaw over WSS with start/media/stop events" — our bridge pumps survive almost intact.
7. **`docs/research/cost-engineering.md` does not exist** despite being referenced by my operating rules — the ₹/min ledger below follows the conventions of the two research docs that do exist (ex-GST, FX ₹87/$, connected-minute billing). Creating that ledger file should be a follow-up for devops/backend.
8. **Scope guardrail:** CLAUDE.md says "don't start Telugu/Sarvam work — that's Phase 2." This approved mandate *is* the Phase-2 kickoff; Phases B/C remain execution-gated behind Phase D acceptance numbers regardless.
9. **Path choice note:** telephony-alternatives.md recommends self-hosted `livekit/sip` (Path A). The mandate directs the Plivo XML `<Stream>` bridge instead — the correct near-term call: it reuses our existing Media-Streams-style bridge (~days, not weeks), keeps every rupee of the ₹0 streaming fee (free on Plivo either way), and leaves `livekit/sip` as the >50-concurrent scale option. Revisit only when PAYG concurrency caps bind (§Risk R7).

---

## 1. Target end-state

VocalIQ places outbound calls on Plivo Indian 160-series legs (₹0.38/min, streaming/recording/AMD included, media anchored in India) through a provider-neutral `TelephonyClient` seam selected by `TELEPHONY_PROVIDER`, with Twilio kept warm as an instant-revert fallback; the cascaded LiveKit pipeline resolves its STT/LLM/TTS per immutable AgentVersion from `voice_settings` — Deepgram/Groq/Cartesia remain the platform defaults for English agents, while Telugu/Tenglish agents select Sarvam Saaras-v3 STT + `sarvam-105b` (non-think) + Bulbul-v3 TTS, all reachable behind the same `ProviderBundle` construction and instrumented turn telemetry; qa-eval owns numeric promotion gates (WER, ≥85 % extraction accuracy, ≤900 ms median e2e) so any component flips to default only on evidence and reverts by env flip or a new AgentVersion row — landing multilingual calls at **≈ ₹1.5–2.1/min all-in** (sticker ceiling ≈ ₹3.0, held under ₹2.0 by TTS char discipline + rate negotiation), versus ≈ ₹3.8–5.4 today.

---

## 2. Phased plan (each phase independently deployable AND revertible)

### Phase A — Telephony provider abstraction: `PlivoClient` + Plivo media bridge

**Goal:** dialer/test-call place calls through Plivo; Plivo legs stream into the same `phone-*` LiveKit rooms the voice-agent already serves. Deployable alone; revert = `TELEPHONY_PROVIDER=twilio` + restart (both webhook surfaces stay mounted permanently).

**New modules**

```python
# backend/app/services/plivo_client.py  (mirrors TwilioClient style: lazy import,
# settings injected, logger.info on placement)
class PlivoClient:
    """Production telephony client using the Plivo REST API."""
    def __init__(self, settings: Settings) -> None: ...
    def _answer_webhook(self, call_id: int) -> str:
        # f"{settings.public_base_url.rstrip('/')}/plivo/voice?call_id={call_id}"
        ...
    def place_call(self, to: str, call_id: int) -> str:
        # lazy `from plivo import RestClient`
        # client.calls.create(
        #     src=settings.plivo_phone_number, dst=to,
        #     answer_url=self._answer_webhook(call_id), answer_method="POST",
        #     hangup_url=f"{base}/plivo/status", hangup_method="POST",
        #     machine_detection="true",                      # AMD included on Plivo
        #     record="record-from-answer-dual",              # ⚠ confirm exact kwarg +
        #     recording_callback_url=...,                    #   callback name vs plivo-python at impl
        # )
        # returns CallUUID (str) — stored in Call.provider_call_id like CallSid
        ...

# backend/app/services/plivo_bridge.py  (pure logic + XML builders, unit-testable
# like twilio_bridge.py; reuses MediaEvent dataclass)
PHONE_STREAM_CONTENT_TYPE = "audio/x-mulaw;rate=8000"

def build_answer_xml(ws_base_url: str, call_id: int) -> str:
    # <Response><Stream bidirectional="true" keepCallAlive="true"
    #   contentType="audio/x-mulaw;rate=8000"
    #   statusCallbackUrl="{base}/plivo/stream-status">{ws_base_url}/plivo/media</Stream></Response>
    # call_id reaches the handler via the answer_url QUERY PARAM (extraHeaders
    # charset forbids underscores), not via XML attributes.
def parse_plivo_event(raw: Any) -> "MediaEvent":
    # start: ev.event="start", ev.stream_sid=start.streamId, ev.call_sid=start.callId
    # media: ev.media_payload = media.payload (base64 mulaw — contentType pinned above)
    # stop/dtmf passthrough; NO "connected" frame exists (unlike Twilio)
def build_play_audio(stream_id: str, ulaw_b64: str) -> str:
    # {"event":"playAudio","streamId":sid,"media":{"contentType":"audio/x-mulaw",
    #  "sampleRate":8000,"payload":b64}}   ← Plivo's outbound frame
def build_clear_audio(stream_id: str) -> str:
    # {"event":"clearAudio","streamId":sid}  ← barge-in flush (upgrade over Twilio path)
```

**New router** `backend/app/routers/plivo.py` — mirrors `routers/twilio.py` structure exactly:

- `POST /plivo/voice` (`plivo_voice(request, call_id: int, db)`) — `_check_plivo_signature()` (X-Plivo-Signature-V3 via plivo SDK validator, gated on `settings.plivo_validate_signature`), same Call/contact bookkeeping block as `twilio_voice` (`routers/twilio.py:319-346`), then `Response(build_answer_xml(settings.media_ws_base_url, call_id), media_type="application/xml")`.
- `WS /plivo/media` (`plivo_media(websocket)`) — clone of `twilio_media` (`routers/twilio.py:193-316`) with three deltas: (a) handshake expects `start` first (drop the `"connected"` continue at line 231), `ev.call_id` comes from the `call_id` query param on the upgrade request, `ev.call_sid == call.provider_call_id` replaces the CallSid check (line 247); (b) inbound pump feeds `ulaw_to_pcm16(payload)` → same `_make_frame`/`source.capture_frame`; (c) outbound pump sends `build_play_audio(...)` frames and `build_clear_audio(...)` when the room signals agent interruption. Reuses `_make_frame`, `_drain_track`, `_put_sentinel`, queue/backpressure logic verbatim — extract those three into `backend/app/services/media_bridge.py` and have **both** routers import them (twilio.py behavior unchanged; pure move).
- `POST /plivo/status` — hangup callback; `PLIVO_STATUS_MAP` added beside `TWILIO_STATUS_MAP` in `services/calls_service.py` (Plivo mirrors TwiML status enums: queued/ringing/in-progress/completed/busy/no-answer/failed/canceled — confirm exact strings against first sandbox callbacks), then the same `end_call(...)` branch as `twilio_status` (`routers/twilio.py:349-394`).
- `POST /plivo/recording` — persists `RecordingUrl` onto `Call.recording_url`, mirroring `twilio_recording`.
- Mount in `main.py::create_app` next to `fast_app.include_router(twilio.router)` (line 102), still prefix-less.

**Touch-points on existing code**

- `backend/app/config.py` — add: `telephony_provider: str = "twilio"`, `plivo_auth_id/plivo_auth_token/plivo_phone_number: str = ""`, `plivo_validate_signature: bool = False`; extend `provider_presence` with `"plivo"` and `"telephony_provider"`.
- `backend/app/main.py` — rewrite `_build_telephony()` (lines 26-31) as a registry: build `TwilioClient` iff twilio creds, `PlivoClient` iff plivo creds, always keep `FakeTelephonyClient` fallback; `fast_app.state.telephony_registry: dict[str, TelephonyClient]` + `fast_app.state.telephony = registry[settings.telephony_provider]` (back-compat for `test_call._get_telephony`). Rewrite `_should_run_dialer()` (lines 34-40) to `settings.dialer_enabled and bool(registry-with-real-clients)` — fixes conflict #4.
- `backend/app/routers/test_call.py` — add optional `provider: Optional[str] = None` to `TestCallRequest`; `_get_telephony(request, payload.provider)` resolves from the registry (default = `settings.telephony_provider`). **This is the dual-run lever:** A/B arms on live calls without redeploy.
- `.env.example` — add `TELEPHONY_PROVIDER=twilio`, `PLIVO_AUTH_ID=`, `PLIVO_AUTH_TOKEN=`, `PLIVO_PHONE_NUMBER=` (+160-series placeholder), `PLIVO_VALIDATE_SIGNATURE=false`.
- Tests: `backend/tests/test_plivo_client.py` (fake RestClient injection: URL shapes, sid returned, failure → exception like `test_call_flow.py` pattern), `backend/tests/test_plivo_bridge.py` (XML golden test, `parse_plivo_event` happy/junk/start-no-callid, playAudio/clearAudio frame shapes), extend `test_call_flow.py` with provider-override resolution cases.

**Verification gate A:** unit suite green → sandbox call to own allowlisted number via `POST /api/test-call {provider:"plivo"}` → transcript appears in dashboard, `turn_latency` log lines show nonzero e2e_ms, hangup maps to internal status correctly, recording URL persists, `clearAudio` observed on intentional interruption. Exit: 2 weeks dual-run parity (connect rate within ±5 %, ASR accuracy eyeball-parity on telephony audio) before `TELEPHONY_PROVIDER=plivo` becomes default.

---

### Phase B — Sarvam speech providers (STT/TTS) behind `voice_settings`

**Goal:** Telugu/Tenglish agents run Saaras-v3 STT + Bulbul-v3 TTS; Deepgram/Cartesia stay platform defaults until Phase D promotes otherwise. Revert = save a new AgentVersion without the sarvam keys (immutable-version model makes this trivial) or unset `SARVAM_API_KEY` (graceful degradation path already exists: `bundle.problems`).

**New module** `voice-agent/app/providers_sarvam.py` (livekit-plugins pattern: subclasses of `stt_module.STT` / `tts_module.TTS`, constructed with keys, degrade-by-absence handled in `build_providers`):

```python
class SarvamSTT(stt_module.STT):
    """Saaras v3 streaming ASR over Sarvam's WebSocket API (8 kHz telephony focus)."""
    def __init__(self, *, api_key: str, model: str = "saaras:v3",
                 language: str = "te-IN", codemix: bool = True,
                 sample_rate: int = 16000) -> None: ...
    # implements stream(): emit stt_module.SpeechEvent(interim/final transcripts)

class SarvamTTS(tts_module.TTS):
    """Bulbul v3 streaming synthesis; native 8 kHz mulaw output for telephony rooms."""
    def __init__(self, *, api_key: str, model: str = "bulbul:v3",
                 voice: str, sample_rate: int = 8000) -> None: ...
    # implements synthesize()/stream() yielding rtc.AudioFrame at 8 kHz
```

If a maintained `livekit-plugins-sarvam` package exists at implementation time (research notes "LiveKit/Pipecat integrations exist"), vendor-thin-wrap it instead of hand-writing the WS layer — decide at Task 1, interface above is fixed either way.

**Touch-points on existing code**

- `voice-agent/app/pipeline.py` — replace `_voice_overrides()` tuple with a frozen dataclass and consume it in `build_providers()` (signature unchanged):

```python
@dataclass(frozen=True)
class VoiceOverrides:
    llm_provider: str = ""      # ""|"groq"|"sarvam"
    llm_model: str = ""
    stt_provider: str = ""      # ""|"deepgram"|"sarvam"
    stt_language: str = ""      # "en"|"en-IN"|"te-IN"|...
    tts_provider: str = ""      # ""|"cartesia"|"sarvam"
    tts_voice_id: str = ""

def _voice_overrides(voice_settings: Optional[Mapping[str, Any]]) -> VoiceOverrides: ...

def build_providers(settings: Settings,
                    voice_settings: Optional[Mapping[str, Any]] = None) -> ProviderBundle:
    # STT branch: sarvam if overrides.stt_provider=="sarvam" AND settings.sarvam_api_key
    #             else deepgram.STT(model="nova-3",
    #                 language=overrides.stt_language or "en",   # ← un-hardcodes line 144
    #                 endpointing_ms=200, ...)
    # TTS branch: sarvam if overrides.tts_provider=="sarvam" AND key
    #             else cartesia.TTS(api_key=..., voice=overrides.tts_voice_id or default)
    # missing-key degradation appends to bundle.problems exactly as today
```

  `run_session` (line 642 `config.get("voice_settings")`) needs zero changes.
- `voice-agent/app/config.py` — add `sarvam_api_key: Optional[str]` + `_get("SARVAM_API_KEY")`; extend `provider_problems()` messaging.
- `backend/app/config.py` — add `sarvam_api_key: str = ""` (presence-only, mirrors deepgram/cartesia block, lines 78-84) + `provider_presence["sarvam"]`.
- `backend/app/domain_config_schema.py:118` — `voice_settings` is already free-form `Dict[str, Any]`: **no migration**; optionally whitelist the six keys above to catch typos in AgentBuilder.
- `frontend/src/components/VoiceSettingsForm.jsx` — extend `LANGUAGES` with `te`/`te-IN`; add provider radio pairs (STT: Deepgram/Saaras · TTS: Cartesia/Bulbul) shown when `SARVAM_API_KEY` presence flag is served; add a Bulbul preset section to `VOICE_PRESETS` populated from Sarvam's per-language recommended-speaker mapping (their own docs admit per-language variance — copy their mapping outright per multilingual.md §4). Persist through the existing `{...v.voice_settings}` merge (`AgentBuilderPage.jsx:89`).
- `.env.example` — `SARVAM_API_KEY=`, `SARVAM_STT_MODEL=saaras:v3`, `SARVAM_TTS_MODEL=bulbul:v3`.
- Tests: offline-only (livekit-agents import guard respected — pure logic in `providers_sarvam.py` kept thin): override-parsing tests for `VoiceOverrides` in `voice-agent/tests/` mirroring existing prompting/extraction test layout; contract test asserting `/internal/agent-config` roundtrips the six keys (`backend/tests/_qa_contract.py` pattern).

**Verification gate B:** sandbox Telugu test call end-to-end on a `phone-*` room; `TurnTelemetry` shows `transcription_delay_ms` + `tts_first_audio_ms` populated for the Sarvam path; Telugu script renders in transcript rows and browser captions (`_publish_caption` already UTF-8-safe); barge-in works (Silero VAD is language-agnostic). Exit: hand the arm to Phase D.

---

### Phase C — LLM routing: `sarvam-105b` (non-think) + Groq escalation

**Goal:** per-agent `voice_settings.llm_provider="sarvam"` routes through Sarvam's OpenAI-compatible chat completions; Groq remains default and escalation tier. Revert = AgentVersion re-save or unset provider key. Cost-neutral vs Groq (₹0.05–0.30/min either way) — this phase is quality-driven (Indic Vibe Check 8.12/9), decided by Phase D numbers.

**Endpoint facts (verified today, docs.sarvam.ai):** OpenAI-compatible request/response; **tool calling documented** (`tools`/`tool_choice`, `finish_reason:"tool_calls"`, max 128 tools) — closes part of multilingual.md GAP #2, though LiveKit-framework validation remains the hard gate; auth accepts `Authorization: Bearer <key>` in addition to `api-subscription-key` (so `livekit.plugins.openai.LLM` works unmodified); `stream_options`/`max_completion_tokens`/`service_tier` are auto-stripped server-side (LiveKit may send them — tolerated); **setting `reasoning_effort` to ANY value enables think mode** → we simply never send it (non-think default), mirroring the existing Qwen `reasoning_effort:"none"` concern at `pipeline.py:166-169`.

**Touch-points**

- `voice-agent/app/pipeline.py::build_providers` — insert before the Groq branch:

```python
if overrides.llm_provider == "sarvam" and settings.sarvam_api_key:
    bundle.llm = openai.LLM(
        model=overrides.llm_model or settings.sarvam_model,   # "sarvam-105b"
        api_key=settings.sarvam_api_key,
        base_url=settings.sarvam_llm_base_url,                # "https://api.sarvam.ai/v1"
        # NOTE: no reasoning_effort kwarg — any value enables think mode (latency)
    )
elif settings.groq_api_key:  # existing Groq branch untouched (escalation/default)
    ...
```

  Exact version-segment caveat: reference pages show both `/v1`-style and `POST …/v2/chat/completions` paths — pin `SARVAM_LLM_BASE_URL` via env and confirm with one curl during implementation; if `/v2` is authoritative, `base_url="https://api.sarvam.ai/v2"` is the only change.
- `voice-agent/app/config.py` — add `sarvam_model: str = "sarvam-105b"`, `sarvam_llm_base_url: str = "https://api.sarvam.ai/v1"`.
- `frontend/src/components/VoiceSettingsForm.jsx` — extend `LLM_MODEL_CHOICES`: `{value:"sarvam-105b", label:"Sarvam 105B — best Telugu/Tenglish"}`; label the pair `(llm_provider,llm_model)` in the saved object (empty provider = legacy model-string behavior preserved for existing versions).
- Rule-based escalation wiring (locked architecture): hard-turn triggers in `escalation_rules` already flow through prompts; the escalation *tier* stays Groq GPT-OSS-120B — implemented as prompt/session guidance, not a second LLM connection (unchanged from today; revisit only if qa-eval shows Sarvam failing specific turns that Groq passes).
- `.env.example` — `SARVAM_MODEL=sarvam-105b`, `SARVAM_LLM_BASE_URL=https://api.sarvam.ai/v1`.
- Tests: provider-selection unit tests (sarvam branch chosen iff provider+key; falls back to Groq with a `problems` entry otherwise).

**Verification gate C:** synthetic tool-loop test — AgentSession with `record_extracted_field`/`end_call` tools driven against Sarvam in a scripted conversation; assert tool_calls fire with parseable `function.arguments` JSON (docs warn arguments are a JSON *string*). Only then live-call gate via Phase D.

---

### Phase D — qa-eval acceptance harness (gates every default-flip)

**Goal:** no provider swap becomes default without numbers. Nothing here ships to prod paths; it's the referee.

**New tree** `qa-eval/` (repo root, sibling of `backend/`):

```
qa-eval/
  datasets/
    telugu_8khz_gold.jsonl     # 60-min annotated set: mixed Telugu/Tenglish,
                               # mobile+landline captures (multilingual.md §7 gap #1)
    absent_student_flow.json   # Telugu translation of the domain-config question flow
  harness.py                   # offline leg: replay dataset audio -> candidate STT;
                               # score WER (jiwer) + extraction accuracy vs gold fields
  live_suite.py               # live leg: N calls via POST /api/test-call per arm
                               # (allowlisted numbers only), pull turns/latency/
                               # extracted_fields from existing APIs, emit report.json
  report.py                    # renders the gate table; exit code 1 on any gate fail
  gates.yaml                   # the numeric contract below, versioned
```

**Gate contract (`gates.yaml`, initial values)**

| Gate | Threshold | Source |
|---|---|---|
| STT WER (Telugu, 8 kHz gold set) | Sarvam ≤ 25 % absolute AND ≤ Deepgram-`te` + 0 pts relative | decides STT swap |
| Extraction accuracy | ≥ 85 % required-field accuracy per arm (FR-12; no fabricated values — low-confidence flags counted as failures only if unfilled) | PRD constraint |
| Median e2e latency | ≤ 900 ms (`e2e_ms` from existing `TurnTelemetry` posts) | locked NFR-1 |
| p95 e2e latency | ≤ 1500 ms | headroom guard |
| Connect rate (live leg) | within ±5 pts of incumbent arm | Phase A parity carry-over |
| TTS naturalness | blind MOS ≥ 4.0 on OUR scripts, 5 voices × college-office staff | multilingual.md §7 gap #3 |
| Tool-call reliability | ≥ 95 % of turns requiring `record_extracted_field` produce a well-formed call | Phase C hard gate |

**Promotion rule:** an arm (e.g., `plivo+saaras+sarvam-105b+bulbul`) becomes platform default only after (1) two consecutive passing weekly runs, (2) owner sign-off on the report. Default-flips are env/version operations (`TELEPHONY_PROVIDER`, new AgentVersion rows), so rollback is always one flip away.

**Touch-points:** consumes only existing surfaces (`/api/test-call` with `provider` override from Phase A, `/internal/*`, transcript/latency tables). One backend addition allowed: expose extracted-fields-per-call via the existing calls API if not already exported (check `routers/export.py` first — likely reusable as-is).

---

## 3. Risk register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Plivo stream quirks**: no `connected` frame breaks naive handshake; default codec is L16 not mulaw; `extraHeaders` charset excludes `_`; WS retried only twice then disconnects; bidirectional forbids `audioTrack=outbound/both` | High → Low | Handshake written against Plivo grammar (Phase A); `contentType` pinned to mulaw; call_id via query param; `keepCallAlive=true` keeps call alive across reconnect attempts; integration test replays recorded Plivo frame sequences |
| R2 | **Sarvam latency at 8 kHz**: cascade budget 650–900 ms has zero slack vs ≤900 ms target; Saaras "Fast mode" <150 ms is a [VENDOR] claim | High | Per-turn `e2e_ms` telemetry already exists — alarm on p95 breach; Cartesia (<90 ms TTFB) stays wired as per-agent TTS escape hatch; `endpointing_ms`/VAD knobs already tuned; if budget blows, keep Sarvam STT + Cartesia TTS hybrid (still beats competitor on Indic accuracy) |
| R3 | **Tenglish extraction accuracy**: code-mixed utterances may yield wrong/garbled structured fields | High | FR-12 enforced in tools (`LOW_CONFIDENCE_THRESHOLD`, `MAX_ASKS_PER_FIELD`, never guess); `heuristic_extract` (`pipeline.py:301`) needs Telugu-script review in Phase D; gate: 85 % extraction floor blocks promotion |
| R4 | **DPDP data residency**: Deepgram/Cartesia US-hosted today; Twilio Media Streams hops US1 (no India region). Sarvam is India-hosted — swap *improves* posture; but recordings still land wherever Plivo stores them | Medium | Plivo India media anchoring (KYC + INR account mandatory before IN numbers); verify Plivo recording storage region at account setup; retention job (`RECORDING_RETENTION_DAYS`) unchanged; compliance-agent sign-off before campaign-scale Plivo cutover (DLT registration ₹5,900, 160-series numbers, auto-dialer pre-declaration — telephony-alternatives.md §5 Phase 0 starts day one, in parallel) |
| R5 | **Sarvam single-vendor concentration + pricing-page inconsistency** (₹30/hr vs ₹1.5/min marketing) | Medium | Get written list pricing pre-contract (multilingual.md gap #4); Deepgram/Cartesia remain one env flip away; negotiate Bulbul v2 rates as condition of volume |
| R6 | **Groq model churn** (Llama deprecations Aug 2026 forced migration anyway) — escalation tier drift | Low | Escalation model pinned via `GROQ_MODEL` env; quarterly model audit folded into qa-eval cadence |
| R7 | **Plivo PAYG concurrency cliff** (2 RPS / 50 concurrent; Enterprise $1k/mo) during campaign bursts | Medium | Load-test at 1.5× planned CPS before any campaign cutover; monitor concurrent-leg metric; trigger documented: sustained >300k min/mo or cap hits → renegotiate Enterprise or start carrier-SIP eval (telephony-alternatives.md Phase 3) |
| R8 | **Compliance barring risk**: one UCC violation bars ALL telecom resources 15 days (Feb 2025 TCCCPR amendment) | High | 160-series transactional numbers (not DND-scrubbed, fits absent-student notification), disclosure script first in every prompt (already rendered first — `render_system_prompt`), calling-hours enforcement unchanged, consent_enforcement stays on |

---

## 4. Verification gates (consolidated, incl. live-call acceptance)

Per-phase gates are stated inline above. **Live-call acceptance criteria (any phase claiming success on real calls):**

1. Calls placed only to `TEST_PHONE_NUMBERS` allowlist while `CONSENT_ENFORCEMENT=true` (guardrail honored; DLT/KYC sign-off required before widening).
2. Full loop observable: `phone-{call_id}` room joined by bridge, agent speaks within 2.5 s of pickup, transcript rows + captions render, `turn_latency` JSON lines posted per exchange with all four timing columns non-null.
3. End-state correctness: hangup maps to the right internal status via the provider status map; `end_call` posts completion; extracted fields visible; recording persisted; retry/backoff bookkeeping fires on no-answer.
4. Interruption: caller talks over agent → VAD triggers, agent stops, playback buffer cleared (`clearAudio` on Plivo), agent resumes coherently.
5. Degradation path: kill a provider key mid-suite → session degrades with apology + `post_complete(status="error")` rather than dead air (`_degrade` path exercised).
6. Numbers, not vibes: Phase D report attached to every default-flip decision.

---

## 5. ₹/min before → after (ex-GST, FX ₹87/$, connected-minute basis, 3-min avg call)

| Phase | Telephony | STT | LLM | TTS | **All-in ₹/min** |
|---|---|---|---|---|---|
| **Baseline (today)** Twilio + Deepgram-en + Groq + Cartesia | 1.55–1.60 (voice 1.20–1.50 + Media Streams 0.37 + recording/AMD extras) | 0.37–0.65 | 0.02–0.30 | 1.8–3.0 | **≈ 3.8–5.5** |
| **After Phase A** Plivo legs (streaming/recording/AMD included) | **0.38** | unchanged | unchanged | unchanged | **≈ 2.6–4.1** |
| **After Phase B** Telugu arm: Saaras v3 in, Bulbul v3 in | 0.38 | 0.50 | unchanged | 0.55–1.80 | **≈ 1.5–3.0** |
| **After Phase C** `sarvam-105b` in | 0.38 | 0.50 | 0.05–0.30 | 0.55–1.80 | **≈ 1.5–3.0** (cost-neutral; quality-driven) |
| **Cumulative expected** (mid TTS chars + v2-rate negotiation −0.5–0.9) | 0.38 | 0.50 | ~0.15 | ~0.55–1.10 | **≈ ₹1.5–2.1 ✅ ≤ ₹2.0 target** |

Notes: English agents can stay on Deepgram-en (₹0.44) + Cartesia where they're already cheapest — per-language routing means the ₹2 figure binds on the *Telugu* arm. Sticker-worst-case (max chars, v3 TTS rates, no negotiation) is ≈ ₹3.0, still under the ₹3.5 competitor line; the three ordered mitigations (v2-rate TTS deal, shorter domain-config phrasings, self-host TTS at >1M chars/mo) hold the ₹2 line. One-time: DLT ₹5,900 + Plivo KYC effort. At ~100k calls/mo, Phase A alone avoids ≈ ₹3.5 lakh/month (telephony-alternatives.md §0).

---

## 6. Dispatch order & ownership

1. **Phase A** → `telephony-agent` (+`backend-agent` for registry/config edits), compliance-agent starts DLT/KYC track in parallel (day one).
2. **Phase B** → `voice-pipeline-agent` (+`frontend-agent` for VoiceSettingsForm), gated on Phase A sandbox green (need Plivo legs to test telephony-grade audio).
3. **Phase C** → `conversation-ai-agent` (small diff; can overlap Phase B tail once `sarvam_api_key` lands).
4. **Phase D** → `qa-eval-agent`, dataset collection starts immediately (it's calendar-bound, not code-bound); all promotions route through it.

Each phase ends with its verification gate as the merge criterion; every default-flip afterward is a one-line env change or one immutable AgentVersion save.
