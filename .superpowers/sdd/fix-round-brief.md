# Fix Round Brief — Twilio bridge final-review findings

Apply ALL findings below to the VocalIQ repo. Files you may touch:
`backend/app/routers/twilio.py`, `backend/app/services/twilio_bridge.py`,
`backend/tests/test_twilio_bridge.py`, `voice-agent/tests/test_rooms.py`.
NO git commands. NO other files.

## C1 — TwiML stream URL missing /twilio prefix
In `routers/twilio.py::_build_voice_twiml`, change:
`Stream(url=f"{ws_base_url}/media", ...)` →
`Stream(url=f"{ws_base_url}/twilio/media", ...)`

## C2 — handshake must tolerate Twilio's mandatory first `connected` frame
Replace the single `receive_text()` + strict-start logic at the top of
`twilio_media` with a bounded loop: read messages until a `start` event arrives;
silently skip `connected` events and unparseable junk; enforce an overall
handshake timeout of 10 seconds using `asyncio.wait_for` on each receive with
a deadline; on timeout → `_close(4400)` + log WARNING.

## C3 — call_id lives in `start.customParameters`; also capture callSid
Twilio's real start frame shape:
```json
{"event":"start","streamSid":"MZ...","start":{"streamSid":"MZ...",
 "callSid":"CA...","customParameters":{"call_id":"42"}}}
```
Update `MediaEvent` to add field `call_sid: str = ""`.
Update `parse_stream_event` so for event=="start" it reads:
- `call_id` from `msg["start"]["customParameters"]["call_id"]`
  (fallback to legacy `parameters` key ONLY if customParameters absent — keeps old test meaningful)
- `call_sid` from `msg["start"]["callSid"]`
Update `test_parse_start_carries_call_id_parameter` fixture to the documented
shape above (customParameters + callSid) and assert both fields parsed.
Add one more test: legacy `parameters` fallback still parses call_id.

## S1 — bind the WS to Twilio via unguessable CallSid
In the route, after loading `call`: require
`ev.call_sid and ev.call_sid == call.provider_call_id` else `_close(4403)` +
log WARNING with call id only. Update route to pass through accordingly.
Add test: valid start with WRONG callSid → websocket closed with code 4403
(use FastAPI TestClient websocket_connect; assert `websocket.receive()` raises
WebSocketDisconnect or collect close code per framework support).

## I1 — register subscription handler before connect
Move the `room.on("track_subscribed")(_on_frame)` registration OUT of
`_pump_room_to_twilio` into the route, executing BEFORE `await room.connect(...)`.
Additionally after connect completes, scan existing
`room.remote_participants` tracks and feed any already-published audio tracks
into the same queue path (belt-and-braces against missed events).
`_pump_room_to_twilio` signature becomes `(queue, ws, stream_sid_box)`.

## I2 — no starved pump / unretrieved tasks
- When the room→queue drain loop ends (track closed/participant gone/
  disconnected), put a sentinel `b""` into the queue; the send loop treats
  `b""` as end-of-stream and exits cleanly.
- Register `room.on("disconnected")` to set an asyncio.Event that the send
  loop also selects on.
- In the route finally-block: cancel remaining tasks AND `await asyncio.gather(*tasks, return_exceptions=True)` so no "exception was never retrieved".

## I3 — org-scope the explicit agent_version_id
`routers/test_call.py`: when `payload.agent_version_id` given, resolve via
join Agent on id + `Agent.org_id == user.org_id` instead of bare db.get;
unknown OR foreign → same 422 "unknown agent_version_id".
Add test in test_call_flow.py: version from ANOTHER org → 422.

## Nits (do all)
1. Rename `_make_frame(pcm8k)` param to `pcm16_8k` and update docstring:
   "16-bit LE PCM at 8 kHz".
2. `voice-agent/tests/test_rooms.py`: replace the `assert X if False else Y`
   line with two plain asserts (`not is_handled_room("phone")`,
   `is_handled_room("phone-42")` already covered elsewhere — keep semantics,
   remove the dead conditional).
3. Move base64 decode inside try/except in `_pump_twilio_to_room`; on
   binascii.Error log DEBUG and continue.

## Verification (all required)
1. Full backend suite: `.venv\Scripts\python.exe -m pytest -q` → all green (96+new)
2. voice-agent offline: `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q` → green
3. Import sanity: `.venv\Scripts\python.exe -c "import app.routers.twilio"` exit 0

Append everything to `.superpowers/sdd/t3-report.md` under "## Final-review fix round".
Return ONLY: status, files changed, verification lines, concerns.
