# Task 3 Report: `/twilio/media` WebSocket bridge route

**Status: DONE_WITH_CONCERNS** — implemented, all verifications pass; one deployment-level concern (rtc dep not installed where the route runs) flagged for orchestrator.

## Files changed
1. `backend/app/routers/twilio.py` — imports (json, WebSocket/WebSocketDisconnect, bridge service fns) + `_make_frame`, both pumps, `@router.websocket("/media")` appended after `_build_voice_twiml`.
2. `backend/app/config.py` — added `livekit_url_internal: str = "ws://livekit:7880"` after the other livekit fields.
3. `infra/docker-compose.yml` — literal `LIVEKIT_URL_INTERNAL: ws://livekit:7880` line in backend `environment:` block (no `${}` interpolation).

## Step 0 introspection (MANDATORY) — actual outputs

Backend venv has **no `livekit` rtc package** (only `livekit-api` 1.2.0):
```
> backend\.venv\Scripts\python.exe -c "from livekit import rtc; ..."
ImportError: cannot import name 'rtc' from 'livekit' (unknown location)
```
The actually-installed rtc SDK lives in `voice-agent\.venv`: **livekit-rtc 1.1.14** (with livekit-agents 1.7.0, livekit-api 1.2.0). Introspection ran there:

```
AudioFrame.__init__.__doc__:
    Initialize an AudioFrame instance.
    Args:
        data (Union[bytes, bytearray, memoryview]): raw audio data, at least
            num_channels * samples_per_channel * sizeof(int16) bytes long.
        sample_rate (int) / num_channels (int) / samples_per_channel (int)

dir(rtc.AudioFrame) filtered:
    ['_from_owned_info', 'create', 'data', 'duration', 'num_channels',
     'sample_rate', 'samples_per_channel', 'to_wav_bytes', 'userdata']
    -> NO `from_s16` classmethod

LocalParticipant publish members:
    ['publish_data', 'publish_data_track', 'publish_dtmf', 'publish_track',
     'publish_transcription', 'unpublish_track']
    -> NO `publish_audio_source`

inspect.signature(rtc.Room.connect):
    (self, url: str, token: str, options: RoomOptions = RoomOptions(
        auto_subscribe=True, dynacast=False, e2ee=None, encryption=None,
        rtc_config=None, connect_timeout=None, single_peer_connection=None)) -> None

inspect.signature(LocalParticipant.publish_track):   # async
    (self, track: LocalTrack, options: TrackPublishOptions = ...) -> LocalTrackPublication
inspect.signature(LocalAudioTrack.create_audio_track):  # sync staticmethod
    (name: str, source: Union[AudioSource, PlatformAudioSource]) -> LocalAudioTrack

inspect.signature(AudioSource.__init__):
    (self, sample_rate: int, num_channels: int, queue_size_ms: int = 1000,
     loop: asyncio.AbstractEventLoop | None = None)
AudioSource.capture_frame: async (self, frame: AudioFrame) -> None

Room.on docstring (excerpt):
    "track_subscribed": Arguments: track (Track),
        publication (RemoteTrackPublication), participant (RemoteParticipant)
    -> callback receives a TRACK, not frames

AudioStream.__init__:
    (self, track: Track, loop=None, capacity=0, sample_rate=48000,
     num_channels=1, frame_size_ms=None, noise_cancellation=None,
     auto_close_noise_cancellation=True, **kwargs)
AudioStream members: __aiter__, __anext__, aclose()  (NO .recv)
AudioFrameEvent(frame=...) -> `.frame` attribute verified by construction
AudioFrame(data=b'...', samples_per_channel=2, sample_rate=8000, num_channels=1) constructed OK
```

## Adaptations vs brief (all introspection-driven)

| Brief | Reality (livekit-rtc 1.1.14) | Adaptation |
|---|---|---|
| `room.local_participant.publish_audio_source(source)` | method does not exist | `track = rtc.LocalAudioTrack.create_audio_track(f"twilio-{call_pk}", source)` then `await room.local_participant.publish_track(track)` (defaults kept per brief) |
| `_on_frame(frame, ...)` via `room.on("track_subscribed")` receiving frames | handler gets `(track, publication, participant)` — a Track, not frames | pump spawns an `_drain(track)` task per subscribed track; iterates `rtc.AudioStream(track)` (`async for event` → `event.frame`); drains cancelled in pump `finally`; `await audio_stream.aclose()` |
| hard-coded `downsample_pcm16(pcm48k, 6)` | AudioStream may deliver resampled frames (default requests 48k) or native-rate frames depending on publisher | factor computed from the real frame: `max(1, round(frame.sample_rate / 8000))`; decimate only if >1 |
| `with next(websocket.app.state.session_factory()) as db:` | `session_factory` is a plain `sessionmaker[Session]` (verified in app/database.py, app/main.py, tests/conftest.py) — `next(Session)` raises TypeError | `with websocket.app.state.session_factory() as db:` |
| `rtc.AudioFrame.from_s16(...)` fallback branch | no `from_s16`; constructor `(data, samples_per_channel, sample_rate, num_channels)` verified working | kept `_make_frame` hasattr-guard unchanged; constructor branch is the live path |
| `room.connect(url, token)` | signature matches positionally; options default auto_subscribe=True (wanted: receive agent audio) | unchanged |

Extra safety beyond brief (per "never crash the server"): `int(ev.call_id)` wrapped — non-numeric `call_id` parameter closes WS with 4400 instead of raising.

## Verification

```
1. backend\.venv\Scripts\python.exe -c "import app.routers.twilio"
   -> import OK, exit 0        (lazy rtc imports keep module importable without rtc pkg)

2. backend: .venv\Scripts\python.exe -m pytest -q
   -> 92 passed, 125 warnings in 46.93s   (baseline 92 held; warnings pre-existing)

3. docker compose -f "..\infra\docker-compose.yml" config --quiet   (workdir backend/)
   -> exit 0
```

Python 3.12/3.13 compat: no `audioop` import in touched code; no syntax newer than 3.10; `asyncio.wait` receives Tasks (not coroutines) so no 3.12+ restriction hit.

## Concerns (for orchestrator)

1. **E2E blocker — `livekit` (rtc) not installed in the backend runtime envs.**
   `backend/requirements.txt` declares only `livekit-api>=0.7`; backend Dockerfile installs from it. All rtc imports in the new route are function-level (so import-sanity passes), but at RUNTIME the first `/twilio/media` connection will hit `ImportError: cannot import name 'rtc'` in the container (and locally in backend/.venv). Fix outside my 3-file scope: add `livekit>=1.1,<2` to `backend/requirements.txt` (rebuild image). Version pinned suggestion based on introspected 1.1.14 in voice-agent venv.
2. Local backend venv therefore cannot smoke-test rtc code paths; verification relied on introspection against the installed 1.1.14 in `voice-agent/.venv`. Manual E2E (Task later) must run where rtc is importable.
3. `backend/twilio.py` exists as a stray root-level file (pre-existing; untouched).
4. Agent→caller downsample assumes agent tracks are near-multiples of 8 kHz (48k/24k/16k/8k all exact; 44.1k would round to 6 and shift pitch slightly) — acceptable per g711.py "aliasing acceptable for v1 speech" note.
5. Pre-existing test warnings (Starlette/httpx deprecation, short HMAC keys, SAWarning in calls.py:140) — unrelated, untouched.

## Final-review fix round

Files changed (only): `backend/app/routers/twilio.py`, `backend/app/services/twilio_bridge.py`, `backend/tests/test_twilio_bridge.py`, `voice-agent/tests/test_rooms.py`, `backend/app/routers/test_call.py`, plus the I3 test in `backend/tests/test_call_flow.py` (brief �I3 explicitly directs "Add test in test_call_flow.py").

### Per-finding status

| Finding | Status | What was done |
|---|---|---|
| C1 stream URL | DONE | `_build_voice_twiml` now emits `{ws_base_url}/twilio/media` |
| C2 handshake | DONE | Route top replaced with bounded loop: skips unparseable junk and mandatory first `{"event":"connected"}`, reads until `start`; per-receive `asyncio.wait_for` against an overall 10 s deadline (`HANDSHAKE_TIMEOUT_SECONDS`); deadline exceeded -> WARNING + `_close(4400)`. Client disconnect pre-start just returns. Malformed start / non-numeric call_id still fail fast with 4400. New test `test_handshake_skips_connected_and_junk_then_closes_on_non_start` covers junk+connected skipping (4400 on non-start). |
| C3 start frame shape | DONE | `MediaEvent` gains `call_sid: str = ""`. For `start`: `call_id` read from `start.customParameters.call_id`, falling back to legacy `start.parameters.call_id` ONLY when customParameters absent; `call_sid` from `start.callSid`. Fixture updated to documented real shape (customParameters + callSid), asserts both fields; new `test_parse_start_legacy_parameters_fallback` covers legacy key. |
| S1 callSid binding | DONE | After loading the Call row: require `ev.call_sid and ev.call_sid == call.provider_call_id`, else WARNING (call id only) + `_close(4403)` before any LiveKit work. New test `test_wrong_callsid_rejected_4403` (TestClient websocket_connect; `WebSocketDisconnect.code == 4403`). |
| I1 subscribe-before-connect | DONE | Queue/drain machinery moved out of the pump. Route registers `room.on("track_subscribed", _on_frame)` BEFORE `room.connect(...)`. After connect completes, existing `room.remote_participants` audio tracks are scanned and fed through the same `_on_frame` path (deduped by track sid so belt-and-braces scan cannot double-drain one track). `_pump_room_to_twilio` signature is now `(queue, ws, stream_sid_box)`. |
| I2 starved pump / unretrieved tasks | DONE | Each drain (`_drain_track`) puts sentinel `b""` into the queue in its `finally` (via `_put_sentinel`, which drops backlog if the queue is full); send loop exits cleanly on `b""`. `room.on("disconnected")` sets a `room_gone` asyncio.Event AND enqueues the sentinel; route supervisor selects on the event via `room_gone_waiter` task for prompt teardown. Route finally-block cancels all tasks (pumps + waiter + drains) then `await asyncio.gather(..., return_exceptions=True)` -> no "exception was never retrieved". |
| I3 org-scope agent_version_id | DONE | `test_call.py` explicit-version branch resolves via `select(AgentVersion).join(Agent ...).where(AgentVersion.id == ..., Agent.org_id == user.org_id)`; unknown OR foreign -> same 422 "unknown agent_version_id". New `test_foreign_org_agent_version_422` in `test_call_flow.py` (version owned by a second Organization -> 422). |
| Nit 1 param name | DONE | `_make_frame(pcm8k)` -> `_make_frame(pcm16_8k)`; docstring now "16-bit LE PCM at 8 kHz". |
| Nit 2 dead conditional | DONE | `test_rooms.py::test_other_rooms_rejected` dead `if False else` removed; plain asserts `not is_handled_room(None)` and `not is_handled_room("phone")` (semantics kept; "phone-42" positive already covered by `test_phone_rooms_handled`). |
| Nit 3 base64 decode | DONE | Decode wrapped in try/except `binascii.Error` inside `_pump_twilio_to_room`; logs DEBUG and continues. |

### Verification

```
1. backend full suite (workdir backend/): .venv\Scripts\python.exe -m pytest -q
   -> 100 passed, 133 warnings in 155.16s   (96 baseline + 4 new tests)

2. voice-agent offline (workdir repo root):
   backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q
   -> 4 passed in 0.09s

3. Import sanity (workdir backend/):
   .venv\Scripts\python.exe -c "import app.routers.twilio"
   -> exit 0
```

### Concerns

1. **I2 literal-vs-intent deviation:** brief fixed `_pump_room_to_twilio(queue, ws, stream_sid_box)` (no room/event param) while also asking the send loop to select on a disconnected Event. Implemented equivalently: disconnect handler enqueues the `b""` sentinel so the send loop exits promptly, AND sets `room_gone` Event which the route supervisor selects on for immediate teardown of everything. No starvation path remains.
2. Brief header listed 4 touchable files but its body required edits in `test_call.py` (I3) and a new test in `test_call_flow.py`; followed the body (both were also named in the dispatch). Total files touched: six (+report).
3. Happy-path WS E2E (handshake -> room.connect -> audio both ways) still needs a live LiveKit; unit coverage here stops at the callSid gate (before any rtc network I/O). rtc IS importable in backend/.venv now (earlier round's missing-livekit concern appears resolved).
