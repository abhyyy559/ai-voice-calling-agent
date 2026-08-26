"""Per-language voice-mapping schema validation."""
import pytest

from domain_config_schema import validate_agent_version_payload


def _payload(voice):
    return {
        "system_prompt": "You are an AI assistant helping parents.",
        "question_flow": [{"step": 1, "question": "Why is your child absent?"}],
        "extraction_schema": {},
        "disclosure_script": "Hello, I am an AI assistant calling.",
        "escalation_rules": ["caller expresses anger"],
        "voice_settings": voice,
    }


def test_defaults_when_absent():
    out = validate_agent_version_payload(_payload({}))
    assert out.voice_settings.language == "en"
    assert out.voice_settings.voices_by_language == {}


def test_multilingual_map_accepted_and_normalized():
    out = validate_agent_version_payload(
        _payload({"language": "EN", "voices_by_language": {"TE": "bulbul-te", "en": "c-en"}})
    )
    assert out.voice_settings.language == "en"
    assert out.voice_settings.voices_by_language == {"te": "bulbul-te", "en": "c-en"}


@pytest.mark.parametrize("bad", [{"language": "fr"}, {"voices_by_language": {"fr": "x"}}])
def test_unsupported_language_rejected(bad):
    with pytest.raises(Exception):
        validate_agent_version_payload(_payload(bad))


def test_unknown_keys_pass_through():
    out = validate_agent_version_payload(_payload({"custom_vendor_flag": True}))
    assert out.voice_settings.custom_vendor_flag is True
