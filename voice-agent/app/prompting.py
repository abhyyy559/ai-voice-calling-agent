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
from typing import Any, Mapping

LOW_CONFIDENCE_THRESHOLD: float = 0.6
MAX_ASKS_PER_FIELD: int = 3

DISCLOSURE_HEADER = (
    "MANDATORY DISCLOSURE - your VERY FIRST utterance, spoken word-for-word:"
)
PERSONA_HEADER = "WHO YOU ARE - role and mission:"
CONTEXT_HEADER = "COMPANY KNOWLEDGE - facts you may use; never invent anything beyond this:"
QUESTIONS_HEADER = "YOUR GOALS - information to collect during the call:"
EXTRACTION_HEADER = "RECORDING ANSWERS - extraction discipline:"
ESCALATION_HEADER = "WHEN TO WRAP UP:"


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


def render_system_prompt(config: Mapping[str, Any]) -> str:
    """Render the full agent instructions from an agent-version config."""
    sections: list[str] = []

    # 1. Disclosure FIRST and verbatim.
    disclosure = _disclosure_text(config)
    if disclosure:
        sections.append(f"{DISCLOSURE_HEADER}\n{disclosure}")

    # 2. Role & mission.
    system_prompt = str(config.get("system_prompt") or "").strip()
    role_lines: list[str] = [
        "You are a friendly human-sounding phone agent making a single outbound call.",
        "This is a real-time SPOKEN conversation: the caller hears your words read aloud by a voice engine.",
        "Your job is to have a natural short conversation, understand the caller, and complete the goals below.",
    ]
    if system_prompt:
        role_lines.append(f"Agent-specific role from the creator: {system_prompt}")
    sections.append("\n".join([PERSONA_HEADER] + [f"- {line}" for line in role_lines]))

    # 3. Company context.
    company_context = config.get("company_context")
    if company_context:
        sections.append(
            f"{CONTEXT_HEADER}\n"
            + json.dumps(company_context, indent=2, ensure_ascii=False, default=str)
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

    # 5. Goals (question flow) as a checklist, woven naturally.
    question_flow = config.get("question_flow") or []
    goal_items: list[str] = []
    number = 0
    for item in question_flow:
        text = _question_text(item)
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
