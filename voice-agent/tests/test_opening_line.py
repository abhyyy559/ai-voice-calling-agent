"""Deterministic protected opening line: disclosure + greeting + first question."""
from app.prompting import build_opening_line, build_token_map

CONFIG = {
    "disclosure_script": "Hi, this is [Agent Name] calling from [Company Name].",
    "question_flow": [{"question": "Why was [Student Name] absent?"}],
}


def _tokens(contact, institution="Demo School"):
    return build_token_map(contact=contact, context={"institution_name": institution})


def test_opening_line_school_card() -> None:
    contact = {"student_name": "Aarav Kumar", "parent_name": "Suresh Kumar"}
    out = build_opening_line(CONFIG, _tokens(contact), contact)
    assert out.startswith("Hi, this is an AI assistant calling from Demo School.")
    assert "Suresh Kumar" in out
    assert "Aarav Kumar" in out
    assert "Why was Aarav Kumar absent?" in out
    assert "[" not in out and "]" not in out


def test_opening_line_lead_card() -> None:
    contact = {"lead_name": "Riya"}
    out = build_opening_line(CONFIG, _tokens(contact, "Acme Realty"), contact)
    assert "Riya" in out and "Acme Realty" in out
    assert "[" not in out and "]" not in out


def test_opening_line_no_names_no_invention() -> None:
    out = build_opening_line(CONFIG, _tokens({}), {})
    assert "Hello" in out
    assert "[" not in out and "]" not in out


def test_opening_line_empty_without_disclosure() -> None:
    assert build_opening_line({"question_flow": []}, {}, {}) == ""
