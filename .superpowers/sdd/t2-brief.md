# Task 2 Brief: bridge primitives — event parser + phone-room token

**Files:**
- Create: `backend/app/services/twilio_bridge.py`
- Test: `backend/tests/test_twilio_bridge.py`

**Interfaces (locked):**
- Produces: `PHONE_ROOM_PREFIX = "phone-"`, `MediaEvent` dataclass (`event`, `stream_sid`, `media_payload`, `call_id`), `parse_stream_event(raw) -> MediaEvent` (raises ValueError on junk), `build_phone_room_token(settings, *, call_id: int, version_id: int, contact: dict) -> tuple[str, str]`.
- Consumes: nothing from other tasks.

- [ ] **Step 1: Failing tests** — create `backend/tests/test_twilio_bridge.py`:

```python
"""Pure logic for the Twilio media bridge: event parsing + room token minting."""
import base64
import json

from app.services.twilio_bridge import (
    PHONE_ROOM_PREFIX,
    build_phone_room_token,
    parse_stream_event,
)

from conftest import make_settings


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
    assert '"call_id": "84"' in claims["metadata"]
    assert claims["video"]["room"] == room
```

FIRST check `make_settings` in `backend/tests/conftest.py`: read its real signature. If it takes a kwargs dict or different param style, adapt the two construction lines to match its contract — do not modify conftest.

- [ ] **Step 2: Run → expect FAIL** (workdir backend): `.venv\Scripts\python.exe -m pytest tests\test_twilio_bridge.py -q`

- [ ] **Step 3: Implement** — create `backend/app/services/twilio_bridge.py`:

```python
"""Twilio Media Streams bridge primitives (pure logic, unit-testable).

routers/twilio.py keeps the websocket route thin: parse events with
parse_stream_event, mint one room token per stream via build_phone_room_token.
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

- [ ] **Step 4: Run → PASS** (5 tests). Also run full suite: `.venv\Scripts\python.exe -m pytest -q` → everything green.

- [ ] **Step 5: Report** to `.superpowers/sdd/t2-report.md`; return status/files/one-line results/concerns only.

## Global Constraints

PowerShell 5.1; NO git commands; touch ONLY the two listed files; never print full tokens in logs/reports (first 12 chars max).
