"""Call list + detail endpoints (org-scoped per contract §4)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Call, Campaign, Contact, ExtractedField, Transcript, User
from app.schemas import CampaignCallOut, CallDetailOut

router = APIRouter(prefix="/api", tags=["calls"])


def _call_org_id(db: Session, call: Call) -> Any:
    """Effective org of a call: denormalized column, else campaign lineage."""
    if call.org_id is not None:
        return call.org_id
    campaign = db.get(Campaign, call.campaign_id) if call.campaign_id else None
    return campaign.org_id if campaign else None


@router.get("/campaigns/{campaign_id}/calls", response_model=list[CampaignCallOut])
def list_campaign_calls(
    campaign_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    campaign = db.get(Campaign, campaign_id)
    if campaign is None or campaign.org_id != user.org_id:
        raise HTTPException(status_code=404, detail="campaign not found")
    rows = db.execute(
        select(Call, Contact.name, Contact.phone)
        .join(Contact, Contact.id == Call.contact_id)
        .where(Call.campaign_id == campaign_id)
        .order_by(Call.id.desc())
    ).all()
    return [
        {
            "id": call.id,
            "campaign_id": call.campaign_id,
            "contact_id": call.contact_id,
            "provider_call_id": call.provider_call_id,
            "status": call.status,
            "started_at": call.started_at,
            "answered_at": call.answered_at,
            "ended_at": call.ended_at,
            "duration_seconds": call.duration_seconds,
            "recording_url": call.recording_url,
            "summary": call.summary,
            "outcome": call.outcome,
            "flagged_for_human": call.flagged_for_human,
            "cost": call.cost,
            "latency": call.latency,
            "created_at": call.created_at,
            "contact_name": name,
            "contact_phone": phone,
        }
        for call, name, phone in rows
    ]


@router.get("/calls/{call_id}", response_model=CallDetailOut)
def get_call(
    call_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    call = db.get(Call, call_id)
    if call is None or _call_org_id(db, call) != user.org_id:
        raise HTTPException(status_code=404, detail="call not found")
    contact = db.get(Contact, call.contact_id)
    turns = db.scalars(
        select(Transcript).where(Transcript.call_id == call.id).order_by(Transcript.turn_index)
    ).all()
    fields = db.scalars(
        select(ExtractedField).where(ExtractedField.call_id == call.id).order_by(ExtractedField.id)
    ).all()
    return {
        "id": call.id,
        "campaign_id": call.campaign_id,
        "contact_id": call.contact_id,
        "provider_call_id": call.provider_call_id,
        "status": call.status,
        "started_at": call.started_at,
        "answered_at": call.answered_at,
        "ended_at": call.ended_at,
        "duration_seconds": call.duration_seconds,
        "recording_url": call.recording_url,
        "summary": call.summary,
        "outcome": call.outcome,
        "flagged_for_human": call.flagged_for_human,
        "cost": call.cost,
        "latency": call.latency,
        "created_at": call.created_at,
        "contact_name": contact.name if contact else None,
        "contact_phone": contact.phone if contact else None,
        "transcript": [
            {
                "turn_index": t.turn_index,
                "speaker": t.speaker,
                "text": t.text,
                "timestamp": t.timestamp,
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
    }
