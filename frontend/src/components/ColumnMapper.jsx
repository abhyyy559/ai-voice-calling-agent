import React from 'react';

export const EMPTY_MAPPING = { name_col: null, phone_col: null, id_col: null, consent_col: null };

/**
 * Parse the header (first) row of a delimited text file (CSV/TSV).
 * Detects the delimiter among , ; tab | and honors quoted cells. Returns string[] of column names.
 */
export function parseCsvHeader(text) {
  const clean = String(text).replace(/^\uFEFF/, '');
  const firstLine = clean.split(/\r?\n/, 1)[0] || '';
  const delim = detectDelimiter(firstLine);
  return parseHeaderRow(clean, delim);
}

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

function parseHeaderRow(text, delim) {
  const cells = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        if (text[i + 1] === '"') {
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
      cells.push(cur.trim());
      cur = '';
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i++;
      break;
    } else {
      cur += ch;
    }
  }
  if (cur.trim() !== '' || cells.length > 0) cells.push(cur.trim());
  return cells;
}

/** Best-effort auto-mapping of recognizable columns. */
export function guessMapping(headers) {
  if (!Array.isArray(headers)) return { ...EMPTY_MAPPING };
  const find = (test) => headers.find((h) => test(String(h).toLowerCase())) || null;
  return {
    name_col: find((h) => /(^|[\s_\-.])name($|[\s_\-.])|fullname|full_name|student/.test(h)),
    phone_col: find((h) => /phone|mobile|number|contact|whatsapp/.test(h) && !/id$/.test(h)),
    id_col: find((h) => /(^|[\s_\-.])(id|roll|roll_?no|roll_?number|enrollment|external[\s_\-]?id)($|[\s_\-.])/.test(h) || /(^|[\s_\-.])id$/.test(h)),
    consent_col: find((h) => /consent|permission|opt[\s_\-]?in/.test(h)),
  };
}

function ColumnSelect({ headers, value, onChange, required }) {
  if (headers && headers.length > 0) {
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
  return (
    <input
      type="text"
      value={value || ''}
      placeholder={required ? 'Exact column header (required)' : 'Exact column header'}
      onChange={(e) => onChange(e.target.value || null)}
    />
  );
}

const TARGETS = [
  { key: 'name_col', label: 'Contact name', required: false },
  { key: 'phone_col', label: 'Phone number', required: true },
  { key: 'id_col', label: 'External ID (roll no., etc.)', required: false },
  { key: 'consent_col', label: 'Consent', required: false },
];

/**
 * Column mapping UI.
 * headers: string[] when known (CSV parsed client-side), or null/[] for XLSX (manual entry).
 */
export default function ColumnMapper({
  headers,
  mapping,
  onMappingChange,
  customRows,
  onCustomRowsChange,
  consentDefault,
  onConsentDefaultChange,
}) {
  const known = Array.isArray(headers) && headers.length > 0;
  const setField = (key, val) => onMappingChange({ ...mapping, [key]: val });

  const setCustomRow = (idx, patch) => {
    const next = customRows.map((r, i) => (i === idx ? { ...r, ...patch } : r));
    onCustomRowsChange(next);
  };

  return (
    <div className="mapper">
      {known ? (
        <p className="hint">
          Detected {headers.length} columns. Confirm the mapping below — the highlighted column names come straight from
          your file's header row.
        </p>
      ) : (
        <div className="banner banner-info">
          Column headers could not be previewed for this file type (XLSX). Type the exact column header names from your
          file for each field you want to import.
        </div>
      )}

      <div className="mapper-rows">
        {TARGETS.map((t) => (
          <div key={t.key} className="mapper-row">
            <label className="mapper-label">
              {t.label}
              {t.required ? <span className="req-star"> *</span> : null}
            </label>
            <div className="mapper-control">
              <ColumnSelect
                headers={known ? headers : null}
                value={mapping[t.key]}
                onChange={(v) => setField(t.key, v)}
                required={t.required}
              />
            </div>
          </div>
        ))}
      </div>

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
            <ColumnSelect
              headers={known ? headers : null}
              value={row.col}
              onChange={(v) => setCustomRow(idx, { col: v })}
              required={false}
            />
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

      <label className="check-row">
        <input
          type="checkbox"
          checked={consentDefault}
          onChange={(e) => onConsentDefaultChange(e.target.checked)}
        />
        <span>
          Treat contacts as having consent if the file has no consent column or a row is blank
          <span className="hint"> (required for compliance — leave unchecked if unsure)</span>
        </span>
      </label>
    </div>
  );
}
