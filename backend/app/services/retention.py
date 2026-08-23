"""Recording/transcript retention job (PRD §8 — automated deletion).

A daily asyncio task deletes transcripts and clears recording URLs on calls
older than RECORDING_RETENTION_DAYS. Also exposed via
``POST /api/admin/retention/run`` for manual triggering.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.models import Call, Transcript
from app.timeutil import utcnow

logger = logging.getLogger(__name__)

RETENTION_INTERVAL_SECONDS = 24 * 60 * 60


def run_retention(
    db: Session,
    settings: Settings,
    now: Optional[datetime] = None,
) -> dict:
    """Delete transcripts and null recording URLs for calls past retention.

    Returns counts for logging / the admin API.
    """
    now = now or utcnow()
    cutoff = now - timedelta(days=settings.recording_retention_days)
    stale_call_ids = list(
        db.scalars(
            select(Call.id).where(
                func.coalesce(Call.ended_at, Call.created_at) <= cutoff,
                (Call.recording_url.is_not(None))
                | Call.id.in_(select(Transcript.call_id).distinct()),
            )
        )
    )

    transcripts_deleted = 0
    recording_urls_cleared = 0
    if stale_call_ids:
        result = db.execute(delete(Transcript).where(Transcript.call_id.in_(stale_call_ids)))
        transcripts_deleted = int(result.rowcount or 0)
        result = db.execute(
            update(Call)
            .where(Call.id.in_(stale_call_ids), Call.recording_url.is_not(None))
            .values(recording_url=None)
        )
        recording_urls_cleared = int(result.rowcount or 0)
        db.commit()

    logger.info(
        "retention: cutoff=%s calls=%d transcripts_deleted=%d recording_urls_cleared=%d",
        cutoff.isoformat(), len(stale_call_ids), transcripts_deleted, recording_urls_cleared,
    )
    return {
        "cutoff": cutoff,
        "calls_older_than_cutoff": len(stale_call_ids),
        "transcripts_deleted": transcripts_deleted,
        "recording_urls_cleared": recording_urls_cleared,
    }


async def retention_loop(settings: Settings, session_factory: sessionmaker[Session]) -> None:
    """Daily background task."""
    while True:
        try:
            await asyncio.to_thread(_run_once, settings, session_factory)
        except asyncio.CancelledError:
            logger.info("retention job stopped")
            raise
        except Exception:  # noqa: BLE001
            logger.exception("retention job failed")
        await asyncio.sleep(RETENTION_INTERVAL_SECONDS)


def _run_once(settings: Settings, session_factory: sessionmaker[Session]) -> None:
    with session_factory() as db:
        run_retention(db, settings)
