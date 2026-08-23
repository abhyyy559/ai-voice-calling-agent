"""Pydantic v2 request/response schemas for the admin, internal and test-call APIs."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

# --- domain configs ---------------------------------------------------------


class DomainConfigOut(BaseModel):
    id: int
    name: str
    display_name: str
    version: int


class DomainConfigSyncOut(BaseModel):
    synced: int
    names: list[str]


# --- campaigns ---------------------------------------------------------------


class CampaignCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    # Legacy read-only path (pre-platform data). New campaigns pin agent_version_id.
    domain_config_id: Optional[int] = None
    agent_version_id: Optional[int] = None


class CampaignOut(BaseModel):
    id: int
    name: str
    status: str
    org_id: Optional[int] = None
    domain_config_id: Optional[int]
    domain_config_name: Optional[str] = None
    agent_version_id: Optional[int] = None
    schedule_window_start: Optional[datetime] = None
    schedule_window_end: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactCounts(BaseModel):
    total: int = 0
    pending_review: int = 0
    invalid: int = 0
    queued: int = 0
    calling: int = 0
    completed: int = 0
    no_answer: int = 0
    busy: int = 0
    failed: int = 0
    opted_out: int = 0


class CampaignListItem(BaseModel):
    id: int
    name: str
    status: str
    org_id: Optional[int] = None
    domain_config_id: Optional[int]
    domain_config_name: Optional[str] = None
    agent_version_id: Optional[int] = None
    counts: ContactCounts
    created_at: Optional[datetime] = None


class CampaignDetail(CampaignOut):
    counts: ContactCounts


class DashboardOut(BaseModel):
    campaign_id: int
    campaign_status: str
    counts: ContactCounts
    calls_in_flight: int
    recent_calls: list[dict[str, Any]]


# --- contacts ----------------------------------------------------------------


class ContactPatch(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    custom_fields: Optional[dict[str, Any]] = None
    status: Optional[str] = None
    consent: Optional[bool] = None


class ContactOut(BaseModel):
    id: int
    campaign_id: int
    name: Optional[str]
    phone: str
    external_id: Optional[str]
    custom_fields: dict[str, Any]
    status: str
    consent: bool
    consent_source: Optional[str]
    attempt_count: int
    next_attempt_at: Optional[datetime]
    last_call_id: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactPage(BaseModel):
    items: list[ContactOut]
    total: int
    page: int
    page_size: int


class ImportResult(BaseModel):
    imported: int
    invalid: int
    errors: list[dict[str, Any]]


# --- calls -------------------------------------------------------------------


class CallOut(BaseModel):
    id: int
    campaign_id: int
    contact_id: int
    provider_call_id: Optional[str]
    status: str
    started_at: Optional[datetime]
    answered_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[float]
    recording_url: Optional[str]
    summary: Optional[str]
    outcome: Optional[str]
    flagged_for_human: bool
    cost: Optional[dict[str, Any]]
    latency: Optional[dict[str, Any]]
    created_at: Optional[datetime] = None


class CampaignCallOut(CallOut):
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class TranscriptTurnOut(BaseModel):
    turn_index: int
    speaker: str
    text: str
    timestamp: Optional[datetime] = None


class ExtractedFieldOut(BaseModel):
    field_name: str
    field_value: Optional[str]
    source_turn_index: Optional[int]
    confidence: Optional[float]


class CallDetailOut(CallOut):
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    transcript: list[TranscriptTurnOut]
    extracted_fields: list[ExtractedFieldOut]


# --- test call ----------------------------------------------------------------


class TestCallRequest(BaseModel):
    to: Optional[str] = None
    domain_config_id: int


class TestCallOut(BaseModel):
    call_id: int
    provider_call_id: str
    status: str


# --- internal (voice-agent) ----------------------------------------------------


class InternalOk(BaseModel):
    ok: bool = True


class RetentionRunOut(BaseModel):
    cutoff: datetime
    calls_older_than_cutoff: int
    transcripts_deleted: int
    recording_urls_cleared: int
