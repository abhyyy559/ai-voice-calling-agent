"""Web playground (frozen contract §4).

Browser mic joins a LiveKit room via a short-lived token issued here; the same
voice-agent worker that handles phone calls accepts the room job. Sessions are
recorded as ``calls(kind='playground')`` — zero telephony minutes burned.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_db
from app.deps import get_current_user, get_org_or_404
from app.models import Agent, AgentVersion, Call, ExtractedField, Transcript, User
from app.timeutil import utcnow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/playground", tags=["playground"])

_TOKEN_TTL = timedelta(hours=1)
_LATENCY_METRICS = ("stt_final_ms", "llm_first_token_ms", "tts_first_audio_ms", "e2e_ms")


class SessionCreate(BaseModel):
    agent_version_id: int = Field(gt=0)


def _issue_room_token(settings: Settings, room_name: str, identity: str, metadata: dict[str, Any]) -> str:
    """Sign a LiveKit room-join token (TTL 1h). Requires configured credentials."""
    if not (settings.livekit_api_key and settings.livekit_api_secret):
        raise HTTPException(
            status_code=503,
            detail="LiveKit credentials not configured (set LIVEKIT_API_KEY / LIVEKIT_API_SECRET)",
        )
    from livekit import api as livekit_api  # lazy: only needed on this endpoint

    token = (
        livekit_api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(identity)
        .with_metadata(json.dumps(metadata))
        .with_grants(
            livekit_api.VideoGrants(room_join=True, room=room_name)
        )
        .with_ttl(_TOKEN_TTL)
    )
    return token.to_jwt()


def _get_own_playground_call(db: Session, call_id: int, user: User) -> Call:
    call = db.get(Call, call_id)
    if call is None or call.kind != "playground" or call.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="not found")
    return call


def _set_room_metadata_best_effort(
    settings: Settings, room_name: str, version_id: int, call_id: int
) -> None:
    """Mirror token metadata onto the room so the worker sees it immediately.

    Best-effort: if the LiveKit server is unreachable the participant-token
    fallback in the voice agent still carries {version_id, call_id}.
    """
    import asyncio

    try:
        from livekit import api as livekit_api

        async def _update() -> None:
            client = livekit_api.LiveKitAPI(
                settings.livekit_url,
                settings.livekit_api_key,
                settings.livekit_api_secret,
            )
            try:
                await client.room.update_room_metadata(
                    livekit_api.UpdateRoomMetadataRequest(
                        room=room_name,
                        metadata=json.dumps(
                            {"version_id": version_id, "call_id": call_id}
                        ),
                    )
                )
            finally:
                await client.aclose()

        asyncio.run(_update())
    except Exception:
        logger.warning(
            "Could not set room metadata for %s (participant-token fallback applies)",
            room_name,
            exc_info=True,
        )


@router.post("/sessions")
def create_session(
    payload: SessionCreate,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settings: Settings = request.app.state.settings
    version = db.get(AgentVersion, payload.agent_version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="not found")
    # Org check through the parent agent; foreign orgs get 404 (no leak).
    agent = get_org_or_404(db, Agent, version.agent_id, user.org_id)

    room_name = f"playground-{user.org_id}-{uuid.uuid4()}"
    call = Call(
        kind="playground",
        status="in_progress",
        org_id=user.org_id,
        agent_version_id=version.id,
        started_at=utcnow(),
    )
    db.add(call)
    db.flush()  # need call.id for the room metadata before signing

    token = _issue_room_token(
        settings,
        room_name,
        identity=f"user-{user.id}",
        metadata={"version_id": version.id, "call_id": call.id},
    )
    _set_room_metadata_best_effort(settings, room_name, version.id, call.id)
    logger.info(
        "playground session created call_id=%s org=%s agent=%s version=%s room=%s",
        call.id,
        user.org_id,
        agent.name,
        version.version,
        room_name,
    )
    db.commit()

    return {
        "call_id": call.id,
        "room_name": room_name,
        "livekit_token": token,
        "livekit_url": settings.livekit_url,
    }


def _latency_summary(turns: list[Transcript]) -> dict[str, Any]:
    """Per-metric n/avg/p50/p95 over the turns that reported each metric."""
    summary: dict[str, Any] = {}
    for metric in _LATENCY_METRICS:
        values = sorted(
            value for turn in turns if (value := getattr(turn, metric)) is not None
        )
        if not values:
            continue
        count = len(values)

        def percentile(fraction: float, vals: list[float] = values) -> float:
            index = min(count - 1, round(fraction * (count - 1)))
            return round(vals[index], 1)

        summary[metric] = {
            "n": count,
            "avg": round(sum(values) / count, 1),
            "p50": percentile(0.5),
            "p95": percentile(0.95),
        }
    return summary


@router.post("/sessions/{call_id}/complete")
def complete_session(
    call_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Finalize a playground session and return transcript/fields/latency."""
    call = _get_own_playground_call(db, call_id, user)
    if call.status == "in_progress":
        now = utcnow()
        call.status = "completed"
        call.ended_at = now
        if call.started_at is not None:
            call.duration_seconds = (now - call.started_at).total_seconds()
    db.commit()

    turns = db.scalars(
        select(Transcript)
        .where(Transcript.call_id == call.id)
        .order_by(Transcript.turn_index)
    ).all()
    fields = db.scalars(
        select(ExtractedField)
        .where(ExtractedField.call_id == call.id)
        .order_by(ExtractedField.id)
    ).all()

    return {
        "call_id": call.id,
        "status": call.status,
        "summary": call.summary,
        "outcome": call.outcome,
        "flagged_for_human": call.flagged_for_human,
        "duration_seconds": call.duration_seconds,
        "transcript": [
            {
                "turn_index": t.turn_index,
                "speaker": t.speaker,
                "text": t.text,
                "timestamp": t.timestamp,
                **{m: getattr(t, m) for m in _LATENCY_METRICS},
            }
            for t in turns
        ],
        "extracted_fields": [
            {
                "field_name": f.field_name,
                "field_value": f.field_value,
                "source_turn_index": f.source_turn_index,
                "confidence": f.confidence,
            }
            for f in fields
        ],
        "latency": _latency_summary(list(turns)),
    }
