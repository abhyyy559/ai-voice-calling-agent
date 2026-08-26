# Task 3 Brief: `/twilio/media` WebSocket bridge route

**Files:**
- Modify: `backend/app/routers/twilio.py` (append pumps + route; add imports)
- Modify: `backend/app/config.py` (add ONE settings field)
- Modify: `infra/docker-compose.yml` (add ONE literal env line in backend environment block)

**Interfaces:**
- Consumes: `parse_stream_event`, `build_phone_room_token`, `PHONE_ROOM_PREFIX` from `app/services/twilio_bridge.py`; `ulaw_to_pcm16`, `downsample_pcm16`, `pcm16_to_ulaw` from `app/services/g711.py`; existing `Call`/`Contact` models; `websocket.app.state.settings/.session_factory`.
- Produces: live WS endpoint Twilio connects to. NO automated test — kept thin; verified by import-sanity + full suite + later manual E2E.

## Step 0 (MANDATORY before writing code): introspect installed livekit

Run these in PowerShell and RECORD outputs in your report:

```
cd C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend
.venv\Scripts\python.exe -c "from livekit import rtc; import inspect; print(rtc.AudioFrame.__init__.__doc__); print([m for m in dir(rtc.AudioFrame) if 's16' in m or 'from' in m])"
.venv\Scripts\python.exe -c "from livekit import rtc; print([m for m in dir(rtc.LocalParticipant) if 'publish' in m])"
.venv\Scripts\python.exe -c "from livekit import rtc; import inspect; print(inspect.signature(rtc.Room.connect))"
```

Adapt the three flagged calls to the REAL signatures you find. Do not invent methods.

## Config additions (exact)

`backend/app/config.py` — add near the other livekit fields:

```python
    # Container-facing LiveKit URL for server-side bridges (media gateway).
    # Browser tokens keep using livekit_url.
    livekit_url_internal: str = "ws://livekit:7880"
```

`infra/docker-compose.yml` — inside the backend service `environment:` block, append one literal line (NO ${} interpolation):

```yaml
      LIVEKIT_URL_INTERNAL: ws://livekit:7880
```

## Route implementation (adapt per introspection)

Append to `backend/app/routers/twilio.py`. Add to top imports if missing: `import json`, `WebSocket, WebSocketDisconnect` from fastapi, and:

```python
from app.services.twilio_bridge import parse_stream_event as _parse_bridge_event
from app.services.twilio_bridge import build_phone_room_token
```

Pumps (module level, after `_build_voice_twiml`):

```python
# --- media streams bridge (Twilio <-> LiveKit phone rooms) -------------------


async def _pump_twilio_to_room(ws, source, stream_sid_box: dict[str, str]) -> None:
    """Decode caller mu-law frames and publish them into the LiveKit room."""
    import base64

    from livekit import rtc

    from app.services.g711 import ulaw_to_pcm16

    while True:
        raw = await ws.receive_text()
        try:
            ev = _parse_bridge_event(raw)
        except ValueError:
            continue
        if ev.event == "stop":
            break
        if ev.event == "start":
            stream_sid_box["sid"] = ev.stream_sid
            continue
        if ev.event != "media" or not ev.media_payload:
            continue
        pcm8k = ulaw_to_pcm16(base64.b64decode(ev.media_payload))
        frame = _make_frame(pcm8k)
        await source.capture_frame(frame)


async def _pump_room_to_twilio(room, ws, stream_sid_box: dict[str, str]) -> None:
    """Subscribe agent audio (48k mono) and forward as mu-law media messages."""
    import asyncio
    import base64

    from app.services.g711 import downsample_pcm16, pcm16_to_ulaw

    queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)

    def _on_frame(frame, _participant=None, _track=None) -> None:  # noqa: ANN001
        pcm48k = bytes(frame.data)
        ulaw = pcm16_to_ulaw(downsample_pcm16(pcm48k, 6))
        try:
            queue.put_nowait(ulaw)
        except asyncio.QueueFull:
            pass  # drop backlog: live caller audio wins over stale frames

    room.on("track_subscribed")(_on_frame)
    while True:
        ulaw = await queue.get()
        payload = base64.b64encode(ulaw).decode()
        await ws.send_text(
            json.dumps(
                {
                    "event": "media",
                    "streamSid": stream_sid_box.get("sid", ""),
                    "media": {"payload": payload},
                }
            )
        )


def _make_frame(pcm8k: bytes):
    """Build an rtc.AudioFrame from 16-bit LE PCM using the installed SDK."""
    from livekit import rtc

    if hasattr(rtc.AudioFrame, "from_s16"):
        return rtc.AudioFrame.from_s16(pcm8k, sample_rate=8000, num_channels=1)
    return rtc.AudioFrame(
        data=pcm8k,
        samples_per_channel=len(pcm8k) // 2,
        sample_rate=8000,
        num_channels=1,
    )
```

Route:

```python
@router.websocket("/media")
async def twilio_media(websocket: WebSocket) -> None:
    """Twilio Media Streams -> LiveKit phone-room bridge (one WS per call leg)."""
    import asyncio

    from livekit import rtc

    await websocket.accept()
    settings = websocket.app.state.settings

    async def _close(code: int) -> None:
        try:
            await websocket.close(code=code)
        except Exception:  # noqa: BLE001
            pass

    try:
        first = await websocket.receive_text()
        ev = _parse_bridge_event(first)
    except (WebSocketDisconnect, ValueError):
        await _close(4400)
        return
    if ev.event != "start" or not ev.call_id:
        await _close(4400)
        return

    with next(websocket.app.state.session_factory()) as db:
        call = db.get(Call, int(ev.call_id))
        if call is None or call.agent_version_id is None:
            await _close(4404)
            return
        contact = db.get(Contact, call.contact_id) if call.contact_id else None
        version_id = int(call.agent_version_id)
        contact_card: dict = {}
        if contact is not None:
            contact_card.update(contact.custom_fields or {})
            contact_card.setdefault("name", contact.name or "")

    token, room_name = build_phone_room_token(
        settings,
        call_id=int(ev.call_id),
        version_id=version_id,
        contact={k: str(v) for k, v in contact_card.items() if v},
    )
    room = rtc.Room()
    stream_sid_box: dict[str, str] = {"sid": ev.stream_sid}
    logger.info("media bridge joining %s (call %s)", room_name, ev.call_id)
    await room.connect(settings.livekit_url_internal, token)

    source = rtc.AudioSource(sample_rate=8000, num_channels=1)
    track = await room.local_participant.publish_audio_source(source)

    to_agent = asyncio.ensure_future(_pump_twilio_to_room(websocket, source, stream_sid_box))
    from_agent = asyncio.ensure_future(_pump_room_to_twilio(room, websocket, stream_sid_box))
    room_name_final = room_name
    try:
        _, pending = await asyncio.wait(
            {to_agent, from_agent}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
    finally:
        try:
            await room.disconnect()
        except Exception:  # noqa: BLE001
            logger.warning("room disconnect failed for %s", room_name_final, exc_info=True)
```

Binding adjustments allowed ONLY where introspection demands: frame construction (`_make_frame` handles it), publish method name/awaitability (`publish_audio_source` vs `publish_tracks(...)`), `room.connect(url, token)` extra kwargs. If publish needs explicit source-options, keep defaults.

Never crash the server: everything after accept() already guarded; ensure no bare raise escapes the route.

## Verification steps

1. `.venv\Scripts\python.exe -c "import app.routers.twilio"` → exit 0
2. Full suite (workdir backend): `.venv\Scripts\python.exe -m pytest -q` → all green (92 baseline)
3. `docker compose -f ..\infra\docker-compose.yml config --quiet` from repo root must parse (or ask orchestrator to run it)

Report contract: full report to `.superpowers/sdd/t3-report.md` including introspection outputs + adapted signatures. Return ONLY status / files / one-line results / concerns.

## Global Constraints

PowerShell 5.1 · NO git commands · touch ONLY the three listed files · never log/print full JWTs.
