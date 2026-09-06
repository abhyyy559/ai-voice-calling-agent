"""Generic caller context + token substitution in the text-mode prompt."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from app.routers.playground import _render_caller_context, _render_text_system_prompt


def _config(**overrides: Any) -> Any:
    base: dict[str, Any] = {
        "disclosure_script": "Hi, this is [Agent Name] calling from [Institution Name].",
        "system_prompt": "You call about [Student Name].",
        "company_context": {},
        "question_flow": [{"step": 1, "question": "Why was [Student Name] absent?"}],
        "extraction_schema": {},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_absent_student_card_names_and_institution() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar", "class_section": "10-A"}
    prompt = _render_text_system_prompt(_config(), contact=contact, institution="Demo School")
    assert "Aarav Kumar" in prompt
    assert "Suresh Kumar" in prompt
    assert "Demo School" in prompt
    assert "[Student Name]" not in prompt
    assert "[Institution Name]" not in prompt
    assert "Why was Aarav Kumar absent?" in prompt


def test_lead_style_card_generic_phrasing() -> None:
    contact = {"lead_name": "Riya", "city": "Hyderabad"}
    block = _render_caller_context(contact, "Acme Realty")
    assert "Riya" in block
    assert "Hyderabad" in block
    assert "the person Riya" in block
    assert "absent" not in block.lower()
    assert "class_section" not in block


def test_empty_contact_guards_against_invented_names() -> None:
    block = _render_caller_context({}, "")
    assert "NEVER invent or guess any name" in block
    prompt = _render_text_system_prompt(_config(), contact=None, institution="")
    assert "CALLER CONTEXT" in prompt
    assert "NEVER invent or guess any name" in prompt


def test_empty_institution_drops_cleanly() -> None:
    prompt = _render_text_system_prompt(_config(), contact={"student_name": "Aarav"}, institution="")
    assert "Aarav" in prompt
    assert "[Institution Name]" not in prompt
    # Scoped: the static HOW-TO-REPLY block intentionally uses two-space
    # indentation, so the no-gap check applies to substituted text only.
    disclosure_line = next(l for l in prompt.splitlines() if "AI assistant calling from" in l)
    assert "  " not in disclosure_line
