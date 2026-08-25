"""Twilio webhooks: voice (TwiML + Media Streams), status callbacks, recordings.

These are mounted WITHOUT the /api prefix so they are reachable at
{PUBLIC_BASE_URL}/twilio/... exactly as configured on Twilio.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Call, Contact
from app.services.calls_service import TWILIO_STATUS_MAP, end_call, log_call_event
from app.services.twilio_bridge import build_phone_room_token
from app.services.twilio_bridge import parse_stream_event as _parse_bridge_event
from app.timeutil import utcnow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["twilio"])

XML_MEDIA_TYPE = "application/xml"


async def _check_signature(request: Request, form) -> None:  # type: ignore[no-untyped-def]
    """Validate X-Twilio-Signature when TWILIO_VALIDATE_SIGNATURE is enabled."""
    settings = request.app.state.settings
    if not getattr(settings, "twilio_validate_signature", False):
        return
    from twilio.request_validator import RequestValidator

    validator = RequestValidator(settings.twilio_auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    if not validator.validate(str(request.url), dict(form), signature):
        raise HTTPException(status_code=403, detail="invalid Twilio signature")


def _build_voice_twiml(ws_base_url: str, call_id: int) -> str:
    """TwiML connecting the call to the voice-agent Media Stream."""
    from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

    response = VoiceResponse()
    connect = Connect()
    stream = Stream(url=f"{ws_base_url}/media", track="inbound_track")
    stream.parameter(name="call_id", value=str(call_id))
    connect.append(stream)
    response.append(connect)
    return str(response)


# --- media streams bridge (Twilio <-> LiveKit phone rooms) -------------------


def _make_frame(pcm8k: bytes) -> Any:
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


async def _pump_twilio_to_room(
    ws: WebSocket, source: Any, stream_sid_box: dict[str, str]
) -> None:
    """Decode caller mu-law frames and publish them into the LiveKit room."""
    import base64

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
        frame = _make_frame(ulaw_to_pcm16(base64.b64decode(ev.media_payload)))
        await source.capture_frame(frame)


async def _pump_room_to_twilio(
    room: Any, ws: WebSocket, stream_sid_box: dict[str, str]
) -> None:
    """Subscribe agent audio and forward it to Twilio as mu-law media messages."""
    import asyncio
    import base64

    from app.services.g711 import downsample_pcm16, pcm16_to_ulaw

    queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)
    drains: list[asyncio.Task[None]] = []

    async def _drain(track: Any) -> None:
        from livekit import rtc

        audio_stream = rtc.AudioStream(track)
        try:
            # track_subscribed hands us a Track (not frames); AudioStream is the
            # async iterator over AudioFrameEvent in the installed SDK.
            async for event in audio_stream:
                pcm = bytes(event.frame.data)
                factor = max(1, round(int(event.frame.sample_rate) / 8000))
                if factor > 1:
                    pcm = downsample_pcm16(pcm, factor)
                try:
                    queue.put_nowait(pcm16_to_ulaw(pcm))
                except asyncio.QueueFull:
                    pass  # drop backlog: live caller audio wins over stale frames
        finally:
            await audio_stream.aclose()

    def _on_track_subscribed(
        track: Any, _publication: Any = None, _participant: Any = None
    ) -> None:
        drains.append(asyncio.ensure_future(_drain(track)))

    room.on("track_subscribed", _on_track_subscribed)
    try:
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
    finally:
        for task in drains:
            task.cancel()


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
    try:
        call_pk = int(ev.call_id)
    except ValueError:
        await _close(4400)
        return

    with websocket.app.state.session_factory() as db:
        call = db.get(Call, call_pk)
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
        call_id=call_pk,
        version_id=version_id,
        contact={k: str(v) for k, v in contact_card.items() if v},
    )
    room = rtc.Room()
    stream_sid_box: dict[str, str] = {"sid": ev.stream_sid}
    logger.info("media bridge joining %s (call %s)", room_name, ev.call_id)
    await room.connect(settings.livekit_url_internal, token)

    source = rtc.AudioSource(sample_rate=8000, num_channels=1)
    caller_track = rtc.LocalAudioTrack.create_audio_track(f"twilio-{call_pk}", source)
    await room.local_participant.publish_track(caller_track)

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


@router.post("/voice")
async def twilio_voice(
    request: Request,
    call_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Answer webhook: return TwiML that bridges the call to the media stream."""
    form = await request.form()
    await _check_signature(request, form)

    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="unknown call_id")

    now = utcnow()
    if call.status not in ("in_progress", "completed"):
        call.status = "in_progress"
    if call.answered_at is None:
        call.answered_at = now
    contact = db.get(Contact, call.contact_id)
    if contact is not None and contact.status != "completed":
        contact.status = "calling"
    log_call_event(db, call.id, "voice_webhook", {"CallSid": form.get("CallSid")})
    db.commit()

    settings = request.app.state.settings
    xml = _build_voice_twiml(settings.media_ws_base_url, call_id)
    return Response(content=xml, media_type=XML_MEDIA_TYPE)


@router.post("/status")
async def twilio_status(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Status callback: map Twilio events onto call/contact/campaign state."""
    form = await request.form()
    await _check_signature(request, form)

    call_sid: Optional[str] = form.get("CallSid")
    call_status: Optional[str] = form.get("CallStatus")
    call_duration: Optional[str] = form.get("CallDuration")

    call = db.scalar(select(Call).where(Call.provider_call_id == call_sid)) if call_sid else None
    if call is None:
        logger.warning("status webhook for unknown CallSid=%s", call_sid)
        return Response(status_code=200)

    log_call_event(db, call.id, f"twilio_status:{call_status}", dict(form))

    mapped = TWILIO_STATUS_MAP.get(str(call_status), "")
    now = utcnow()
    contact = db.get(Contact, call.contact_id)

    if mapped == "in_progress":
        call.status = "in_progress"
        if call.answered_at is None:
            call.answered_at = now
        if contact is not None:
            contact.status = "calling"
    elif mapped in ("queued", "ringing"):
        if call.status == "queued":
            call.status = mapped
    elif mapped in ("completed", "no_answer", "busy", "failed", "canceled"):
        if call.status not in ("completed",):  # allow late webhooks after completion
            duration = float(call_duration) if call_duration else None
            settings = request.app.state.settings
            if contact is not None:
                end_call(db, call, contact, mapped, settings, now=now, duration_seconds=duration)
            else:
                call.status = mapped
                call.ended_at = now
                call.duration_seconds = duration

    db.commit()
    return Response(status_code=200)


@router.post("/recording")
async def twilio_recording(
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    """Recording-status callback: persist the recording URL."""
    form = await request.form()
    await _check_signature(request, form)

    call_sid: Optional[str] = form.get("CallSid")
    recording_url: Optional[str] = form.get("RecordingUrl")
    call = db.scalar(select(Call).where(Call.provider_call_id == call_sid)) if call_sid else None
    if call is not None and recording_url:
        call.recording_url = recording_url
        log_call_event(
            db, call.id, "twilio_recording", {"RecordingUrl": recording_url, "RecordingSid": form.get("RecordingSid")}
        )
        db.commit()
    else:
        logger.warning("recording webhook for unknown CallSid=%s", call_sid)
    return Response(status_code=200)
