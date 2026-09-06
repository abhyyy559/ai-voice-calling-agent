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



# ---------------------------------------------------------------------------
# Domain-generic caller context: lead-verification style contact card.
# Uses a lead-verification agent config (not the school BASE_CONFIG) so the
# assertions prove the platform itself is domain-neutral.
# ---------------------------------------------------------------------------
LEAD_CONFIG: Dict[str, Any] = {
    "disclosure_script": (
        "Hello, I am calling from EduPro Learning. I am an AI voice assistant. "
        "This call is recorded for quality and verification purposes."
    ),
    "system_prompt": (
        "You are a lead verification agent for EduPro Learning. You call people "
        "who filled the demo-class form on our website."
    ),
    "question_flow": [
        {"step": 1, "question": "Are you still interested in the demo class?"},
        {"step": 2, "question": "Which city are you in currently?"},
    ],
    "extraction_schema": {
        "still_interested": {
            "type": "boolean",
            "description": "Whether the lead is still interested.",
            "validation": "required",
            "confidence_threshold": 0.8,
        },
    },
}

LEAD_CONTACT: Dict[str, Any] = {
    "full_name": "Priya Sharma",
    "city": "Hyderabad",
    "form_source": "website-demo-form",
}


def test_lead_contact_names_subject_and_no_parent_language() -> None:
    rendered = render_system_prompt(LEAD_CONFIG, contact=LEAD_CONTACT)

    assert CALLER_CONTEXT_HEADER in rendered
    assert "Priya Sharma" in rendered
    assert "Hyderabad" in rendered
    # No school-domain language when the card has no student/parent fields.
    lowered = rendered.lower()
    assert "parent/guardian" not in lowered
    assert "student" not in lowered
    # School-specific forbidden phrase is NOT present for a lead card.
    assert "parent or guardian of the student" not in lowered


def test_lead_contact_verify_target_is_the_subject() -> None:
    rendered = render_system_prompt(LEAD_CONFIG, contact=LEAD_CONTACT)

    # The lead answers their own phone: verify against them, not a guardian.
    assert "Priya Sharma (the person you are calling)" in rendered


def test_lead_contact_verify_target_is_the_subject() -> None:
    rendered = render_system_prompt(LEAD_CONFIG, contact=LEAD_CONTACT)

    # The lead answers their own phone: verify against them, not a guardian.
    assert "Priya Sharma (the person you are calling)" in rendered


def test_lead_agent_renders_creator_role_definition() -> None:
    rendered = render_system_prompt(LEAD_CONFIG, contact=LEAD_CONTACT)

    # The creator's prompt drives the role, verbatim.
    assert "lead verification agent for EduPro Learning" in rendered
    assert "ROLE & MISSION - defined by the agent creator" in rendered


def test_contact_person_key_overrides_subject_as_verify_target() -> None:
    rendered = render_system_prompt(
        BASE_CONFIG,
        contact={"full_name": "Priya Sharma", "contact_person": "Rahul (assistant)"},
    )

    assert "Rahul (assistant)" in rendered


def test_says_names_out_loud_instead_of_vague() -> None:
    rendered = render_system_prompt(BASE_CONFIG, contact=CONTACT)

    # The agent must use the REAL names in its greeting, never generic.
    assert "SAY THE NAMES OUT LOUD" in rendered
    assert "Suresh" in rendered
    assert "Aarav" in rendered
    # The school-flow forbidden-phrase rule is present (names exist).
    assert "parent or guardian of the student" in rendered
    # Example opening puts the names in the mouth.
    assert "parent or guardian of Aarav" in rendered


def test_say_names_uses_full_name_for_lead() -> None:
    rendered = render_system_prompt(LEAD_CONFIG, contact=LEAD_CONTACT)

    assert "Good morning, am I speaking with Priya Sharma?" in rendered
    assert "SAY THE NAMES OUT LOUD" in rendered

