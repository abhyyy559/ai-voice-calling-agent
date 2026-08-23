"""Telephony abstraction for placing outbound calls.

``TelephonyClient`` is the interface the dialer depends on; ``TwilioClient``
is the production implementation and ``FakeTelephonyClient`` is used in tests
and local development without Twilio credentials.
"""
from __future__ import annotations

import logging
from typing import Protocol

from app.config import Settings

logger = logging.getLogger(__name__)


class TelephonyClient(Protocol):
    """Interface for placing an outbound call.

    Returns the provider call id (Twilio CallSid). Raises on failure —
    the dialer converts exceptions into per-call failures.
    """

    def place_call(self, to: str, call_id: int) -> str:
        ...  # pragma: no cover


class TwilioClient:
    """Production telephony client using the Twilio REST API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _voice_webhook(self, call_id: int) -> str:
        return f"{self.settings.public_base_url.rstrip('/')}/twilio/voice?call_id={call_id}"

    def place_call(self, to: str, call_id: int) -> str:
        from twilio.rest import Client  # lazy import keeps tests light

        settings = self.settings
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        base = settings.public_base_url.rstrip("/")
        call = client.calls.create(
            to=to,
            from_=settings.twilio_phone_number,
            url=self._voice_webhook(call_id),
            method="POST",
            status_callback=f"{base}/twilio/status",
            status_callback_method="POST",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=True,
            recording_status_callback=f"{base}/twilio/recording",
            recording_status_callback_method="POST",
        )
        logger.info("placed twilio call call_id=%s sid=%s to=%s", call_id, call.sid, to)
        return str(call.sid)


class FakeTelephonyClient:
    """In-memory fake; records placed calls and returns synthetic Sids."""

    def __init__(self) -> None:
        self.placed: list[tuple[str, int]] = []
        self.fail_next = False

    def place_call(self, to: str, call_id: int) -> str:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("fake telephony failure")
        self.placed.append((to, call_id))
        return f"CAfake{call_id:010d}"
