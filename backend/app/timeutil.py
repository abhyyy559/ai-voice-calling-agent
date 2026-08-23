"""Time helpers.

Convention used across the backend: **all datetimes persisted in the database
are timezone-naive UTC**.  ISO-8601 strings received from other services are
converted to naive UTC before storage.  Calling-hours checks convert naive UTC
to the configured local timezone (default Asia/Kolkata).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def utcnow() -> datetime:
    """Current time as timezone-naive UTC (DB convention)."""
    return datetime.now(UTC).replace(tzinfo=None)


def to_naive_utc(value: datetime) -> datetime:
    """Convert an aware datetime to naive UTC; naive values pass through."""
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value


def parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 string into naive UTC. Raises ValueError on bad input."""
    text = value.strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid ISO-8601 timestamp: {value!r}") from exc
    return to_naive_utc(parsed)


def to_aware_utc(value: datetime) -> datetime:
    """Interpret a datetime as UTC (naive values assumed already UTC)."""
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def is_within_calling_hours(
    now_utc: datetime,
    tz_name: str,
    start_hour: int,
    end_hour: int,
) -> bool:
    """True when local wall-clock hour is in [start_hour, end_hour).

    Start inclusive, end exclusive (9, 21 => 09:00:00–20:59:59.999 local).
    """
    local = to_aware_utc(now_utc).astimezone(ZoneInfo(tz_name))
    return start_hour <= local.hour < end_hour


def backoff_from(now_utc: datetime, minutes: int) -> datetime:
    """now + backoff, returned as naive UTC."""
    return to_naive_utc(now_utc) + timedelta(minutes=minutes)
