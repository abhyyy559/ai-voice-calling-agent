"""CALLER CONTEXT section: personalized prompt from packed contact metadata (P0-2).

render_system_prompt(config, contact=...) must render a CALLER CONTEXT block
naming the student/class/absence, instruct the agent to ask for the parent,
and enforce verify-relationship-before-details. Without a contact, the block
must be absent entirely.
"""

from __future__ import annotations

from typing import Any, Dict

from app.prompting import CALLER_CONTEXT_HEADER, render_system_prompt

from test_voice_unit_prompt import BASE_CONFIG

CONTACT: Dict[str, Any] = {
    "student_name": "Aarav",
    "parent_name": "Suresh",
    "class_section": "10-B",
    "absent_date": "2026-08-24",
}


def test_no_contact_means_no_caller_context() -> None:
    rendered = render_system_prompt(BASE_CONFIG)
    assert CALLER_CONTEXT_HEADER not in rendered
    assert "Aarav" not in rendered


def test_contact_renders_caller_context_with_names() -> None:
    rendered = render_system_prompt(BASE_CONFIG, contact=CONTACT)

    assert CALLER_CONTEXT_HEADER in rendered
    assert "Aarav" in rendered
    assert "class 10-B" in rendered
    assert "2026-08-24" in rendered
    assert "Suresh" in rendered


def test_verify_relationship_rule_present() -> None:
    rendered = render_system_prompt(BASE_CONFIG, contact=CONTACT)

    lowered = rendered.lower()
    assert "verify" in lowered and "relationship" in lowered
    # Wrong person -> ask availability and end, never share student details.
    assert "available" in lowered
    assert "end the call" in lowered


def test_generic_custom_fields_are_listed() -> None:
    rendered = render_system_prompt(
        BASE_CONFIG, contact={"roll_number": "42"}
    )

    assert CALLER_CONTEXT_HEADER in rendered
    assert "roll_number" in rendered and "42" in rendered


def test_render_remains_deterministic_with_contact() -> None:
    assert render_system_prompt(BASE_CONFIG, contact=CONTACT) == (
        render_system_prompt(BASE_CONFIG, contact=CONTACT)
    )
