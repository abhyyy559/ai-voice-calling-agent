"""Campaign results export tests: v2 columns (call status, duration,
avg e2e latency per call, one column per extracted field, flattened contact
custom_fields)."""

from __future__ import annotations

import csv
import io
from typing import Any

from app.models import Call, Campaign, Contact, ExtractedField, Organization, Transcript
from app.services.export_service import export_csv


def _seed(db: Any) -> Campaign:
    org = Organization(name="Acme", slug="acme")
    db.add(org)
    db.flush()
    campaign = Campaign(org_id=org.id, name="Absents - Aug")
    db.add(campaign)
    db.flush()
    contacted = Contact(
        campaign_id=campaign.id,
        org_id=org.id,
        name="Suresh",
        phone="+911234567890",
        status="completed",
        custom_fields={"student_name": "Aarav", "class_section": "10-B"},
    )
    pending = Contact(
        campaign_id=campaign.id,
        org_id=org.id,
        name="NoCall Yet",
        phone="+919876543210",
        status="queued",
        custom_fields={"student_name": "Ira"},
    )
    db.add_all([contacted, pending])
    db.flush()
    call = Call(
        campaign_id=campaign.id,
        contact_id=contacted.id,
        kind="phone",
        status="completed",
        duration_seconds=95.0,
    )
    db.add(call)
    db.flush()
    db.add_all(
        [
            Transcript(call_id=call.id, turn_index=0, speaker="agent", text="hi", e2e_ms=None),
            Transcript(call_id=call.id, turn_index=1, speaker="caller", text="fever", e2e_ms=None),
            Transcript(
                call_id=call.id, turn_index=1, speaker="agent", text="sorry to hear", e2e_ms=1000.0
            ),
            Transcript(
                call_id=call.id, turn_index=2, speaker="agent", text="ok", e2e_ms=2000.0
            ),
        ]
    )
    db.add(
        ExtractedField(
            call_id=call.id, field_name="reason_for_absence", field_value="fever"
        )
    )
    db.commit()
    return campaign


def test_export_has_v2_columns_and_values(session_factory):
    from sqlalchemy import select

    with session_factory() as db:
        campaign = _seed(db)
        csv_bytes = export_csv(db, campaign)

    rows = list(csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    header, data = rows[0], rows[1:]
    assert len(data) == 2

    # V2 columns present.
    for col in ("Contact Status", "Call Status", "Duration (s)", "E2E Latency (ms)"):
        assert col in header, f"missing {col}"
    assert "reason_for_absence" in header  # extracted field column
    assert "student_name" in header and "class_section" in header  # custom fields

    def cell(row_idx: int, col_name: str) -> str:
        return data[row_idx][header.index(col_name)]

    # Call-scoped values on the contacted row.
    assert cell(0, "Call Status") == "completed"
    assert float(cell(0, "Duration (s)")) == 95.0
    assert float(cell(0, "E2E Latency (ms)")) == 1500.0  # avg(1000, 2000); Nones skipped
    assert cell(0, "reason_for_absence") == "fever"
    assert cell(0, "student_name") == "Aarav"

    # Uncalled contact: empty call columns, custom fields still flattened.
    assert cell(1, "Call Status") == ""
    assert cell(1, "E2E Latency (ms)") == ""
    assert cell(1, "student_name") == "Ira"
