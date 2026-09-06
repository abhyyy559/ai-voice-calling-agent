"""Pure system-prompt rendering for the cascaded voice pipeline.

This module is deliberately free of I/O and third-party imports so it can be
unit tested offline. The rendered prompt is structured, in order:

1. Mandatory disclosure script — VERBATIM, always the very first utterance.
2. Role & mission (who the agent is, what this call achieves).
3. Persona / company context.
4. Speaking style — TTS-safe, human, brief.
5. Conversation flow — question flow as a checklist, not a script.
6. Extraction discipline (never-fabricate + immediate tool recording).
7. Escalation policy (low confidence / exhausted asks -> wrap-up + flag).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Mapping, Optional

logger = logging.getLogger("voice_agent.prompting")

LOW_CONFIDENCE_THRESHOLD: float = 0.6
MAX_ASKS_PER_FIELD: int = 3

DISCLOSURE_HEADER = (
    "MANDATORY DISCLOSURE - your VERY FIRST utterance, spoken word-for-word:"
)
PERSONA_HEADER = "WHO YOU ARE - role and mission:"
ROLE_MISSION_HEADER = (
    "ROLE & MISSION - defined by the agent creator (AUTHORITATIVE):"
)
CONTEXT_HEADER = "COMPANY KNOWLEDGE - facts you may use; never invent anything beyond this:"
CALLER_CONTEXT_HEADER = "CALLER CONTEXT - who this specific call is about:"
LANGUAGE_HEADER = "LANGUAGE INSTRUCTION:"
QUESTIONS_HEADER = "YOUR GOALS - information to collect during the call:"
EXTRACTION_HEADER = "RECORDING ANSWERS - extraction discipline:"
ESCALATION_HEADER = "WHEN TO WRAP UP:"

LANGUAGE_NAMES = {"en": "English", "te": "Telugu", "hi": "Hindi"}

#: Bracket placeholder tokens that may appear verbatim in config strings and
#: must never be spoken/shipped. Mapped to real values; empty values are removed.
KNOWN_TOKENS: tuple[str, ...] = (
    "[Institution Name]",
    "[Company Name]",
    "[Student Name]",
    "[Lead Name]",
    "[Parent/Guardian Name]",
    "[Agent Name]",
    "[Expected Return Date]",
)

_BRACKET_ARTIFACT_RE = re.compile(r"\[[^\]]*\]")
_DOUBLE_SPACE_RE = re.compile(r"\s{2,}")

_TOOL_BLOCK_RE = re.compile(
    r"<tool_call>.*?</tool_call>|<function=[^>]*>|<parameter=[^>]*>",
    re.DOTALL | re.IGNORECASE,
)
_TOOL_CALLS_JSON_RE = re.compile(r'"[^"]*tool_calls[^"]*"\s*:\s*\[.*?\]', re.DOTALL)


def scrub_speech_text(text: str) -> str:
    """Remove LLM tool-call markup from text that will be spoken/saved.

    Handles LiveKit-style inline markup (``<tool_call>...``, ``<function=...>``,
    ``<parameter=...>``) and OpenAI-style ``\"tool_calls\": [...]`` JSON that a
    model may emit as inline assistant text. Returns cleaned, stripped text.
    """
    original = str(text or "")
    out = _TOOL_BLOCK_RE.sub(" ", original)
    out = _TOOL_CALLS_JSON_RE.sub(" ", out)
    out = _DOUBLE_SPACE_RE.sub(" ", out).strip()
    if out != original.strip():
        logger.debug("Scrubbed tool-call markup from agent text")
    return out


def apply_token_substitution(
    text: str, tokens: Optional[Mapping[str, str]] = None
) -> str:
    """Replace known bracket tokens with real values; empty -> removed.

    After substitution, any remaining ``[...]`` placeholder is stripped so a
    bare bracket never ships. Returns cleaned text.
    """
    if not text:
        return text
    out = str(text)
    for token, value in (tokens or {}).items():
        out = out.replace(str(token), str(value) if value is not None else "")
    # Safety net: strip any remaining placeholder tokens.
    out = _BRACKET_ARTIFACT_RE.sub("", out)
    return _DOUBLE_SPACE_RE.sub(" ", out).strip()


def _first_name(*candidates: Optional[Mapping[str, Any]]) -> str:
    """First known name found across contact cards (student/name/contact_name...)."""
    for card in candidates:
        if not isinstance(card, Mapping):
            continue
        for key in ("student_name", "name", "contact_name", "full_name", "lead_name"):
            value = str(card.get(key) or "").strip()
            if value:
                return value
    return ""


def build_token_map(
    contact: Optional[Mapping[str, Any]] = None,
    context: Optional[Mapping[str, Any]] = None,
    agent_name: str = "",
) -> dict[str, str]:
    """Resolve known placeholder tokens to real values for this call.

    ``contact`` is the contact card packed in room/token metadata; ``context``
    is the backend's call-context JSON (institution_name + optional contact).
    ``[Expected Return Date]`` has no data source, so it maps to "" (dropped).

    ``agent_name`` fills ``[Agent Name]``; empty falls back to
    "an AI assistant" so disclosures never dangle.
    """
    ctx = context if isinstance(context, Mapping) else {}
    ctx_contact = ctx.get("contact") if isinstance(ctx.get("contact"), Mapping) else {}
    institution = str(ctx.get("institution_name") or "").strip()
    name = _first_name(contact, ctx_contact)
    who = str(agent_name or "").strip() or "an AI assistant"
    return {
        "[Institution Name]": institution,
        "[Company Name]": institution,
        "[Student Name]": name,
        "[Lead Name]": name,
        "[Parent/Guardian Name]": name,
        "[Agent Name]": who,
        "[Expected Return Date]": "",
    }


_CARD_PARENT_KEYS = ("parent_name", "parent", "guardian", "contact_person")
_CARD_SUBJECT_KEYS = ("student_name", "full_name", "contact_name", "lead_name", "candidate_name", "name")


def _card_value(card: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = str(card.get(key) or "").strip()
        if value:
            return value
    return ""


def build_opening_line(
    config: Mapping[str, Any],
    tokens: Optional[Mapping[str, str]] = None,
    contact: Optional[Mapping[str, Any]] = None,
) -> str:
    """Deterministic opening: disclosure + greeting + first question.

    Everything is token-substituted, so no ``[...]`` placeholder can ship.
    Returns "" when there is no disclosure script — the caller then falls
    back to the prompt-driven auto-turn.
    """
    tok = dict(tokens or {})
    disclosure = apply_token_substitution(_disclosure_text(config), tok)
    if not disclosure:
        return ""
    card = contact if isinstance(contact, Mapping) else {}
    parent = _card_value(card, _CARD_PARENT_KEYS)
    subject = _card_value(card, _CARD_SUBJECT_KEYS)
    institution = tok.get("[Institution Name]", "") or tok.get("[Company Name]", "")
    who = tok.get("[Agent Name]", "") or "an AI assistant"
    # Short standalone sentences (not one long clause): the TTS engine
    # synthesizes sentence by sentence, so names get clean prosodic breaks
    # and are pronounced far more clearly than mid-sentence.
    if parent and subject and parent != subject:
        if institution:
            greet = (
                f"Hello {parent}. "
                f"This is {who} calling from {institution}. "
                f"I'm calling about {subject}."
            )
        else:
            greet = f"Hello {parent}. This is {who} calling about {subject}."
    elif subject:
        if institution:
            greet = f"Hello {subject}. This is {who} calling from {institution}."
        else:
            greet = f"Hello {subject}. This is {who} calling."
    elif institution:
        greet = f"Hello. This is {who} calling from {institution}."
    else:
        greet = "Hello."
    first_question = ""
    flow = config.get("question_flow") if isinstance(config, Mapping) else []
    if isinstance(flow, list):
        for item in flow:
            text_value = apply_token_substitution(_question_text(item), tok)
            if text_value:
                first_question = text_value
                break
    opening = f"{disclosure} {greet}"
    if first_question:
        opening += f" {first_question}"
    return scrub_speech_text(opening)


def _disclosure_text(config: Mapping[str, Any]) -> str:
    """Disclosure script, accepting both the platform key and the legacy one."""
    raw = config.get("disclosure_script")
    if not raw:
        raw = config.get("mandatory_disclosure")
    return str(raw or "").strip()


def _question_text(item: Any) -> str:
    """Question text from either a plain string or a flow-step object."""
    if isinstance(item, Mapping):
        text = item.get("question") or item.get("text") or ""
        return str(text).strip()
    return str(item or "").strip()


def render_caller_context(contact: Mapping[str, Any]) -> str:
    """CALLER CONTEXT block (P0-2) from the contact card packed in room/token
    metadata. Names the person the call is about, tells the agent who to ask
    for, and enforces verify-relationship-before-details."""
    fields: dict[str, str] = {}
    if isinstance(contact, Mapping):
        for key, value in contact.items():
            name = str(key).strip()
            if not name or isinstance(value, (dict, list)):
                continue
            text = str(value).strip()
            if text:
                fields[name] = text

    lines = [CALLER_CONTEXT_HEADER]
    about: list[str] = []
    student = fields.get("student_name") or ""
    parent = fields.get("parent_name") or ""
    # Domain-generic subject keys: whichever of these is present marks the
    # person the call is about (lead verification, surveys, appointments, ...).
    subject = (
        fields.get("full_name")
        or fields.get("contact_name")
        or fields.get("lead_name")
        or fields.get("candidate_name")
        or fields.get("name")
        or ""
    )
    if student:
        about.append(f"the student {student}")
    if fields.get("class_section"):
        about.append(f"class {fields['class_section']}")
    if fields.get("absent_date"):
        about.append(f"absent on {fields['absent_date']}")
    if subject:
        about.append(f"the person {subject}")
    if about:
        lines.append("- You are calling about " + ", ".join(about) + ".")
    else:
        lines.append(
            "- Details of the person this call is about: "
            + json.dumps(fields, ensure_ascii=False, sort_keys=True)
        )

    # Any other custom fields still get through - the creator's contact card
    # may carry domain-specific facts (city, form_source, account_id, ...) the
    # agent should be able to use without the platform knowing their meaning.
    woven = {
        "student_name",
        "class_section",
        "absent_date",
        "full_name",
        "contact_name",
        "lead_name",
        "candidate_name",
        "name",
        "parent_name",
        "contact_person",
    }
    extras = {k: v for k, v in fields.items() if k not in woven}
    if extras and about:
        lines.append(
            "- Other details you may use if relevant: "
            + json.dumps(extras, ensure_ascii=False, sort_keys=True)
        )

    # Who to ask for: an explicit parent (school flows) or contact person wins;
    # otherwise the subject themself (e.g. a lead answering their own phone).
    verify_target = (
        parent
        or fields.get("contact_person")
        or (subject and f"{subject} (the person you are calling)")
        or "the person you are calling"
    )
    if parent:
        lines.append(f"- Ask to speak with {parent} (the parent/guardian).")
    elif subject:
        lines.append(f"- Ask for {subject} when the call is answered.")

    # Say the names out loud. The #1 complaint from real test calls is a generic
    # opening ("may I speak with the parent or guardian...") when the caller's
    # name is sitting right there in the contact card. Collect every name we
    # know and instruct the agent to use them in the greeting. Prefer the plain
    # name over the label so the greeting sounds natural ("Suresh", not
    # "Suresh (the parent/guardian)").
    known_names: list[str] = []
    for key in ("parent_name", "student_name", "full_name", "lead_name",
                "contact_name", "candidate_name", "name", "contact_person"):
        val = str(fields.get(key) or "").strip()
        if val and val not in known_names:
            known_names.append(val)
    if known_names:
        examples = []
        if parent and student:
            examples.append(f"Good morning, am I speaking with {parent}, parent or guardian of {student}?")
        elif parent:
            examples.append(f"Good morning, am I speaking with {parent}?")
        elif subject:
            examples.append(f"Good morning, am I speaking with {subject}?")
        named = ", ".join(known_names)
        lines.append(
            "- SAY THE NAMES OUT LOUD: greet the person using their name. "
            f"Known name(s) on this record: {named}."
        )
        if examples:
            lines.append(
                "- Example openings to model: "
                + " | ".join(examples)
            )
        if parent or student:
            lines.append(
                "- NEVER say 'the person we are calling about' or 'the parent or "
                "guardian of the student' when you have a real name on this record. "
                "Names make the call feel human; vagueness is how callers sense a bot."
            )
        else:
            lines.append(
                "- NEVER say 'the person we are calling about' when you have a real "
                "name on this record. Names make the call feel human; vagueness is "
                "how callers sense a bot."
            )
    lines.extend(
        [
            (
                "- VERIFY RELATIONSHIP BEFORE DETAILS: confirm you are speaking with "
                f"{verify_target} before discussing any details about the person "
                "this call is about."
            ),
            (
                "- If the person who answered is NOT "
                f"{verify_target}, do NOT share any details: ask when they will be "
                "available, thank them politely, say goodbye, and end the call."
            ),
        ]
    )
    return "\n".join(lines)


def render_system_prompt(
    config: Mapping[str, Any],
    contact: Optional[Mapping[str, Any]] = None,
    tokens: Optional[Mapping[str, str]] = None,
) -> str:
    """Render the full agent instructions from an agent-version config.

    ``contact`` (optional, P0-2) is the flat custom-field card packed into the
    room/token metadata; when present a CALLER CONTEXT section personalizes
    the prompt and adds the parent-verification rule.

    ``tokens`` (optional, C) is a resolved token map (``[Institution Name]`` ->
    value) applied to the disclosure, system_prompt, and question_flow text so
    literal ``[Institution Name]`` placeholders never ship. Empty values are
    removed.
    """
    sections: list[str] = []

    # 1. Disclosure FIRST and verbatim.
    disclosure = apply_token_substitution(_disclosure_text(config), tokens)
    if disclosure:
        sections.append(f"{DISCLOSURE_HEADER}\n{disclosure}")

    # 2. Role & mission — platform baseline, then the creator's definition.
    system_prompt = apply_token_substitution(
        str(config.get("system_prompt") or "").strip(), tokens
    )
    role_lines: list[str] = [
        "You are a human-sounding phone agent making a single outbound call.",
        "This is a real-time SPOKEN conversation: the caller hears your words read aloud by a voice engine.",
        "Your job is to have a natural short conversation, understand the caller, and complete the goals below.",
    ]
    sections.append("\n".join([PERSONA_HEADER] + [f"- {line}" for line in role_lines]))

    # 2b. Creator's role definition - the PRIMARY identity instruction.
    # Rendered verbatim as its own block (NOT a bullet inside the generic
    # persona) so a well-written prompt fully defines who the agent is, why it
    # is calling, and how it communicates. The platform guardrails further
    # below still apply; this block only wins on role/behavior specifics.
    if system_prompt:
        sections.append(
            f"{ROLE_MISSION_HEADER}\n"
            f"{system_prompt}\n"
            "This role definition is authoritative for WHO you are and HOW you "
            "behave in this call: where it differs from generic examples in "
            "these instructions, follow the role definition."
        )

    # 3. Company context.
    company_context = config.get("company_context")
    if company_context:
        sections.append(
            f"{CONTEXT_HEADER}\n"
            + json.dumps(company_context, indent=2, ensure_ascii=False, default=str)
        )

    # 3b. Caller context (P0-2) — who this specific call is about.
    if contact:
        sections.append(render_caller_context(contact))

    # 3c. Language instruction — tells the LLM which language to respond in.
    voice_settings = config.get("voice_settings") or {}
    if isinstance(voice_settings, Mapping):
        lang_code = str(voice_settings.get("language") or "en").lower()
    else:
        lang_code = "en"
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
    if lang_code != "en":
        sections.append(
            f"{LANGUAGE_HEADER}\n"
            f"- The caller speaks {lang_name}. Respond entirely in {lang_name}.\n"
            "- If the caller code-switches (mixes languages mid-sentence), "
            f"follow their lead: reply in {lang_name} but accept words from any language.\n"
            "- Keep the same extraction field names in English when calling tools."
        )
    else:
        sections.append(
            f"{LANGUAGE_HEADER}\n"
            "- The primary language for this call is English.\n"
            "- If the caller speaks another language, try to follow their lead "
            "but default to English."
        )

    # 4. Speaking style — this is what makes it sound human instead of IVR-like.
    sections.append(
        "HOW TO SPEAK (critical):\n"
        "- Keep every reply SHORT: usually 1-2 sentences, never more than 3.\n"
        "- Plain conversational words only. This text is converted to speech:\n"
        "  NO markdown, NO asterisks, NO bullet lists, NO numbering symbols,\n"
        "  NO emoji, NO newlines inside a reply. Sentences and punctuation only.\n"
        "- Listen first, then respond to what the caller ACTUALLY said before moving on.\n"
        "  Reflect it back briefly and warmly, e.g. 'Sorry to hear you've been unwell.'\n"
        "- Ask ONE thing per turn. After the caller answers, acknowledge their answer,\n"
        "  then guide the conversation toward the next goal naturally - do not read\n"
        "  questions like a robot reading a script.\n"
        "- If the caller volunteers information early, accept it happily and skip that goal later.\n"
        "- Never repeat a question they already answered. Never talk over long pauses with new content;\n"
        "  a simple 'Are you still there?' is enough after silence.\n"
        "- Stay polite and calm even if the caller is upset or wants to hang up."
    )

    # 4b. Guardrails — on-topic only, privacy, brevity, human handoff.
    sections.append(
        "HARD RULES (non-negotiable):\n"
        "- STAY ON TOPIC: you only discuss the purpose of this call defined above. "
        "If asked anything unrelated (news, general knowledge, personal opinions), "
        "politely decline: 'I can only help with <purpose> today' and steer back.\n"
        "- PRIVACY: never share any information about any OTHER person, caller, or record. "
        "Only discuss the specific person this call is about.\n"
        "- VERIFY BEFORE SHARING: if the relationship of the person answering is unclear "
        "for a sensitive topic, confirm who you are speaking with first.\n"
        "- BE BRIEF: complete the goals and end the call promptly - every extra minute costs money.\n"
        "- HUMAN HANDOFF: if the caller repeatedly drifts off-topic, demands things beyond "
        "your scope, or needs more help than this call provides, say you will arrange a "
        "human representative to follow up, then call `end_call` with that summary."
    )

    # 5. Goals (question flow) as a checklist, woven naturally.
    question_flow = config.get("question_flow") or []
    goal_items: list[str] = []
    number = 0
    for item in question_flow:
        text = apply_token_substitution(_question_text(item), tokens)
        if not text:
            continue
        number += 1
        goal_items.append(f"{number}. {text}")
    if goal_items:
        sections.append(
            f"{QUESTIONS_HEADER}\n"
            + "\n".join(goal_items)
            + "\nCover ALL of these by the end of the call, in whatever order the "
              "conversation makes natural. You do not need to use the exact wording - "
              "weave each into the conversation naturally."
        )
    else:
        sections.append(
            f"{QUESTIONS_HEADER}\n- No fixed goals were configured; have a natural "
            "conversation about why you are calling."
        )

    # 6. Extraction rules with never-fabricate + immediate recording.
    extraction_schema = config.get("extraction_schema") or {}
    extraction_lines: list[str] = [
        EXTRACTION_HEADER,
        "- The moment the caller states something that answers any goal above, IMMEDIATELY "
        "call `record_extracted_field(field_name, value, confidence)` in that same turn. "
        "Do not wait until the end of the call.",
        "- Use the EXACT field names listed below. Value must be quoted as the caller said it.",
        "- Invoke `record_extracted_field` through your real FUNCTION-CALLING mechanism. "
        "NEVER write tool-call markup into your spoken text - never output `<tool_call>`, "
        "`<function=...>`, `<parameter=...>`, or `tool_calls` JSON. If you don't yet have a "
        "real value, keep asking a short clarifying question - do not invent one or fake a call.",
        "- Give an honest confidence between 0.0 and 1.0. If you clearly heard it, say 0.9. "
        "If you are guessing, do NOT record - ask a short clarifying question instead.",
        "- NEVER fabricate or guess a value. Uncertain means ask again, differently.",
        (
            f"- If your confidence for a value stays below {LOW_CONFIDENCE_THRESHOLD}, treat that field as NOT captured: "
            "wrap up gracefully and clearly flag it when you call `end_call`."
        ),
        (
            f"- If a required field is still unfilled after asking up to {MAX_ASKS_PER_FIELD} times, stop asking about it, wrap up gracefully, "
            "and flag it in your `end_call` summary."
        ),
        "- To finish the call, call `end_call(summary)` with a factual summary of captured fields, flagged/unfilled fields, and the caller's mood.",
    ]
    schema_lines: list[str] = ["Fields to capture:"]
    if isinstance(extraction_schema, Mapping):
        for field_name, spec in extraction_schema.items():
            if isinstance(spec, Mapping):
                description = str(
                    spec.get("description") or spec.get("type") or ""
                ).strip()
                validation = str(spec.get("validation") or "").strip().lower()
                marker = " [REQUIRED]" if validation == "required" else ""
                schema_lines.append(f"- `{field_name}`{marker}: {description}".rstrip(": "))
            else:
                schema_lines.append(f"- `{field_name}`: {spec}")
    extraction_lines.extend(schema_lines)
    sections.append("\n".join(extraction_lines))

    # 7. Optional extra escalation rules supplied by the agent author.
    escalation_rules = config.get("escalation_rules") or []
    rule_items: list[str] = []
    if isinstance(escalation_rules, Mapping):
        rule_items = [
            f"{key}: {value}" for key, value in escalation_rules.items()
        ]
    elif isinstance(escalation_rules, (list, tuple)):
        rule_items = [str(rule) for rule in escalation_rules if str(rule).strip()]
    if rule_items:
        wrapped = "\n".join(f"- {rule}" for rule in rule_items)
        sections.append(f"{ESCALATION_HEADER}\n{wrapped}")

    return "\n\n".join(sections)
