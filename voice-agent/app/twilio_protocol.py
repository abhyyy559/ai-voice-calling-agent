"""Twilio Media Streams WebSocket protocol: message types, encode/decode,
and outbound frame chunking.

Inbound (from Twilio, JSON text frames):
- {"event": "connected"}
- {"event": "start", "streamSid": "...", "start": {"callSid": "...",
    "customParameters": {"call_id": "<db id>"}}}
- {"event": "media", "sequenceNumber": "...", "media": {"track": "inbound",
    "chunk": 820, "timestamp": "...", "payload": "<base64 mu-law 8kHz>"}}
- {"event": "mark", "mark": {"name": "..."}}
- {"event": "stop"}

Outbound (to Twilio, JSON text frames):
- {"event": "media", "streamSid": "...", "media": {"payload": "<base64>"}}
- {"event": "mark",   "streamSid": "...", "mark": {"name": "<id>"}}
- {"event": "clear",  "streamSid": "..."}   (flush queued audio -- barge-in)

Audio is 8 kHz mu-law; one 20 ms frame = 160 bytes.  We only ever receive the
inbound track (the TwiML sets track=inbound_track), so agent echo is not an
issue for barge-in.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

from .audio import MULAW_SILENCE

SAMPLE_RATE = 8000
FRAME_MS = 20
BYTES_PER_SAMPLE = 1  # mu-law: 1 byte per sample
FRAME_SIZE = SAMPLE_RATE * BYTES_PER_SAMPLE * FRAME_MS // 1000  # 160 bytes


@dataclass
class TwilioMessage:
    """A parsed inbound Twilio Media Streams message."""

    kind: str  # "connected" | "start" | "media" | "mark" | "stop" | "unknown"
    stream_sid: Optional[str] = None
    call_sid: Optional[str] = None
    call_id: Optional[str] = None  # our DB id, from customParameters
    audio: Optional[bytes] = None  # decoded mu-law payload (media only)
    mark_name: Optional[str] = None
    raw: dict = field(default_factory=dict)


def parse_message(text: str) -> TwilioMessage:
    """Parse one inbound JSON text frame from Twilio."""
    data: dict = json.loads(text)
    event = data.get("event", "unknown")
    msg = TwilioMessage(kind=event, raw=data)
    if event == "start":
        msg.stream_sid = data.get("streamSid")
        start = data.get("start") or {}
        msg.call_sid = start.get("callSid")
        params = start.get("customParameters") or {}
        msg.call_id = params.get("call_id") or params.get("callId")
    elif event == "media":
        msg.stream_sid = data.get("streamSid")
        payload = (data.get("media") or {}).get("payload")
        msg.audio = base64.b64decode(payload) if payload else b""
    elif event == "mark":
        msg.mark_name = (data.get("mark") or {}).get("name")
    return msg


def chunk_frames(audio: bytes, frame_size: int = FRAME_SIZE,
                 pad_last: bool = True) -> Iterator[bytes]:
    """Split mu-law audio into Twilio-sized frames (160 bytes = 20 ms @ 8kHz).

    The final partial frame is padded with mu-law silence (0xFF) so Twilio
    always receives whole 160-byte frames.
    """
    if frame_size <= 0:
        raise ValueError("frame_size must be positive")
    if not audio:
        return
    for i in range(0, len(audio), frame_size):
        frame = audio[i:i + frame_size]
        if pad_last and len(frame) < frame_size:
            frame = frame + bytes([MULAW_SILENCE]) * (frame_size - len(frame))
        yield frame


def encode_media_frame(stream_sid: str, frame: bytes) -> str:
    """Build an outbound media message for one audio frame."""
    return json.dumps({
        "event": "media",
        "streamSid": stream_sid,
        "media": {"payload": base64.b64encode(frame).decode("ascii")},
    })


def encode_mark(stream_sid: str, name: str) -> str:
    """Build an outbound mark message (playback sentinel after queued audio)."""
    return json.dumps({
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {"name": name},
    })


def encode_clear(stream_sid: str) -> str:
    """Build an outbound clear message (flush queued audio -- barge-in)."""
    return json.dumps({"event": "clear", "streamSid": stream_sid})


def encode_media_batch(stream_sid: str, audio: bytes) -> list[str]:
    """Convenience: chunk + encode a whole audio buffer, one message per frame.

    Frames are handed to Twilio as fast as it can buffer them -- Twilio paces
    playback itself, so no artificial sleep is applied here.
    """
    return [
        encode_media_frame(stream_sid, frame) for frame in chunk_frames(audio)
    ]


def decode_payload(payload: str) -> bytes:
    """Decode a base64 media payload to raw mu-law bytes."""
    return base64.b64decode(payload)


def payload_duration_seconds(num_bytes: int) -> float:
    """Duration of a mu-law buffer at 8 kHz (1 byte per sample)."""
    return num_bytes / float(SAMPLE_RATE)


def make_mark_name(prefix: str = "mark") -> str:
    """A unique-ish mark name (monotonic within a process is not required)."""
    import itertools
    import uuid

    return f"{prefix}-{uuid.uuid4().hex[:12]}"


_COUNTER = itertools.count()  # type: ignore[name-defined]  # re-imported above


def next_mark_name(prefix: str = "mark") -> str:
    """Process-unique, monotonic mark name."""
    return f"{prefix}-{next(_COUNTER)}"


def safe_json_loads(text: str) -> Optional[dict[str, Any]]:
    """Parse JSON, returning None on failure (never raise on bad frames)."""
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        return None
    return value if isinstance(value, dict) else None
