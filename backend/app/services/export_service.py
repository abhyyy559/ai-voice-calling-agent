"""Campaign results export to CSV (utf-8-sig BOM) or XLSX (bold header)."""
from __future__ import annotations

import csv
import io
from typing import Any

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Call, Campaign, Contact, ExtractedField, Transcript

CSV_MEDIA_TYPE = "text/csv"
XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

_FIXED_PREFIX = ["Name", "Phone", "External ID"]
_FIXED_MIDDLE = ["Contact Status", "Call Status", "Outcome", "Duration (s)", "E2E Latency (ms)"]
_FIXED_SUFFIX = ["Flagged For Human", "Summary", "Recording URL", "Transcript"]


def _collect_data(db: Session, campaign_id: int) -> tuple[list[str], list[list[Any]], list[Contact], list[Call]]:
    """Return (header, rows, contacts, latest_calls) for the campaign."""
    contacts = list(
        db.scalars(
            select(Contact).where(Contact.campaign_id == campaign_id).order_by(Contact.id)
        )
    )
    calls = list(
        db.scalars(
            select(Call).where(Call.campaign_id == campaign_id).order_by(Call.created_at, Call.id)
        )
    )
    latest_by_contact: dict[int, Call] = {}
    for call in calls:  # ordered ascending, last write wins
        latest_by_contact[call.contact_id] = call

    custom_keys = sorted({k for c in contacts for k in (c.custom_fields or {})})
    extracted_names = sorted(
        set(
            db.scalars(
                select(ExtractedField.field_name)
                .join(Call, Call.id == ExtractedField.call_id)
                .where(Call.campaign_id == campaign_id)
                .distinct()
            )
        )
    )
    header = (
        _FIXED_PREFIX + custom_keys + _FIXED_MIDDLE + extracted_names + _FIXED_SUFFIX
    )

    field_values: dict[int, dict[str, str]] = {}
    transcripts_by_call: dict[int, list[str]] = {}
    e2e_by_call: dict[int, float] = {}
    if calls:
        call_ids = [c.id for c in calls]
        for f in db.scalars(select(ExtractedField).where(ExtractedField.call_id.in_(call_ids))):
            field_values.setdefault(f.call_id, {})[f.field_name] = f.field_value
        for t in db.scalars(
            select(Transcript)
            .where(Transcript.call_id.in_(call_ids))
            .order_by(Transcript.call_id, Transcript.turn_index)
        ):
            transcripts_by_call.setdefault(t.call_id, []).append(f"{t.speaker}: {t.text}")
        # Avg end-to-end turn latency over the turns that reported it.
        e2e_sums: dict[int, tuple[float, int]] = {}
        for t in db.scalars(
            select(Transcript).where(
                Transcript.call_id.in_(call_ids), Transcript.e2e_ms.isnot(None)
            )
        ):
            total, n = e2e_sums.get(t.call_id, (0.0, 0))
            e2e_sums[t.call_id] = (total + float(t.e2e_ms), n + 1)
        for call_id_value, (total, n) in e2e_sums.items():
            e2e_by_call[call_id_value] = round(total / n, 1)

    rows: list[list[Any]] = []
    for contact in contacts:
        call = latest_by_contact.get(contact.id)
        fields = field_values.get(call.id, {}) if call else {}
        row: list[Any] = [
            contact.name or "",
            contact.phone,
            contact.external_id or "",
        ]
        row += [(contact.custom_fields or {}).get(k, "") for k in custom_keys]
        row += [
            contact.status,
            call.status if call else "",
            (call.outcome or "") if call else "",
            call.duration_seconds if call and call.duration_seconds is not None else "",
            e2e_by_call.get(call.id, "") if call else "",
        ]
        row += [fields.get(name, "") for name in extracted_names]
        row += [
            bool(call.flagged_for_human) if call else False,
            (call.summary or "") if call else "",
            (call.recording_url or "") if call else "",
            "; ".join(transcripts_by_call.get(call.id, [])) if call else "",
        ]
        rows.append(row)
    return header, rows, contacts, calls


def export_csv(db: Session, campaign: Campaign) -> bytes:
    """Render campaign results as CSV bytes with a utf-8 BOM."""
    header, rows, _, _ = _collect_data(db, campaign.id)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig")


def export_xlsx(db: Session, campaign: Campaign) -> bytes:
    """Render campaign results as an XLSX workbook with a bold header row."""
    header, rows, _, _ = _collect_data(db, campaign.id)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "results"
    sheet.append(header)
    from openpyxl.styles import Font

    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for row in rows:
        sheet.append(row)
    out = io.BytesIO()
    workbook.save(out)
    return out.getvalue()
