"""Contact-list import (CSV / XLSX) with phone normalization and consent capture."""
from __future__ import annotations

import csv
import io
import re
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import ConsentRecord, Contact
from app.timeutil import utcnow

_WHITELIST = re.compile(r"^[+0-9]+$")
_TRUTHY = {"1", "true", "yes", "y", "consent", "consented", "ok", "t"}


def cell_to_str(value: Any) -> str:
    """Coerce a spreadsheet/csv cell to a clean string."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def normalize_phone(raw: str) -> tuple[str, bool]:
    """Normalize a phone number to E.164 for India or pass through valid E.164.

    Returns ``(normalized, valid)``. On failure the best-effort stripped value
    is returned with valid=False so it can be stored with status=invalid.
    """
    if raw is None:
        return "", False
    cleaned = re.sub(r"[\s\-().]", "", str(raw).strip())
    if not cleaned:
        return "", False
    if not _WHITELIST.match(cleaned):
        return cleaned, False

    if cleaned.startswith("+"):
        digits = cleaned[1:]
        # E.164: 11-15 digits total, and Indian numbers must be +91 + 10 digits.
        if digits.isdigit() and 11 <= len(digits) <= 15:
            if digits.startswith("91"):
                return f"+{digits}", len(digits) == 12 and digits[2] in "6789"
            return f"+{digits}", True
        return cleaned, False

    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
        return normalize_phone(cleaned)

    if cleaned.startswith("0"):
        cleaned = cleaned[1:]

    if len(cleaned) == 12 and cleaned.startswith("91"):
        cleaned = cleaned[2:]

    if len(cleaned) == 10 and cleaned[0] in "6789" and cleaned.isdigit():
        return f"+91{cleaned}", True

    return cleaned, False


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in _TRUTHY


def _read_rows(data: bytes, filename: str) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) from CSV or XLSX bytes, detected by extension."""
    name = filename.lower()
    if name.endswith(".xlsx"):
        from openpyxl import load_workbook  # lazy import

        workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            sheet = workbook.active
            rows = [[cell_to_str(c) for c in row] for row in sheet.iter_rows(values_only=True)]
        finally:
            workbook.close()
        if not rows:
            return [], []
        return rows[0], [r for r in rows[1:] if any(cell != "" for cell in r)]

    # default: CSV (accepts a BOM)
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = [r for r in reader if any(cell.strip() != "" for cell in r)]
    if not rows:
        return [], []
    return [c.strip() for c in rows[0]], rows[1:]


class ImportMapping:
    """Parsed column mapping sent by the import UI."""

    def __init__(self, mapping: dict[str, Any]) -> None:
        self.name_col: Optional[str] = mapping.get("name_col")
        self.phone_col: str = mapping.get("phone_col") or ""
        self.id_col: Optional[str] = mapping.get("id_col")
        self.consent_col: Optional[str] = mapping.get("consent_col")
        custom = mapping.get("custom") or {}
        if not isinstance(custom, dict):
            raise ValueError("'custom' mapping must be an object of {field: column}")
        self.custom: dict[str, str] = {str(k): str(v) for k, v in custom.items()}


def import_contacts(
    db: Session,
    campaign_id: int,
    data: bytes,
    filename: str,
    mapping: dict[str, Any],
    consent_default: bool = False,
) -> dict[str, Any]:
    """Parse and import a contact file. Returns {imported, invalid, errors}."""
    parsed = ImportMapping(mapping)
    if not parsed.phone_col:
        raise ValueError("mapping must include a 'phone_col'")
    header, rows = _read_rows(data, filename)
    if not header:
        raise ValueError("file has no header row")
    index = {name: i for i, name in enumerate(header)}

    missing = [c for c in (parsed.phone_col, parsed.name_col, parsed.id_col, parsed.consent_col)
               if c and c not in index]
    missing += [col for col in parsed.custom.values() if col not in index]
    if missing:
        raise ValueError(f"columns not found in file: {', '.join(sorted(set(missing)))}")

    def cell(row: list[str], col: Optional[str]) -> str:
        if col is None:
            return ""
        i = index[col]
        return row[i] if i < len(row) else ""

    imported = 0
    invalid = 0
    errors: list[dict[str, Any]] = []
    now = utcnow()
    for row_num, row in enumerate(rows, start=2):
        name = cell(row, parsed.name_col)
        raw_phone = cell(row, parsed.phone_col)
        phone, ok = normalize_phone(raw_phone)
        consent = _is_truthy(cell(row, parsed.consent_col)) if parsed.consent_col else consent_default
        custom_fields = {key: cell(row, col) for key, col in parsed.custom.items()}

        if not ok:
            invalid += 1
            errors.append(
                {"row": row_num, "error": f"invalid phone number: {raw_phone!r}"}
            )
            status = "invalid"
        else:
            imported += 1
            status = "pending_review"

        contact = Contact(
            campaign_id=campaign_id,
            name=name or None,
            phone=phone,
            external_id=cell(row, parsed.id_col) or None,
            custom_fields=custom_fields,
            status=status,
            consent=bool(consent),
            consent_source=(
                f"import:{parsed.consent_col}" if parsed.consent_col and consent
                else ("import:consent_default" if consent else None)
            ),
        )
        db.add(contact)
        db.flush()
        if consent and ok:
            db.add(
                ConsentRecord(
                    contact_id=contact.id,
                    phone=phone,
                    consent_type="calling",
                    consent_given=True,
                    source=f"import:{filename}",
                    captured_at=now,
                )
            )

    db.commit()
    return {"imported": imported, "invalid": invalid, "errors": errors}
