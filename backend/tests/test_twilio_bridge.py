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
