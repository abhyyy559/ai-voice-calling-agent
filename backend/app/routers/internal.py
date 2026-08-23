"""Internal API consumed by the voice-agent service (no auth this phase).

- GET  /internal/calls/{call_id}/context — everything the agent needs to run
  the call (contact, campaign, full domain config JSON).
- POST /internal/calls/{call_id}/report  — best-effort writes of transcript
  turns, extracted fields, summary, metrics and status. Invalid payloads get
  a 400; this endpoint never returns a 500 for bad input.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Call, Campaign, Contact, DomainConfig
from app.services.calls_service import apply_report

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/calls/{call_id}/context")
def call_context(call_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="call not found")
    contact = db.get(Contact, call.contact_id)
    campaign = db.get(Campaign, call.campaign_id)
    domain_config = (
        db.get(DomainConfig, campaign.domain_config_id)
        if campaign and campaign.domain_config_id
        else None
    )
    return {
        "call": {"id": call.id, "status": call.status},
        "contact": {
            "name": contact.name if contact else None,
            "phone": contact.phone if contact else None,
            "external_id": contact.external_id if contact else None,
            "custom_fields": (contact.custom_fields or {}) if contact else {},
        },
        "campaign": {"name": campaign.name if campaign else None},
        "domain_config": domain_config.config if domain_config else None,
    }


@router.post("/calls/{call_id}/report")
def call_report(
    call_id: int,
    body: dict = Body(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    call = db.get(Call, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="call not found")
    if not isinstance(body, dict) or "type" not in body:
        raise HTTPException(status_code=400, detail="body must be {type, payload}")
    try:
        apply_report(db, call, body["type"], body.get("payload"))
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}
