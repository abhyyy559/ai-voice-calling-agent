"""Dry-run personas: scripted callers behind the text-mode campaign dry-run."""
from __future__ import annotations

import pytest

from app.services.dry_run import PERSONA_ORDER, persona_reply, validate_persona


def test_persona_order_covers_five_behaviors() -> None:
    assert set(PERSONA_ORDER) == {"cooperative", "terse", "distracted", "refuses", "clueless"}


def test_cooperative_answers_from_script() -> None:
    reply = persona_reply("cooperative", "Why was Aarav absent?", 1, {"student_name": "Aarav"})
    assert reply
    assert "Aarav" not in reply  # caller answers; never parrots the agent's question


def test_refuses_ends_early() -> None:
    first = persona_reply("refuses", "Hello?", 0, {})
    assert first is not None and "not" in first.lower()
    assert persona_reply("refuses", "Why?", 5, {}) is None


def test_terse_is_short() -> None:
    reply = persona_reply("terse", "Why was Aarav absent?", 1, {})
    assert reply is not None and len(reply.split()) <= 3


def test_unknown_persona_rejected() -> None:
    with pytest.raises(ValueError):
        validate_persona("sarcastic")
