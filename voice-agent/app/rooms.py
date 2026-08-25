"""Which LiveKit rooms this worker serves. Kept free of livekit imports."""
from __future__ import annotations

HANDLED_PREFIXES = ("playground-", "phone-")


def is_handled_room(name: str) -> bool:
    """True when a room should get the conversational agent."""
    clean = (name or "").strip()
    return any(clean.startswith(p) and len(clean) > len(p) for p in HANDLED_PREFIXES)
