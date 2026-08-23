"""Offline tests for app.prompting.render_system_prompt."""

from __future__ import annotations

from typing import Any, Dict

from app.prompting import (
    DISCLOSURE_HEADER,
    EXTRACTION_HEADER,
    PERSONA_HEADER,
    QUESTIONS_HEADER,
    render_system_prompt,
)

BASE_CONFIG: Dict[str, Any] = {
    "disclosure_script": (
        "Hello, I am calling from Acme Academy. I am an AI voice assistant. "
        "This call is recorded for quality and verification purposes."
    ),
    "system_prompt": (
        "You are an AI voice assistant representing Acme Academy. Your role is "
        "to contact parents or guardians of absent students."
    ),
    "company_context": {"company_name": "Acme Academy", "timezone": "Asia/Kolkata"},
    "question_flow": [
        {"step": 1, "question": "Could you share the reason for the absence?"},
        {"step": 2, "question": "Do you expect the student to return tomorrow?"},
        {"step": 3, "question": "Is the absence due to a medical reason?"},
    ],
    "extraction_schema": {
        "reason_for_absence": {
            "type": "string",
            "description": "Reason provided for the absence.",
            "validation": "required",
            "confidence_threshold": 0.8,
        },
        "is_sick_leave": {"type": "boolean", "description": "Illness-related.", "validation": "optional"},
    },
}


def test_disclosure_is_first_block() -> None:
    rendered = render_system_prompt(BASE_CONFIG)

    assert rendered.lstrip().startswith(DISCLOSURE_HEADER.split(" - ")[0])
    disclosure_text = BASE_CONFIG["disclosure_script"]
    assert rendered.index(disclosure_text) < rendered.index(PERSONA_HEADER)
    assert rendered.index(disclosure_text) < rendered.index(QUESTIONS_HEADER)
    assert rendered.index(disclosure_text) < rendered.index(EXTRACTION_HEADER)


def test_questions_are_numbered_in_order() -> None:
    rendered = render_system_prompt(BASE_CONFIG)

    questions_header_at = rendered.index(QUESTIONS_HEADER)
    extraction_at = rendered.index(EXTRACTION_HEADER)
    flow_block = rendered[questions_header_at:extraction_at]
    assert "1. Could you share the reason for the absence?" in flow_block
    assert "2. Do you expect the student to return tomorrow?" in flow_block
    assert "3. Is the absence due to a medical reason?" in flow_block
    # Order must be ascending.
    assert flow_block.index("1. ") < flow_block.index("2. ") < flow_block.index("3. ")
    # The provided step numbers are ignored; numbering is positional 1..n.
    assert "step" not in flow_block


def test_escalation_and_never_fabricate_text_present() -> None:
    rendered = render_system_prompt(BASE_CONFIG)
    lowered = rendered.lower()

    assert "never fabricate" in lowered
    assert "0.6" in rendered  # low-confidence escalation threshold
    assert "3 times" in lowered or "up to 3" in lowered  # max asks
    assert "flag" in lowered  # flagged wrap-up requirement


def test_required_fields_marked_in_schema_block() -> None:
    rendered = render_system_prompt(BASE_CONFIG)
    schema_block = rendered[rendered.index(EXTRACTION_HEADER):]

    assert "`reason_for_absence` [REQUIRED]" in schema_block
    assert "`is_sick_leave`" in schema_block
    assert "[REQUIRED]" not in schema_block.split("`is_sick_leave`")[1].split("\n")[0]


def test_legacy_mandatory_disclosure_key_supported() -> None:
    legacy: Dict[str, Any] = dict(BASE_CONFIG)
    del legacy["disclosure_script"]
    legacy["mandatory_disclosure"] = "Legacy disclosure sentence."

    rendered = render_system_prompt(legacy)

    assert rendered.lstrip().startswith(
        DISCLOSURE_HEADER.split(" - ")[0]
    ), "disclosure block must still come first"
    assert rendered.index("Legacy disclosure sentence.") < rendered.index(PERSONA_HEADER)


def test_empty_question_flow_renders_without_crash() -> None:
    minimal = {"disclosure_script": "Hi.", "question_flow": []}
    rendered = render_system_prompt(minimal)
    assert "Hi." in rendered
