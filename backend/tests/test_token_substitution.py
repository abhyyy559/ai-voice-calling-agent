"""Bracket-token substitution ported from voice-agent/app/prompting.py."""
from __future__ import annotations

from app.services.token_substitution import (
    KNOWN_TOKENS,
    apply_token_substitution,
    build_token_map,
)


def test_known_tokens_cover_lead_gen_aliases() -> None:
    assert set(KNOWN_TOKENS) >= {
        "[Institution Name]",
        "[Company Name]",
        "[Student Name]",
        "[Lead Name]",
        "[Parent/Guardian Name]",
        "[Agent Name]",
        "[Expected Return Date]",
    }


def test_build_token_map_resolves_names_and_institution() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"}
    tokens = build_token_map(contact, institution="Demo School")
    assert tokens["[Student Name]"] == "Aarav Kumar"
    assert tokens["[Parent/Guardian Name]"] == "Suresh Kumar"
    assert tokens["[Institution Name]"] == "Demo School"
    assert tokens["[Company Name]"] == "Demo School"


def test_build_token_map_lead_style_contact() -> None:
    tokens = build_token_map({"lead_name": "Riya", "city": "Hyderabad"}, institution="Acme Realty")
    assert tokens["[Lead Name]"] == "Riya"
    assert tokens["[Student Name]"] == "Riya"


def test_build_token_map_agent_name_defaults_to_assistant() -> None:
    assert build_token_map({})["[Agent Name]"] == "an AI assistant"
    assert build_token_map({}, agent_name="Priya")["[Agent Name]"] == "Priya"


def test_apply_token_substitution_replaces_and_drops_empties() -> None:
    tokens = build_token_map({"student_name": "Aarav"}, institution="")
    out = apply_token_substitution(
        "Hello [Parent/Guardian Name], calling from [Institution Name] about [Student Name].",
        tokens,
    )
    assert "[Parent/Guardian Name]" not in out
    assert "[Institution Name]" not in out
    assert "Aarav" in out
    assert "  " not in out


def test_apply_token_substitution_strips_unknown_brackets() -> None:
    out = apply_token_substitution("See [Something Else] today.", {})
    assert "[" not in out and "]" not in out
    assert out == "See today."


def test_apply_token_substitution_falsy_passthrough() -> None:
    assert apply_token_substitution("", {}) == ""
