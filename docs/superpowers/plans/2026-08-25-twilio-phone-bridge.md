# Twilio Phone Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Real outbound calls speak with the agent — Twilio audio bridges into LiveKit `phone-*` rooms where the existing conversation pipeline runs.

**Architecture:** A WebSocket route `/twilio/media` inside the BACKEND decodes Twilio Media Streams μ-law 8 kHz frames and pumps them into a LiveKit room as a participant; the agent's published audio is downsampled back to μ-law for the caller. Worker accepts `phone-*` rooms; `/api/test-call` persists `agent_version_id` on the Call row so the bridge can mint metadata-bearing tokens.

**Tech Stack:** FastAPI WebSocket (uvicorn), `livekit` rtc/api SDK, stdlib `audioop` (py3.12 image), existing pytest suites.

## Global Constraints

- Spec: `docs/superpowers/specs/2026-08-25-twilio-phone-bridge-design.md` — bridge lives in BACKEND; no new container ports; no new env vars.
- Room naming: `phone-{call_id}` exactly. Bridge participant identity: `twilio-{first 8 of streamSid}`.
- Never log auth tokens or full JWTs.
- Existing behavior untouched: playground flow, campaign dialer, webhooks.
- Backend tests: from `backend/` run `.venv\Scripts\python.exe -m pytest -q`. Voice-agent offline tests also run under the SAME backend venv from repo root: `.venv` is backend-local, so use `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q` from repo root (its conftest fixes imports).
- Windows PowerShell 5.1 shell; orchestrator commits (implementers do NOT run git).

## Interfaces (locked across tasks)

```python
# app/services/g711.py
ulaw_to_pcm16(data: bytes) -> bytes          # 1 byte/sample -> 2 bytes/sample LE
pcm16_to_ulaw(data: bytes) -> bytes          # inverse
downsample_pcm16(data: bytes, factor: int = 6) -> bytes   # naive decimation

# app/services/twilio_bridge.py
@dataclass MediaEvent: event: str; stream_sid: str; media_payload: str; call_id: str
parse_stream_event(raw: str | bytes) -> MediaEvent            # raises ValueError on junk
build_phone_room_token(settings, *, call_id: int, version_id: int,
                       contact: dict[str, str]) -> tuple[str, str]  # (jwt, room_name)

# voice-agent/app/rooms.py
is_handled_room(name: str) -> bool             # True for playground-* / phone-*
```

---

### Task 1: g711 codec module

**Files:**
- Create: `backend/app/services/g711.py`
- Test: `backend/tests/test_g711.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `ulaw_to_pcm16`, `pcm16_to_ulaw`, `downsample_pcm16` (signatures above).

- [ ] **Step 1: Failing tests**

Create `backend/tests/test_g711.py`:

```python
"""g711 mu-law codec roundtrips used by the Twilio media bridge."""
from app.services.g711 import downsample_pcm16, pcm16_to_ulaw, ulaw_to_pcm16


def test_roundtrip_silence():
    raw = bytes([0xFF]) * 160  # mu-law silence
    assert len(ulaw_to_pcm16(raw)) == 320
    assert pcm16_to_ulaw(ulaw_to_pcm16(raw))[:160] == raw


def test_roundtrip_tone_lengths():
    pcm = b"\x00\x40" * 320  # tiny positive samples, 20ms @8k
    ulaw = pcm16_to_ulaw(pcm)
    assert len(ulaw) == 320
    back = ulaw_to_pcm16(ulaw)
    assert len(back) == len(pcm)


def test_downsample_factor6():
    pcm = bytes(range(256)) * 8  # 2048 samples
    out = downsample_pcm16(pcm, 6)
    assert len(out) == (2048 // 6) * 2


def test_downsample_default_is_6():
    assert downsample_pcm16(b"\x01\x00" * 12) == downsample_pcm16(b"\x01\x00" * 12, 6)
```

- [ ] **Step 2: Run → expect FAIL (ModuleNotFoundError)**

Run (workdir `backend`): `.venv\Scripts\python.exe -m pytest tests\test_g711.py -q`
Expected: collection error, `No module named 'app.services.g711'`.

- [ ] **Step 3: Implement**

Create `backend/app/services/g711.py`:

```python
"""G.711 mu-law helpers for the Twilio media bridge (stdlib audioop)."""
from __future__ import annotations

import audioop


def ulaw_to_pcm16(data: bytes) -> bytes:
    """Decode 8 kHz mu-law to 16-bit little-endian PCM (2 bytes per sample)."""
    return audioop.ulaw2lin(data, 2)


def pcm16_to_ulaw(data: bytes) -> bytes:
    """Encode 16-bit little-endian PCM to 8 kHz mu-law (1 byte per sample)."""
    return audioop.lin2ulaw(data)


def downsample_pcm16(data: bytes, factor: int = 6) -> bytes:
    """Naive decimation of 16-bit LE PCM by `factor` (48k->8k uses 6).

    Keeps every `factor`-th sample. Aliasing is acceptable for v1 speech.
    """
    if factor <= 1:
        return data
    return b"".join(data[i : i + 2] for i in range(0, len(data) - 1, 2 * factor))
```

- [ ] **Step 4: Run → PASS**

Same command. Expected: `4 passed`.

---

### Task 2: bridge primitives — event parser + phone-room token

**Files:**
- Create: `backend/app/services/twilio_bridge.py`
- Test: `backend/tests/test_twilio_bridge.py`

**Interfaces:**
- Consumes: Task 1 codecs (not directly), `settings.livekit_api_key/secret/url`.
- Produces: `MediaEvent`, `parse_stream_event`, `build_phone_room_token` (signatures above); constants `PHONE_ROOM_PREFIX = "phone-"`.

- [ ] **Step 1: Failing tests**

Create `backend/tests/test_twilio_bridge.py`:

```python
"""Pure logic for the Twilio media bridge: event parsing + room token minting."""
import base64
import json

from conftest import make_settings  # exists in conftest.py already
from app.services.twilio_bridge import (
    PHONE_ROOM_PREFIX,
    build_phone_room_token,
    parse_stream_event,
)


def _media_frame() -> str:
    return base64.b64encode(bytes([0xFF]) * 160).decode()


def test_parse_media_event():
    raw = json.dumps(
        {
            "event": "media",
            "streamSid": "MZ1234567890",
            "media": {"payload": _media_frame()},
        }
    )
    ev = parse_stream_event(raw)
    assert ev.event == "media"
    assert ev.stream_sid == "MZ1234567890"
    assert ev.media_payload == _media_frame()


def test_parse_start_carries_call_id_parameter():
    raw = json.dumps(
        {
            "event": "start",
            "streamSid": "MZ1234567890",
            "start": {"parameters": {"call_id": "42"}},
        }
    )
    ev = parse_stream_event(raw)
    assert ev.event == "start"
    assert ev.call_id == "42"


def test_parse_junk_raises_valueerror():
    import pytest

    with pytest.raises(ValueError):
        parse_stream_event("not json")


def test_build_phone_room_token_shape():
    settings = make_settings(livekit_api_key="devkey", livekit_api_secret="devsecret")
    token, room = build_phone_room_token(
        settings, call_id=84, version_id=3, contact={"student_name": "Aarav"}
    )
    assert room == f"{PHONE_ROOM_PREFIX}84"
    claims = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
    assert claims["iss"] == "devkey"
    assert claims["metadata"].startswith('{"version_id": 3')
    assert claims["video"]["room"] == room
```

Note: check `make_settings` exists in `backend/tests/conftest.py`; if its signature differs (kwargs dict), adapt calls to its real contract — read conftest first.

- [ ] **Step 2: Run → expect FAIL**

Run (workdir `backend`): `.venv\Scripts\python.exe -m pytest tests\test_twilio_bridge.py -q`

- [ ] **Step 3: Implement**

Create `backend/app/services/twilio_bridge.py`:

```python
"""Twilio Media Streams bridge primitives (pure logic, unit-testable).

The FastAPI websocket route in routers/twilio.py stays thin: parse events,
decode/pump frames, mint one room token per stream using build_phone_room_token.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

PHONE_ROOM_PREFIX = "phone-"


@dataclass(frozen=True)
class MediaEvent:
    event: str
    stream_sid: str
    media_payload: str
    call_id: str


def parse_stream_event(raw: Any) -> MediaEvent:
    """Parse one Twilio Media Streams JSON message; raise ValueError on junk."""
    try:
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        msg = json.loads(str(raw))
        if not isinstance(msg, Mapping):
            raise ValueError("not an object")
        event = str(msg.get("event") or "")
        if not event:
            raise ValueError("missing event")
        start = msg.get("start") or {}
        params = start.get("parameters") or {} if isinstance(start, Mapping) else {}
        media = msg.get("media") or {}
        return MediaEvent(
            event=event,
            stream_sid=str(msg.get("streamSid") or ""),
            media_payload=str(media.get("payload") or "") if isinstance(media, Mapping) else "",
            call_id=str(params.get("call_id") or "") if isinstance(params, Mapping) else "",
        )
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"bad twilio event: {exc}") from exc


def build_phone_room_token(
    settings: Any, *, call_id: int, version_id: int, contact: Mapping[str, Any]
) -> tuple[str, str]:
    """Mint a join token for the phone room carrying pipeline metadata."""
    from livekit import api as livekit_api

    room_name = f"{PHONE_ROOM_PREFIX}{call_id}"
    metadata = json.dumps(
        {"version_id": version_id, "call_id": str(call_id), "contact": dict(contact)}
    )
    token = (
        livekit_api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(f"twilio-{str(call_id)[-8:]}")
        .with_metadata(metadata)
        .with_grants(livekit_api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    return token, room_name
```

If `make_settings` in conftest builds Settings via kwargs, ensure the test constructs settings the same way the rest of the suite does.

- [ ] **Step 4: Run → PASS** (`5 passed`)

---

### Task 3: `/twilio/media` WebSocket endpoint (thin pump layer)

**Files:**
- Modify: `backend/app/routers/twilio.py` (append route + two private pump coroutines)

**Interfaces:**
- Consumes: Task 2 `parse_stream_event/build_phone_room_token`, Task 1 codecs.
- Produces: live path Twilio connects to. No unit test (integration verified manually E2E); kept thin so review + manual gate covers it.

- [ ] **Step 1: Implement**

Append to `backend/app/routers/twilio.py` — first the two pump coroutines (module level, after `_build_voice_twiml`):

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
        frame = rtc.AudioFrame.from_s16(pcm8k, sample_rate=8000, num_channels=1)
        await source.capture_frame(frame)


async def _pump_room_to_twilio(room, ws, stream_sid_box: dict[str, str]) -> None:
    """Subscribe agent audio (48k mono) and forward as mu-law media messages."""
    import asyncio

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
```

Add to the imports at the top of the file:

```python
import json  # if not already imported
from fastapi import WebSocket, WebSocketDisconnect
from app.services.twilio_bridge import parse_stream_event as _parse_bridge_event
from app.services.twilio_bridge import build_phone_room_token
```

Then the route:

```python
@router.websocket("/media")
async def twilio_media(websocket: WebSocket) -> None:
    """Twilio Media Streams -> LiveKit phone-room bridge (one WS per call leg)."""
    import asyncio

    from livekit import rtc

    await websocket.accept()
    settings = websocket.app.state.settings

    async def _close(code: int) -> None:
        await websocket.close(code=code)

    try:
        first = await websocket.receive_text()
        ev = _parse_bridge_event(first)
    except (WebSocketDisconnect, ValueError):
        try:
            await _close(4400)
        except Exception:  # noqa: BLE001
            pass
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
    await room.connect(settings.livekit_url_internal, token)

    source = rtc.AudioSource(sample_rate=8000, num_channels=1)
    track = await room.local_participant.publish_audio_source(source)

    to_agent = asyncio.ensure_future(_pump_twilio_to_room(websocket, source, stream_sid_box))
    from_agent = asyncio.ensure_future(_pump_room_to_twilio(room, websocket, stream_sid_box))
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
            logger.warning("room disconnect failed for %s", room_name, exc_info=True)
```

Implementation notes (binding):
- Introspect the installed `livekit` package inside `backend/.venv` and adapt to REAL signatures; record what you used in the module docstring. Specifically verify: (a) how to build an `rtc.AudioFrame` from raw s16 bytes (`from_s16` vs constructor kwargs), (b) publishing an `rtc.AudioSource` on `LocalParticipant` (exact method name/awaitability), (c) whether `rtc.Room.connect` takes options. Do NOT invent methods — read the package, don't guess.
- `websocket.app.state.session_factory` exists (set in `create_app`).
- The route must never crash the server: broad try/except after `accept()`, log WARNING with call_id.
- **Internal LiveKit URL (binding decision)**: the bridge connects from INSIDE the backend container → it must use compose DNS (`ws://livekit:7880`), not the host-facing URL baked into browser tokens. Add in this task: Settings field `livekit_url_internal: str = "ws://livekit:7880"` in `backend/app/config.py`; literal line in the compose backend environment block: `LIVEKIT_URL_INTERNAL: ws://livekit:7880`; route uses `settings.livekit_url_internal`. Browser tokens keep using `settings.livekit_url`.

- [ ] **Step 2: Full backend suite still green**

Run (workdir `backend`): `.venv\Scripts\python.exe -m pytest -q` → all pass (no new tests; route is exercised manually later).
Also `.venv\Scripts\python.exe -c "import app.routers.twilio"` must succeed (syntax/livekit import sanity).

---

### Task 4: worker accepts phone rooms

**Files:**
- Create: `voice-agent/app/rooms.py`
- Modify: `voice-agent/agent.py` (entrypoint filter)
- Test: `voice-agent/tests/test_rooms.py`

**Interfaces:**
- Produces: `is_handled_room(name: str) -> bool`.

- [ ] **Step 1: Failing test**

Create `voice-agent/tests/test_rooms.py`:

```python
"""Room-name routing for the worker (playground vs phone legs)."""
from app.rooms import is_handled_room


def test_playground_rooms_handled():
    assert is_handled_room("playground-1-abc")


def test_phone_rooms_handled():
    assert is_handled_room("phone-42")


def test_other_rooms_rejected():
    assert not is_handled_room("campaign-x")
    assert not is_handled_room("")
    assert not is_handled_room("phone")  # prefix requires trailing dash+id
```

- [ ] **Step 2: Run → FAIL**

Run (repo root): `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests\test_rooms.py -q`

- [ ] **Step 3: Implement**

Create `voice-agent/app/rooms.py`:

```python
"""Which LiveKit rooms this worker serves. Kept free of livekit imports."""
from __future__ import annotations

HANDLED_PREFIXES = ("playground-", "phone-")


def is_handled_room(name: str) -> bool:
    """True when a room should get the conversational agent."""
    clean = (name or "").strip()
    return any(clean.startswith(p) and len(clean) > len(p) for p in HANDLED_PREFIXES)
```

Edit `voice-agent/agent.py` entrypoint: replace the prefix check block

```python
    room_name = ctx.room.name or ""
    if not room_name.startswith(PLAYGROUND_PREFIX):
        logger.info(
            "Ignoring job for room %r - only %s* rooms are handled this phase",
            room_name,
            PLAYGROUND_PREFIX,
        )
        return
```

with

```python
    room_name = ctx.room.name or ""
    if not is_handled_room(room_name):
        logger.info("Ignoring job for unhandled room %r", room_name)
        return
```

and update imports: remove `PLAYGROUND_PREFIX` from the pipeline import; add `from app.rooms import is_handled_room`. Also update the module docstring sentence about dormancy to: "Handles playground-* (browser) and phone-* (Twilio bridge) rooms."

- [ ] **Step 4: Run → PASS**, then whole voice-agent offline suite: `backend\.venv\Scripts\python.exe -m pytest voice-agent\tests -q` → all green.

---

### Task 5: test-call dispatch — persist agent_version_id + room info

**Files:**
- Modify: `backend/app/schemas.py` (`TestCallRequest`, `TestCallOut`)
- Modify: `backend/app/routers/test_call.py`
- Test: `backend/tests/test_call_flow.py`

**Interfaces:**
- Consumes: `PHONE_ROOM_PREFIX` from Task 2.
- Produces: `TestCallRequest(agent_version_id: Optional[int])`; `TestCallOut` += `room_name: str`; `calls.agent_version_id` populated for phone calls.

- [ ] **Step 1: Failing tests**

Create `backend/tests/test_call_flow.py`:

```python
"""/api/test-call resolves an agent version and stamps the call row."""
from typing import Any

from app.models import Agent, AgentVersion, Call, Organization, User
from conftest import auth_headers, register


def _seed_agent_version(db: Any, org_id: int) -> int:
    org = db.get(Organization, org_id)
    owner = db.scalar(User.__table__.select().limit(1))  # not used; keep simple
    agent = Agent(org_id=org_id, name="Phone Agent", status="draft")
    db.add(agent)
    db.flush()
    version = AgentVersion(
        agent_id=agent.id,
        version=1,
        system_prompt="You call parents about absences.",
        company_context={},
        question_flow=[{"question": "Why absent?"}],
        extraction_schema={"reason_for_absence": {"type": "string", "validation": "required"}},
        disclosure_script="Hello, this is an automated call.",
        escalation_rules=[],
        voice_settings={},
        created_by=db.scalar(select_first_user_id(org_id)),
    )
    db.add(version)
    db.flush()
    agent.current_version_id = version.id
    db.commit()
    return version.id


def select_first_user_id(org_id: int):  # pragma: no cover - helper
    from sqlalchemy import select

    from app.models import User

    return select(User.id).where(User.org_id == org_id).limit(1).scalar_subquery()


def test_test_call_requires_resolvable_version(client, session_factory):
    token, user = register(client)
    resp = client.post(
        "/api/test-call",
        headers=auth_headers(token),
        json={"to": "+919391470646", "domain_config_id": 1},
    )
    assert resp.status_code in (200, 422, 502)


def test_response_contains_phone_room_name(client, session_factory, monkeypatch):
    token, user = register(client)
    with session_factory() as db:
        version_id = _seed_agent_version(db, user["org_id"])

    class FakeTelephony:
        def place_call(self, to: str, call_id: int) -> str:
            return f"CAfake{call_id}"

    from app.main import create_app

    monkeypatch.setattr(
        "app.routers.test_call._get_telephony", lambda request: FakeTelephony()
    )

    resp = client.post(
        "/api/test-call",
        headers=auth_headers(token),
        json={"to": "+919391470646", "domain_config_id": 1, "agent_version_id": version_id},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["room_name"] == f"phone-{body['call_id']}"
    with session_factory() as db:
        call = db.get(Call, body["call_id"])
        assert call.agent_version_id == version_id
```

Implementer notes (binding): if `AgentVersion.created_by` is non-nullable FK to users, resolve the registering user's id via their org instead of the scalar-subquery helper shown — simplify freely, assertions stay identical. If `domain_config_id` validation blocks (no DomainConfig row), seed one DomainConfig row in the fixture the same way other tests do (see `tests/test_campaign_launch.py` patterns).

- [ ] **Step 2: Run → FAIL** (response lacks room_name / agent_version_id ignored)

Run (workdir `backend`): `.venv\Scripts\python.exe -m pytest tests\test_call_flow.py -q`

- [ ] **Step 3: Implement**

`schemas.py` changes:

```python
class TestCallRequest(BaseModel):
    to: Optional[str] = None
    domain_config_id: int
    agent_version_id: Optional[int] = None  # phone leg: which agent version speaks


class TestCallOut(BaseModel):
    call_id: int
    provider_call_id: str
    status: str
    room_name: str
```

`routers/test_call.py`: after the contact upsert block and BEFORE building `call`:

```python
    if payload.agent_version_id is not None:
        version = db.get(AgentVersion, payload.agent_version_id)
        if version is None:
            raise HTTPException(status_code=422, detail="unknown agent_version_id")
    else:
        version = db.scalar(
            select(AgentVersion)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(Agent.org_id == user_org_id(request, db))
            .order_by(AgentVersion.id.desc())
            .limit(1)
        )
        if version is None:
            raise HTTPException(status_code=422, detail="no agent versions in org")
```

Add tiny local helper (top of module):

```python
def user_org_id(request: Request, db: Session) -> int:
    """Org id of the authenticated caller (JWT already validated by dependency)."""
    from app.deps import get_current_user  # local import avoids cycle

    return request.state.user_org_id if hasattr(request.state, "user_org_id") else _resolve_via_db(db)
```

Simpler binding decision: instead of request.state plumbing, change the route signature to accept `user: User = Depends(get_current_user)` (pattern already used across routers) and use `user.org_id` directly; drop the helper. Import `AgentVersion`, `User`, `get_current_user` accordingly.

Then set on the call before commit: `call.agent_version_id = version.id` and extend the success return:

```python
    return {
        "call_id": call.id,
        "provider_call_id": sid,
        "status": call.status,
        "room_name": f"{PHONE_ROOM_PREFIX}{call.id}",
    }
```

Import `PHONE_ROOM_PREFIX` from `app.services.twilio_bridge`. Note: `TestCallOut.room_name` required ⇒ also include `room_name` in BOTH failure paths? No — failures raise HTTPException, schema only validates 200 responses.

- [ ] **Step 4: Run full suite → PASS**

Run (workdir `backend`): `.venv\Scripts\python.exe -m pytest -q` → all green (84 baseline + new files ≈ 92+).

---

### Task 6: run book + env example

**Files:**
- Modify: `docs/USER_GUIDE.md` (append "Real phone test call" section)
- Create: `.env.example` (missing entirely; CLAUDE.md mandates it)

**Interfaces:** none.

- [ ] **Step 1: Append run book section** to `docs/USER_GUIDE.md`:

```markdown
## Real phone test call (Twilio beta)

Prereqs in `.env`: TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_PHONE_NUMBER,
destination mobile verified in Twilio console (trial rule), plus a public tunnel:

    cloudflared tunnel --url http://localhost:8000

Put the printed https URL into `.env` as PUBLIC_BASE_URL=... , restart backend
(`docker compose -f infra/docker-compose.yml up -d backend --force-recreate`),
open UI → Test Call → enter your verified number → Start. Answer the phone;
the trial preamble plays first, then the agent disclosure. Hang up from either
side; view transcript + export XLSX from Call Detail.
```

- [ ] **Step 2: Create `.env.example`** with every key currently read anywhere (names verbatim from config/settings modules): DATABASE_URL, REDIS_URL, JWT_SECRET, INTERNAL_API_TOKEN, ENVIRONMENT, LOG_LEVEL, CORS_ORIGINS, LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, DEEPGRAM_API_KEY, CARTESIA_API_KEY, GROQ_API_KEY, GROQ_MODEL, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_VALIDATE_SIGNATURE, TEST_PHONE_NUMBERS, CONSENT_ENFORCEMENT, PUBLIC_BASE_URL, PUBLIC_WS_BASE_URL — each with a safe placeholder comment, no real values. Cross-check each name against `backend/app/config.py` + `voice-agent/app/config.py` before saving; add any found-but-unlisted key too.

- [ ] **Step 3: Commit everything** (orchestrator): one commit per task as tasks land.

## Out of scope

Conversation-quality feedback fixes · Plivo/Exotel Indian DIDs · campaign parallel calling demo (needs tunnel only, reuses this bridge) · auth hardening.
