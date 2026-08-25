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

# Twilio always sends {"event":"connected"} first; the handshake must tolerate
# junk before the mandatory "start" frame but cannot wait forever.
HANDSHAKE_TIMEOUT_SECONDS = 10.0


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
    stream = Stream(url=f"{ws_base_url}/twilio/media", track="inbound_track")
    stream.parameter(name="call_id", value=str(call_id))
    connect.append(stream)
    response.append(connect)
    return str(response)


# --- media streams bridge (Twilio <-> LiveKit phone rooms) -------------------


def _make_frame(pcm16_8k: bytes) -> Any:
    """Build an rtc.AudioFrame from 16-bit LE PCM at 8 kHz."""
    from livekit import rtc

    if hasattr(rtc.AudioFrame, "from_s16"):
        return rtc.AudioFrame.from_s16(pcm16_8k, sample_rate=8000, num_channels=1)
    return rtc.AudioFrame(
        data=pcm16_8k,
        samples_per_channel=len(pcm16_8k) // 2,
        sample_rate=8000,
        num_channels=1,
    )


async def _pump_twilio_to_room(
    ws: WebSocket, source: Any, stream_sid_box: dict[str, str]
) -> None:
    """Decode caller mu-law frames and publish them into the LiveKit room."""
    import base64
    import binascii

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
        try:
            pcm = base64.b64decode(ev.media_payload)
        except binascii.Error:
            logger.debug("dropping non-base64 twilio media frame")
            continue
        frame = _make_frame(ulaw_to_pcm16(pcm))
        await source.capture_frame(frame)


def _put_sentinel(queue: Any) -> None:
    """Enqueue the b"" end-of-stream sentinel, dropping backlog if full."""
    import asyncio

    try:
        queue.put_nowait(b"")
    except asyncio.QueueFull:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        try:
            queue.put_nowait(b"")
        except asyncio.QueueFull:
            pass


async def _drain_track(track: Any, queue: Any) -> None:
    """Forward one subscribed remote audio track into the bridge queue."""
    import asyncio

    from livekit import rtc

    from app.services.g711 import downsample_pcm16, pcm16_to_ulaw

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
        _put_sentinel(queue)


async def _pump_room_to_twilio(
    queue: Any, ws: WebSocket, stream_sid_box: dict[str, str]
) -> None:
    """Send queued agent mu-law frames to Twilio as media messages.

    Exits cleanly when any drain puts the b"" sentinel (track ended,
    participant gone, room disconnected).
    """
    import asyncio
    import base64

    getter = asyncio.ensure_future(queue.get())
    try:
        while True:
            await asyncio.wait({getter})
            ulaw = getter.result()
            getter = asyncio.ensure_future(queue.get())
            if ulaw == b"":
                break
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
        getter.cancel()


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

    # --- handshake: read until the mandatory `start` event (10s deadline) ----
    loop = asyncio.get_running_loop()
    deadline = loop.time() + HANDSHAKE_TIMEOUT_SECONDS
    while True:
        remaining = deadline - loop.time()
        if remaining <= 0:
            logger.warning("twilio media handshake timed out")
            await _close(4400)
            return
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=remaining)
        except asyncio.TimeoutError:
            logger.warning("twilio media handshake timed out")
            await _close(4400)
            return
        except WebSocketDisconnect:
            return
        try:
            ev = _parse_bridge_event(raw)
        except ValueError:
            continue  # tolerate unparseable junk before start
        if ev.event == "connected":
            continue  # Twilio's mandatory first greeting
        if ev.event != "start" or not ev.call_id:
            await _close(4400)
            return
        try:
            call_pk = int(ev.call_id)
        except ValueError:
            await _close(4400)
            return
        break

    with websocket.app.state.session_factory() as db:
        call = db.get(Call, call_pk)
        if call is None or call.agent_version_id is None:
            await _close(4404)
            return
        if not ev.call_sid or ev.call_sid != call.provider_call_id:
            logger.warning("callSid mismatch on media bridge for call %s", call_pk)
            await _close(4403)
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

    queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=100)
    drains: list[asyncio.Task[None]] = []
    seen_tracks: set[Any] = set()
    room_gone = asyncio.Event()

    def _on_frame(
        track: Any, _publication: Any = None, _participant: Any = None
    ) -> None:
        key = getattr(track, "sid", None) or id(track)
        if key in seen_tracks:
            return  # belt-and-braces scan may double-report an existing track
        seen_tracks.add(key)
        drains.append(asyncio.ensure_future(_drain_track(track, queue)))

    def _on_room_disconnected(_room: Any = None) -> None:
        room_gone.set()
        _put_sentinel(queue)

    # Register BEFORE connect so no track_subscribed event can be missed.
    room.on("track_subscribed", _on_frame)
    room.on("disconnected", _on_room_disconnected)

    logger.info("media bridge joining %s (call %s)", room_name, ev.call_id)
    await room.connect(settings.livekit_url_internal, token)

    # Belt-and-braces: feed tracks already published before we finished joining.
    for participant in list(room.remote_participants.values()):
        for publication in list(participant.track_publications.values()):
            track = publication.track
            if track is not None and track.kind == rtc.TrackKind.KIND_AUDIO:
                _on_frame(track)

    source = rtc.AudioSource(sample_rate=8000, num_channels=1)
    caller_track = rtc.LocalAudioTrack.create_audio_track(f"twilio-{call_pk}", source)
    await room.local_participant.publish_track(caller_track)

    to_agent = asyncio.ensure_future(_pump_twilio_to_room(websocket, source, stream_sid_box))
    from_agent = asyncio.ensure_future(_pump_room_to_twilio(queue, websocket, stream_sid_box))
    room_gone_waiter = asyncio.ensure_future(room_gone.wait())
    tasks: tuple[asyncio.Future[Any], ...] = (to_agent, from_agent, room_gone_waiter)
    try:
        await asyncio.wait(set(tasks), return_when=asyncio.FIRST_COMPLETED)
    finally:
        for task in (*tasks, *drains):
            task.cancel()
        await asyncio.gather(*tasks, *drains, return_exceptions=True)
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
