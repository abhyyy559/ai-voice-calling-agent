"""Extraction bookkeeping and framework-agnostic tool implementations.

``VoiceAgentTools`` implements the two LLM function tools of the pipeline:

- ``record_extracted_field(field_name, value, confidence)``
- ``end_call(summary)``

The class is intentionally free of livekit imports so the escalation logic can
be unit tested offline against a fake backend client; ``app.pipeline`` wraps
these callables as LiveKit ``@function_tool`` methods.

Escalation policy (FR-12): confidence < 0.6, or a required field still unfilled
after 3 asks -> graceful wrap-up + flag. Values are never fabricated.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Protocol

logger = logging.getLogger("voice_agent.extraction")

LOW_CONFIDENCE_THRESHOLD: float = 0.6
MAX_ASKS_PER_FIELD: int = 3


class ExtractionBackend(Protocol):
    """Minimal backend surface needed by the tools (real or fake)."""

    async def post_fields(
        self, call_id: str, fields: list[Mapping[str, Any]]
    ) -> bool: ...

    async def post_complete(
        self,
        call_id: str,
        *,
        status: str = "completed",
        error: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> bool: ...


@dataclass(frozen=True)
class RecordResult:
    """Outcome of a single ``record_extracted_field`` attempt."""

    field_name: str
    value: str
    confidence: float
    accepted: bool
    flagged: bool
    should_wrap_up: bool
    reason: str


@dataclass
class ExtractionCoordinator:
    """Tracks recorded fields, ask counts, and pending wrap-up flags."""

    required_fields: frozenset[str] = field(default_factory=frozenset)
    low_confidence_threshold: float = LOW_CONFIDENCE_THRESHOLD
    max_asks_per_field: int = MAX_ASKS_PER_FIELD

    recorded: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    flagged_fields: Dict[str, str] = field(default_factory=dict)
    ask_counts: Dict[str, int] = field(default_factory=dict)
    _wrap_up_reasons: List[str] = field(default_factory=list)

    def mark_asked(self, field_name: str) -> int:
        """Record that a question about ``field_name`` was asked once more."""
        count = self.ask_counts.get(field_name, 0) + 1
        self.ask_counts[field_name] = count
        if (
            count >= self.max_asks_per_field
            and field_name in self.required_fields
            and field_name not in self.recorded
            and field_name not in self.flagged_fields
        ):
            reason = (
                f"Required field '{field_name}' still unfilled after "
                f"{self.max_asks_per_field} asks - giving up on it and wrapping up."
            )
            self.flagged_fields[field_name] = reason
            self._wrap_up_reasons.append(reason)
            logger.warning("escalation: %s", reason)
        return count

    def record(self, field_name: str, value: str, confidence: float) -> RecordResult:
        """Store (or flag) one extracted value. Never invents data."""
        clamped = max(0.0, min(1.0, float(confidence)))
        if clamped < self.low_confidence_threshold:
            reason = (
                f"Low confidence ({clamped:.2f}) for '{field_name}' below "
                f"{self.low_confidence_threshold:.2f} - not captured."
            )
            self.flagged_fields.setdefault(field_name, reason)
            self._wrap_up_reasons.append(reason)
            logger.warning("escalation: %s", reason)
            return RecordResult(
                field_name=field_name,
                value=value,
                confidence=clamped,
                accepted=False,
                flagged=True,
                should_wrap_up=True,
                reason=reason,
            )
        self.recorded[field_name] = {"value": value, "confidence": clamped}
        return RecordResult(
            field_name=field_name,
            value=value,
            confidence=clamped,
            accepted=True,
            flagged=False,
            should_wrap_up=False,
            reason="",
        )

    def consume_wrap_up(self) -> Optional[str]:
        """Pop the oldest pending wrap-up reason, or ``None`` if none."""
        if self._wrap_up_reasons:
            return self._wrap_up_reasons.pop(0)
        return None

    def unfilled_required(self) -> List[str]:
        """Required fields with no accepted value yet."""
        return sorted(self.required_fields - set(self.recorded))


class VoiceAgentTools:
    """Framework-free implementations of the two pipeline function tools."""

    def __init__(
        self,
        coordinator: ExtractionCoordinator,
        backend: ExtractionBackend,
        call_id: str,
    ) -> None:
        self._coordinator = coordinator
        self._backend = backend
        self._call_id = call_id

    async def record_extracted_field(
        self,
        field_name: str,
        value: str,
        confidence: float,
        *,
        source_turn_index: int = 0,
    ) -> str:
        """Record one extracted field and escalate when it is unreliable."""
        result = self._coordinator.record(field_name, str(value), float(confidence))
        await self._backend.post_fields(
            self._call_id,
            [
                {
                    "field_name": result.field_name,
                    "field_value": result.value,
                    "confidence": result.confidence,
                    "source_turn_index": source_turn_index,
                }
            ],
        )
        if result.should_wrap_up:
            await self._backend.post_complete(
                self._call_id,
                status="wrapped_up_flagged",
                error=result.reason,
            )
            return (
                f"FLAGGED - {result.reason} Do NOT guess this value. Wrap up the "
                f"call gracefully now and call `end_call` with a summary noting "
                f"that '{result.field_name}' could not be reliably captured."
            )
        return (
            f"Recorded {result.field_name}='{result.value}' "
            f"(confidence {result.confidence:.2f})."
        )

    async def end_call(self, summary: str) -> str:
        """Finalize the call, annotating any unfilled required fields."""
        unfilled = self._coordinator.unfilled_required()
        final_summary = str(summary or "").strip()
        if unfilled:
            final_summary = (
                f"{final_summary} | Unfilled required fields (flagged, never "
                f"fabricated): {', '.join(unfilled)}."
            ).strip()
        await self._backend.post_complete(
            self._call_id,
            status="completed",
            error=None,
            summary=final_summary or None,
        )
        return f"Call ended. Summary posted: {final_summary}"
