"""Pure system-prompt rendering for the cascaded voice pipeline.

This module is deliberately free of I/O and third-party imports so it can be
unit tested offline. The rendered prompt is structured, in order:

1. Mandatory disclosure script — VERBATIM, always the very first block.
2. Persona / company context.
3. Numbered question flow.
4. Extraction rules, including the never-fabricate rule and the escalation
   policy (low confidence / exhausted asks -> graceful wrap-up + flag).
"""

from __future__ import annotations

from typing import Any, Mapping

LOW_CONFIDENCE_THRESHOLD: float = 0.6
MAX_ASKS_PER_FIELD: int = 3

DISCLOSURE_HEADER = "MANDATORY DISCLOSURE - say this VERBATIM as your very first utterance, before anything else:"
PERSONA_HEADER = "PERSONA & COMPANY CONTEXT:"
QUESTIONS_HEADER = "QUESTION FLOW - ask in this exact order, one question at a time, adapting naturally to the caller's answers:"
EXTRACTION_HEADER = "EXTRACTION RULES:"


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

    # 2. Persona + company context.
    persona_parts: list[str] = [PERSONA_HEADER]
    system_prompt = str(config.get("system_prompt") or "").strip()
    if system_prompt:
        persona_parts.append(system_prompt)
    company_context = config.get("company_context")
    if company_context:
        import json

        persona_parts.append(
            json.dumps(company_context, indent=2, ensure_ascii=False, default=str)
        )
    sections.append("\n".join(persona_parts))

    # 3. Numbered question flow.
    question_flow = config.get("question_flow") or []
    lines: list[str] = [QUESTIONS_HEADER]
    number = 0
    for item in question_flow:
        text = _question_text(item)
        if not text:
            continue
        number += 1
        lines.append(f"{number}. {text}")
    sections.append("\n".join(lines))

    # 4. Extraction rules with never-fabricate + escalation policy.
    extraction_lines: list[str] = [
        EXTRACTION_HEADER,
        "For every field in the extraction schema below, capture what the caller says.",
        "- After each answer, call `record_extracted_field(field_name, value, confidence)` with an honest confidence between 0.0 and 1.0.",
        "- NEVER fabricate or guess a value: if you are not certain what was said, ask a short clarifying question instead of inventing data.",
        (
            f"- If your confidence for a value is below {LOW_CONFIDENCE_THRESHOLD}, treat that field as NOT captured: "
            "wrap up gracefully and clearly flag it when you call `end_call`."
        ),
        (
            f"- If a required field is still unfilled after asking up to {MAX_ASKS_PER_FIELD} times, stop asking about it, wrap up gracefully, "
            "and flag it in your `end_call` summary."
        ),
        "- To finish the call, call `end_call(summary)` with a factual summary of captured fields, flagged/unfilled fields, and the caller's mood.",
    ]
    extraction_schema = config.get("extraction_schema") or {}
    if isinstance(extraction_schema, Mapping):
        schema_lines: list[str] = ["Extraction schema:"]
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

    # Optional extra escalation rules supplied by the agent author.
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
        sections.append(f"ADDITIONAL ESCALATION RULES - end the call politely and hand off to a human when:\n{wrapped}")

    return "\n\n".join(sections)
