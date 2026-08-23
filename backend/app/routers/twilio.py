"""Twilio webhooks: voice (TwiML + Media Streams), status callbacks, recordings.

These are mounted WITHOUT the /api prefix so they are reachable at
{PUBLIC_BASE_URL}/twilio/... exactly as configured on Twilio.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Call, Contact
from app.services.calls_service import TWILIO_STATUS_MAP, end_call, log_call_event
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
