"""Scripted caller personas for the text-mode campaign dry-run.

Personas are positional scripts: reply N answers the agent's Nth utterance.
They deliberately do NOT track conversation state — the point is stressing
the agent's confirmation loop, extraction precision, and wind-down behavior,
not passing a Turing test. ``None`` means the persona has nothing left to
say (runner stops the simulation for that lead).
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

PERSONA_ORDER: tuple[str, ...] = ("cooperative", "terse", "distracted", "refuses", "clueless")

_PERSONA_SCRIPTS: dict[str, list[str]] = {
    "cooperative": [
        "Yes, speaking.",
        "He has had fever since yesterday.",
        "He should be back on Monday.",
        "Yes, I can submit the medical certificate tomorrow.",
        "Thank you, goodbye.",
    ],
    "terse": ["Yes.", "Fever.", "Monday.", "Yes.", "Bye."],
    "distracted": [
        "Yes, speaking — sorry, the TV is loud, one second.",
        "Fever since yesterday. Ask my wife if you need the exact time, she tracks all that.",
        "Monday, I think. Unless the doctor says rest longer, then Tuesday maybe.",
        "Yes, certificate tomorrow. Anyway the traffic today was terrible.",
        "Okay bye now.",
    ],
    "refuses": [
        "I do not want to talk about this, please do not call again.",
        "Please remove our number. Goodbye.",
    ],
    "clueless": [
        "I don't know.",
        "Not sure, you'd have to ask someone else.",
        "I really couldn't say.",
        "No idea. Is there anything else?",
    ],
}


def validate_persona(name: str) -> str:
    """Return the persona name or raise ValueError for unknown names."""
    if name not in _PERSONA_SCRIPTS:
        raise ValueError(f"unknown dry-run persona: {name!r}")
    return name


def persona_reply(
    persona_name: str,
    agent_text: str,
    turn_no: int,
    contact: Mapping[str, Any],
) -> Optional[str]:
    """Next scripted caller line, or None when the persona is done."""
    script = _PERSONA_SCRIPTS[validate_persona(persona_name)]
    if turn_no < 0 or turn_no >= len(script):
        return None
    return script[turn_no]
