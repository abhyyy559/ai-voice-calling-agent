"""Test-call endpoint: place an immediate single call to an allowlisted number.

Test calls bypass the dialer (campaign stays out of `running`), but still
create contact + call rows so transcripts and reports flow through the same
pipeline as campaign calls.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Agent, AgentVersion, Call, Campaign, Contact, DomainConfig, User
from app.schemas import TestCallOut, TestCallRequest
from app.services.calls_service import log_call_event
from app.services.import_service import normalize_phone
from app.services.telephony import TelephonyClient
from app.services.twilio_bridge import PHONE_ROOM_PREFIX
from app.timeutil import utcnow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["test-call"])

TEST_CAMPAIGN_NAME = "Test Calls"


def _get_telephony(request: Request) -> TelephonyClient:
    return request.app.state.telephony


@router.post("/test-call", response_model=TestCallOut)
def place_test_call(
    payload: TestCallRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    settings = request.app.state.settings
    allowlist = [
        normalize_phone(p)[0] for p in settings.test_phone_number_list
    ]

    target: Optional[str] = None
    if payload.to:
        target, ok = normalize_phone(payload.to)
        if not ok:
            raise HTTPException(status_code=422, detail=f"invalid phone number: {payload.to}")
    elif allowlist:
        target = allowlist[0]
    else:
        raise HTTPException(
            status_code=422, detail="no 'to' given and TEST_PHONE_NUMBERS is empty"
        )

    if settings.consent_enforcement and target not in allowlist:
        raise HTTPException(
            status_code=422,
            detail=f"{target} is not in TEST_PHONE_NUMBERS; consent enforcement is on",
        )

    if db.get(DomainConfig, payload.domain_config_id) is None:
        raise HTTPException(status_code=422, detail="unknown domain_config_id")

    if payload.agent_version_id is not None:
        version = db.scalar(
            select(AgentVersion)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(AgentVersion.id == payload.agent_version_id, Agent.org_id == user.org_id)
        )
        if version is None:
            raise HTTPException(status_code=422, detail="unknown agent_version_id")
    else:
        version = db.scalar(
            select(AgentVersion)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(Agent.org_id == user.org_id)
            .order_by(AgentVersion.id.desc())
            .limit(1)
        )
        if version is None:
            raise HTTPException(status_code=422, detail="no agent versions in org")

    campaign = db.scalar(select(Campaign).where(Campaign.name == TEST_CAMPAIGN_NAME))
    if campaign is None:
        campaign = Campaign(
            name=TEST_CAMPAIGN_NAME, domain_config_id=payload.domain_config_id, status="draft"
        )
        db.add(campaign)
        db.flush()
    elif campaign.domain_config_id != payload.domain_config_id:
        campaign.domain_config_id = payload.domain_config_id

    contact = db.scalar(
        select(Contact).where(Contact.campaign_id == campaign.id, Contact.phone == target)
    )
    if contact is None:
        contact = Contact(
            campaign_id=campaign.id,
            name=f"Test Call ({target})",
            phone=target,
            status="pending_review",
            consent=True,
            consent_source="test_allowlist",
        )
        db.add(contact)
        db.flush()

    now = utcnow()
    call = Call(
        campaign_id=campaign.id,
        contact_id=contact.id,
        agent_version_id=version.id,
        status="queued",
        started_at=now,
    )
    db.add(call)
    db.commit()

    telephony: TelephonyClient = _get_telephony(request)
    try:
        sid = telephony.place_call(target, call.id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("test call placement failed: %s", exc)
        call.status = "failed"
        call.ended_at = utcnow()
        log_call_event(db, call.id, "dial_failed", {"error": str(exc)})
        contact.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"telephony error: {exc}") from exc

    call.provider_call_id = sid
    call.status = "ringing"
    contact.status = "calling"
    contact.last_call_id = call.id
    log_call_event(db, call.id, "test_call_placed", {"to": target})
    db.commit()

    return {
        "call_id": call.id,
        "provider_call_id": sid,
        "status": call.status,
        "room_name": f"{PHONE_ROOM_PREFIX}{call.id}",
    }
