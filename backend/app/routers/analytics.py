"""Org-scoped analytics for the Overview page (GET /api/analytics/summary).

Tenancy: a call belongs to the caller's org when its denormalized
``calls.org_id`` matches, else when its campaign's org matches — the same
"effective org" rule used by the call detail endpoint. Transcript latency
stats and extracted-field counts are computed over that same call set.
"""
from __future__ import annotations

import math
import statistics
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Agent, AgentVersion, Call, Campaign, ExtractedField, Transcript, User
from app.schemas import AnalyticsSummaryOut
from app.timeutil import utcnow

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

RECENT_CALLS_LIMIT = 8


def _org_call_filter(org_id: int):
    """SQL filter matching calls whose effective org is ``org_id``."""
    return or_(Call.org_id == org_id, Campaign.org_id == org_id)


def _percentile(sorted_values: list[float], pct: float) -> float | None:
    """Nearest-rank percentile on a pre-sorted list."""
    if not sorted_values:
        return None
    idx = max(0, min(len(sorted_values) - 1, math.ceil(pct * len(sorted_values)) - 1))
    value = sorted_values[idx]
    return round(float(value), 1)


@router.get("/summary", response_model=AnalyticsSummaryOut)
def analytics_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    org_filter = _org_call_filter(user.org_id)

    # --- call set ----------------------------------------------------------
    calls = db.scalars(
        select(Call).outerjoin(Campaign, Campaign.id == Call.campaign_id).where(org_filter)
    ).all()

    total_calls = len(calls)
    completed_calls = sum(1 for c in calls if c.status == "completed")
    success_rate_pct = round((completed_calls / total_calls * 100.0), 1) if total_calls else 0.0
    call_ids = [c.id for c in calls]

    # --- e2e latency from per-turn transcripts ------------------------------
    e2e_values: list[float] = []
    total_extracted_fields = 0
    if call_ids:
        e2e_rows = db.execute(
            select(Transcript.e2e_ms)
            .where(
                and_(
                    Transcript.call_id.in_(call_ids),
                    Transcript.e2e_ms.isnot(None),
                )
            )
        ).scalars().all()
        e2e_values = [float(v) for v in e2e_rows]

        field_ids = db.scalars(
            select(ExtractedField.id).where(ExtractedField.call_id.in_(call_ids))
        ).all()
        total_extracted_fields = len(field_ids)

    avg_e2e_ms = round(sum(e2e_values) / len(e2e_values), 1) if e2e_values else None
    median_e2e_ms = (
        round(float(statistics.median(e2e_values)), 1) if e2e_values else None
    )
    p95_e2e_ms = _percentile(sorted(e2e_values), 0.95)

    # --- last-7-day histogram (UTC day buckets, zero-filled) ---------------
    today = utcnow().date()
    start_day = today - timedelta(days=6)
    buckets: dict[str, int] = {
        (start_day + timedelta(days=i)).isoformat(): 0 for i in range(7)
    }
    for call in calls:
        stamp = call.started_at or call.created_at
        if stamp is None:
            continue
        key = stamp.date().isoformat()
        if key in buckets:
            buckets[key] += 1
    calls_last_7d = [{"date": day, "count": count} for day, count in buckets.items()]

    # --- recent calls with resolved agent names ----------------------------
    version_ids = {c.agent_version_id for c in calls[:RECENT_CALLS_LIMIT] if c.agent_version_id}
    agent_names: dict[int, str] = {}
    if version_ids:
        rows = db.execute(
            select(AgentVersion.id, Agent.name)
            .join(Agent, Agent.id == AgentVersion.agent_id)
            .where(AgentVersion.id.in_(version_ids))
        ).all()
        agent_names = {vid: name for vid, name in rows}

    recent_source = sorted(calls, key=lambda c: c.id, reverse=True)[:RECENT_CALLS_LIMIT]
    recent_calls = [
        {
            "id": c.id,
            "status": c.status,
            "kind": c.kind or "phone",
            "duration_seconds": c.duration_seconds,
            "started_at": c.started_at,
            "agent_name": agent_names.get(c.agent_version_id),
        }
        for c in recent_source
    ]

    return {
        "total_calls": total_calls,
        "completed_calls": completed_calls,
        "success_rate_pct": success_rate_pct,
        "avg_e2e_ms": avg_e2e_ms,
        "median_e2e_ms": median_e2e_ms,
        "p95_e2e_ms": p95_e2e_ms,
        "total_extracted_fields": total_extracted_fields,
        "calls_last_7d": calls_last_7d,
        "recent_calls": recent_calls,
    }
