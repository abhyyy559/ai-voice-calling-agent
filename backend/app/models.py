"""SQLAlchemy ORM models — refined schema from PRD §6.

Notes:
- All timestamps are timezone-naive UTC (see app.timeutil).
- ``contacts.last_call_id`` is a *logical* FK to ``calls.id``. The DB-level
  constraint is created in the Alembic migration (Postgres) but omitted from
  the model metadata so ``Base.metadata.create_all`` also works on SQLite,
  which cannot ALTER TABLE ADD CONSTRAINT. The only ORM-level circular
  dependency is avoided this way.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# --- status vocabularies ---------------------------------------------------
CAMPAIGN_STATUSES = ("draft", "running", "paused", "completed", "canceled")
CONTACT_STATUSES = (
    "pending_review",
    "invalid",
    "queued",
    "calling",
    "completed",
    "no_answer",
    "busy",
    "failed",
    "opted_out",
)
CALL_STATUSES = (
    "queued",
    "ringing",
    "in_progress",
    "completed",
    "no_answer",
    "busy",
    "failed",
    "canceled",
)
# call states counted as "in flight" for concurrency limiting
IN_FLIGHT_CALL_STATUSES = ("queued", "ringing", "in_progress")


class Base(DeclarativeBase):
    """Declarative base for all models."""


class DomainConfig(Base):
    """A versioned call-domain configuration (question flow, extraction schema, ...)."""

    __tablename__ = "domain_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    config: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="domain_config")


class Campaign(Base):
    """A calling campaign: contacts + domain config + schedule."""

    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain_config_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("domain_configs.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    schedule_window_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    schedule_window_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    domain_config: Mapped[Optional[DomainConfig]] = relationship(back_populates="campaigns")
    contacts: Mapped[list["Contact"]] = relationship(back_populates="campaign")
    calls: Mapped[list["Call"]] = relationship(back_populates="campaign")


class Contact(Base):
    """A call recipient within a campaign."""

    __tablename__ = "contacts"
    __table_args__ = (Index("ix_contacts_campaign_status", "campaign_id", "status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"), nullable=False, index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending_review")
    consent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    consent_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Logical FK to calls.id (constraint added by the Alembic migration only).
    last_call_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    campaign: Mapped[Campaign] = relationship(back_populates="contacts")
    consent_records: Mapped[list["ConsentRecord"]] = relationship(back_populates="contact")


class Call(Base):
    """An outbound call attempt against a contact."""

    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id"), nullable=False, index=True
    )
    contact_id: Mapped[int] = mapped_column(
        ForeignKey("contacts.id"), nullable=False, index=True
    )
    provider_call_id: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recording_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    flagged_for_human: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cost: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    latency: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    campaign: Mapped[Campaign] = relationship(back_populates="calls")
    contact: Mapped[Contact] = relationship(backref="calls")
    events: Mapped[list["CallEvent"]] = relationship(
        back_populates="call", cascade="all, delete-orphan"
    )
    transcripts: Mapped[list["Transcript"]] = relationship(
        back_populates="call", cascade="all, delete-orphan"
    )
    extracted_fields: Mapped[list["ExtractedField"]] = relationship(
        back_populates="call", cascade="all, delete-orphan"
    )


class CallEvent(Base):
    """Raw provider/webhook event log for a call."""

    __tablename__ = "call_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    call: Mapped[Call] = relationship(back_populates="events")


class Transcript(Base):
    """One conversational turn of a call."""

    __tablename__ = "transcripts"
    __table_args__ = (Index("ix_transcripts_call_turn", "call_id", "turn_index"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(10), nullable=False)  # agent | caller
    text: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    call: Mapped[Call] = relationship(back_populates="transcripts")


class ExtractedField(Base):
    """A structured field extracted from a call, traceable to a transcript turn."""

    __tablename__ = "extracted_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("calls.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(200), nullable=False)
    field_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_turn_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    call: Mapped[Call] = relationship(back_populates="extracted_fields")


class ConsentRecord(Base):
    """Recorded consent basis for a contact/phone (PRD §8)."""

    __tablename__ = "consent_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("contacts.id"), nullable=True, index=True
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False, default="calling")
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    contact: Mapped[Optional[Contact]] = relationship(back_populates="consent_records")
