# Task Brief: per-language voice-mapping schema (EchoSarathi §2.4 step 3 groundwork)

**Files:**
- Modify: `backend/domain_config_schema.py`
- Modify: `voice-agent/app/pipeline.py` (ONLY `_voice_overrides` + `build_providers` signature usage)
- Modify: `domain-configs/absent-student.json` (add example mapping)
- Tests: `backend/tests/test_voice_schema.py` (new), extend `backend/tests/test_config_validation.py` if it exists and fits

## Goal

Agents can declare a primary `language` plus optional `voices_by_language` map so the
TTS layer can later pick the right voice per response language. THIS TASK = schema +
plumbing only; runtime mid-call switching is a separate task.

## Exact changes

### 1. domain_config_schema.py

Add after `EscalationRule`:

```python
class VoiceLanguageEntry(BaseModel):
    """One language -> voice-id binding inside voice_settings.voices_by_language."""
    model_config = ConfigDict(str_strip_whitespace=True)

    voice_id: str = Field(min_length=1)


ALLOWED_LANGUAGES = frozenset({"en", "te", "hi"})


class VoiceSettings(BaseModel):
    """Structured view of voice_settings; unknown keys pass through untouched."""
    model_config = ConfigDict(extra="allow", str_strip_whitespace=True)

    language: str = Field(default="en")
    tts_voice_id: str = Field(default="")
    llm_model: str = Field(default="")
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0)
    stt_language: str = Field(default="en")
    voices_by_language: Dict[str, str] = Field(default_factory=dict)

    @field_validator("language", "stt_language")
    @classmethod
    def _known_language(cls, v: str) -> str:
        v = v.lower()
        if v not in ALLOWED_LANGUAGES:
            raise ValueError(f"unsupported language {v!r}; allowed: {sorted(ALLOWED_LANGUAGES)}")
        return v

    @field_validator("voices_by_language")
    @classmethod
    def _languages_known(cls, v: Dict[str, str]) -> Dict[str, str]:
        bad = [k.lower() for k in v if k.lower() not in ALLOWED_LANGUAGES]
        if bad:
            raise ValueError(f"unsupported languages in voices_by_language: {bad}")
        return {k.lower(): val.strip() for k, val in v.items() if val.strip()}
```

Wire into `AgentVersionPayload`: change field
`voice_settings: Dict[str, Any] = Field(default_factory=dict)` to
`voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)`.
Check every consumer of `payload.voice_settings` still works — it now yields a
VoiceSettings model; where code treated it as dict, use
`payload.voice_settings.model_dump(exclude_none=True)` or attribute access.
Grep: seed_demo.py `_version_payload_from_config`, routers/agents.py,
services/calls_service.py, anywhere `.voice_settings`.

Import `ConfigDict`, `field_validator` from pydantic if not already imported.

### 2. voice-agent/app/pipeline.py

Replace `_voice_overrides`:

```python
def _voice_overrides(voice_settings):
    """(llm_model, tts_voice_id, voices_by_language, language) from saved settings."""
    vs = voice_settings or {}
    get = vs.get if isinstance(vs, Mapping) else (lambda k, d=None: getattr(vs, k, d))
    llm_model = str(get("llm_model", "") or "").strip()
    tts_voice = str(get("tts_voice_id", "") or "").strip()
    vbl = dict(get("voices_by_language", {}) or {})
    lang = str(get("language", "en") or "en").lower()
    return llm_model, tts_voice, vbl, lang
```

In `build_providers`: unpack 4 values; choose
`tts_kwargs["voice"] = vbl.get(lang) or tts_voice_override` (explicit per-language
mapping wins over legacy single override). Keep everything else identical.

### 3. domain-configs/absent-student.json

Inside the top-level object add (illustrative; keeps current English behavior):

```json
 "voice_settings": {"language": "en",
  "voices_by_language": {"en": "", "te": ""}}
```

(empty ids = platform default voice; real Bulbul/Cartesia ids land in Phase B)

## Tests — create backend/tests/test_voice_schema.py

```python
"""Per-language voice-mapping schema validation."""
import pytest

from domain_config_schema import validate_agent_version_payload


def _payload(voice):
    return {
        "system_prompt": "p",
        "question_flow": [{"question": "q"}],
        "extraction_schema": {},
        "disclosure_script": "Hello.",
        "escalation_rules": [],
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
```

## Verification

1. New tests green; FULL backend suite green from backend/: `.venv\Scripts\python.exe -m pytest -q` (baseline 100)
2. Seed script still runs: from backend, `.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'..'); import scripts.seed_demo as s; print('ok')"` (import-level only)
3. Report exact consumer files you had to adapt.

## Constraints

PowerShell 5.1 · NO git · touch ONLY listed files (+ minimal consumer adaptations REQUIRED by the model change, each reported).
