import React from 'react';

export const EMPTY_MAPPING = { name_col: null, phone_col: null, id_col: null, consent_col: null };

// ---------------------------------------------------------------------------
// Delimited-text (CSV/TSV) parsing — quote-aware, delimiter auto-detected.
// ---------------------------------------------------------------------------

function detectDelimiter(firstLine) {
  const candidates = [',', ';', '\t', '|'];
  let best = ',';
  let bestCount = 0;
  for (const c of candidates) {
    const count = firstLine.split(c).length - 1;
    if (count > bestCount) {
      bestCount = count;
      best = c;
    }
  }
  return best;
}

/**
 * Parse a whole delimited text file into an array of row arrays.
 * Handles quoted cells (including newlines and escaped "" inside quotes).
 */
export function parseDelimited(text) {
  const clean = String(text).replace(/^\uFEFF/, '');
  const firstBreak = clean.search(/[\r\n]/);
  const firstLine = firstBreak === -1 ? clean : clean.slice(0, firstBreak);
  const delim = detectDelimiter(firstLine);

  const rows = [];
  let row = [];
  let cur = '';
  let inQuotes = false;

  const pushCell = () => {
    row.push(cur.trim());
    cur = '';
  };
  const pushRow = () => {
    pushCell();
    if (row.length > 1 || (row.length === 1 && row[0] !== '')) rows.push(row);
    row = [];
  };

  for (let i = 0; i < clean.length; i++) {
    const ch = clean[i];
    if (inQuotes) {
      if (ch === '"') {
        if (clean[i + 1] === '"') {
          cur += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        cur += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === delim) {
      pushCell();
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && clean[i + 1] === '\n') i++;
      pushRow();
    } else {
      cur += ch;
    }
  }
  pushRow();
  return rows;
}

// ---------------------------------------------------------------------------
// Phone validation (India-first, tolerant of formatting)
// ---------------------------------------------------------------------------

/** Strip spaces, dashes, dots and brackets so "+91 98480 12345" becomes comparable. */
export function normalizePhoneValue(value) {
  if (value == null) return '';
  return String(value).trim().replace(/[().\-\s]/g, '');
}

/**
 * True when the value looks like a dialable number:
 * Indian mobile (optionally +91/0 prefixed) or any E.164-style number.
 */
export function isValidPhoneValue(value) {
  const s = normalizePhoneValue(value);
  if (!s || !/^\+?[0-9]+$/.test(s)) return false;
  if (/^(?:\+?91|0)?[6-9]\d{9}$/.test(s)) return true;
  if (/^\+?[1-9]\d{7,14}$/.test(s)) return true;
  return false;
}

// ---------------------------------------------------------------------------
// Auto-mapping (best guess, never asks the user to type column names)
// ---------------------------------------------------------------------------

/**
 * Fuzzy-match detected headers onto target fields. Exact/common names win,
 * looser substring matches are the fallback. Chosen columns never collide.
 */
export function guessMapping(headers) {
  if (!Array.isArray(headers)) return { ...EMPTY_MAPPING };
  const norm = headers.map((h) => String(h).toLowerCase().replace(/[\s\-]+/g, '_'));
  const taken = new Set();
  const find = (exactRe, looseRe) => {
    let idx = norm.findIndex((h, i) => !taken.has(i) && exactRe.test(h));
    if (idx === -1) idx = norm.findIndex((h, i) => !taken.has(i) && looseRe.test(h));
    if (idx === -1) return null;
    taken.add(idx);
    return headers[idx];
  };

  const phone_col = find(
    /^(phone|phone_?no|phone_?number|mobile|mobile_?no|mobile_?number|number|contact_?number|whatsapp|msisdn|cell)$/,
    /(phone|mobile|whatsapp|msisdn|number)/
  );
  const name_col = find(
    /^(name|full_?name|student_?name|first_?name|given_?name|contact_?name|customer_?name)$/,
    /(^|_)(name)(_|$)/
  );
  const id_col = find(
    /^(id|roll|roll_?no|roll_?number|enrollment|enrollment_?no|external_?id|regd?_?no)$/,
    /(^|_)(id|roll|enrollment)(_no)?$/
  );
  const consent_col = find(/^(consent|consent_?given|permission|opt_?in)$/, /consent|permission|opt_?in/);

  return { name_col, phone_col, id_col, consent_col };
}

// ---------------------------------------------------------------------------
// UI
// ---------------------------------------------------------------------------

const TARGETS = [
  { key: 'name_col', label: 'Contact name', required: false },
  { key: 'phone_col', label: 'Phone number', required: true },
  { key: 'id_col', label: 'External ID (roll no., etc.)', required: false },
  { key: 'consent_col', label: 'Consent', required: false },
];

function HeaderSelect({ headers, value, onChange }) {
  return (
    <select value={value || ''} onChange={(e) => onChange(e.target.value || null)}>
      <option value="">— Not mapped —</option>
      {headers.map((h, idx) => (
        <option key={`${h}-${idx}`} value={h}>
          {h}
        </option>
      ))}
    </select>
  );
}

/**
 * Column mapping UI fed entirely by the client-side parser — users pick from
 * DETECTED headers, they never type column names. Also renders a small
 * preview of the first rows, flagging invalid phone values inline.
 *
 * headers: string[] (from CSV/XLSX parse)
 * rows: string[][] data rows (header row excluded)
 */
export default function ColumnMapper({
  headers,
  rows = [],
  maxPreviewRows = 5,
  mapping,
  onMappingChange,
  customRows = [],
  onCustomRowsChange,
}) {
  const known = Array.isArray(headers) && headers.length > 0;
  const setField = (key, val) => onMappingChange({ ...mapping, [key]: val });

  const setCustomRow = (idx, patch) => {
    const next = customRows.map((r, i) => (i === idx ? { ...r, ...patch } : r));
    onCustomRowsChange(next);
  };

  if (!known) return null;

  const nameIdx = headers.indexOf(mapping.name_col);
  const phoneIdx = headers.indexOf(mapping.phone_col);
  const idIdx = headers.indexOf(mapping.id_col);
  const consentIdx = headers.indexOf(mapping.consent_col);
  const preview = rows.slice(0, maxPreviewRows);

  const cellClass = (colIdx) => {
    if (colIdx === phoneIdx) return 'preview-cell preview-phone';
    if (colIdx === nameIdx || colIdx === idIdx || colIdx === consentIdx) return 'preview-cell preview-mapped';
    return 'preview-cell';
  };

  const phoneBad = (value, colIdx) => colIdx === phoneIdx && !isValidPhoneValue(value);

  return (
    <div className="mapper">
      <p className="hint">
        We found <strong>{headers.length} column{headers.length === 1 ? '' : 's'}</strong> in your file. Confirm what each
        field below means — we pre-filled our best guess, change any dropdown if needed.
      </p>

      <div className="mapper-rows">
        {TARGETS.map((t) => (
          <div key={t.key} className="mapper-row">
            <label className="mapper-label">
              {t.label}
              {t.required ? <span className="req-star"> *</span> : null}
            </label>
            <div className="mapper-control">
              <HeaderSelect headers={headers} value={mapping[t.key]} onChange={(v) => setField(t.key, v)} />
            </div>
          </div>
        ))}
      </div>

      {preview.length > 0 && (
        <div className="import-preview-wrap">
          <p className="preview-caption">
            First {Math.min(preview.length, maxPreviewRows)} rows — highlighted columns are the ones you mapped above.
          </p>
          <div className="table-wrap import-preview">
            <table className="data-table">
              <thead>
                <tr>
                  {headers.map((h, idx) => (
                    <th key={`${h}-${idx}`} className={idx === phoneIdx ? 'preview-head-phone' : undefined}>
                      {h || '—'}
                      {idx === phoneIdx ? ' · phone' : ''}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, ri) => {
                  const rowHasBadPhone = phoneIdx >= 0 && phoneBad(row[phoneIdx], phoneIdx);
                  return (
                    <tr key={ri} className={rowHasBadPhone ? 'preview-row-flagged' : undefined}>
                      {headers.map((_, ci) => (
                        <td key={ci} className={cellClass(ci)}>
                          <span
                            className={
                              phoneBad(row[ci], ci) ? 'preview-bad-value' : undefined
                            }
                            title={phoneBad(row[ci], ci) ? 'Invalid phone number — this row will be flagged' : undefined}
                          >
                            {String(row[ci] != null && row[ci] !== '' ? row[ci] : '—')}
                          </span>
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {rows.length > preview.length && (
            <p className="preview-caption">
              …and {rows.length - preview.length} more row{rows.length - preview.length === 1 ? '' : 's'} in the file.
            </p>
          )}
        </div>
      )}

      <div className="mapper-custom">
        <div className="mapper-custom-head">
          <span>Custom fields</span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => onCustomRowsChange([...customRows, { field: '', col: null }])}
          >
            + Add custom field
          </button>
        </div>
        {customRows.length === 0 && (
          <p className="hint">Optional: map extra columns (e.g. class, department) to store them as custom fields.</p>
        )}
        {customRows.map((row, idx) => (
          <div key={idx} className="mapper-custom-row">
            <input
              type="text"
              placeholder="Field name (e.g. class)"
              value={row.field}
              onChange={(e) => setCustomRow(idx, { field: e.target.value })}
            />
            <HeaderSelect headers={headers} value={row.col} onChange={(v) => setCustomRow(idx, { col: v })} />
            <button
              type="button"
              className="icon-btn"
              aria-label="Remove custom field mapping"
              onClick={() => onCustomRowsChange(customRows.filter((_, i) => i !== idx))}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
