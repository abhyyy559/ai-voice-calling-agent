import React from 'react';

export const FIELD_TYPES = [
  { value: 'string', label: 'Text' },
  { value: 'date', label: 'Date' },
  { value: 'boolean', label: 'Yes / No' },
  { value: 'number', label: 'Number' },
];

/**
 * Extraction-schema editor.
 *
 * `rows` is an array of { name, type, description, required, threshold } in
 * display order. Serialization converts this to the API's
 * { fieldName: { type, description, validation, confidence_threshold } } map.
 */
export default function ExtractionSchemaEditor({ rows, onChange, error }) {
  const items = Array.isArray(rows) ? rows : [];

  function update(index, patch) {
    onChange(items.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  }

  function remove(index) {
    onChange(items.filter((_, i) => i !== index));
  }

  function add() {
    onChange([
      ...items,
      { name: '', type: 'string', description: '', required: false, threshold: 0.6 },
    ]);
  }

  return (
    <div className="ese">
      {error && <div className="banner banner-error">{error}</div>}
      {!items.length ? (
        <div className="empty-state ese-empty">
          No fields yet. Add the structured facts the agent should collect during the call (e.g. reason, date).
        </div>
      ) : (
        <div className="table-wrap">
          <table className="data-table ese-table">
            <thead>
              <tr>
                <th>Field name</th>
                <th>Type</th>
                <th>What to listen for</th>
                <th>Required</th>
                <th style={{ width: '150px' }}>Confidence min.</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {items.map((row, i) => (
                <tr key={i}>
                  <td>
                    <input
                      type="text"
                      aria-label={`Field ${i + 1} name`}
                      value={row.name}
                      className="ese-name-input"
                      placeholder="e.g. expected_return_date"
                      onChange={(e) => update(i, { name: e.target.value })}
                    />
                    {items.some((r, j) => j !== i && r.name.trim() && r.name.trim() === row.name.trim()) && (
                      <p className="hint hint-error">Duplicate field name.</p>
                    )}
                  </td>
                  <td>
                    <select
                      aria-label={`Field ${i + 1} type`}
                      value={row.type}
                      onChange={(e) => update(i, { type: e.target.value })}
                    >
                      {FIELD_TYPES.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td>
                    <input
                      type="text"
                      aria-label={`Field ${i + 1} description`}
                      value={row.description}
                      placeholder="e.g. The day the student says they will return"
                      onChange={(e) => update(i, { description: e.target.value })}
                    />
                  </td>
                  <td>
                    <label className="check-row ese-check">
                      <input
                        type="checkbox"
                        checked={!!row.required}
                        aria-label={`Field ${i + 1} required`}
                        onChange={(e) => update(i, { required: e.target.checked })}
                      />
                      <span>Must have</span>
                    </label>
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.05"
                      aria-label={`Field ${i + 1} confidence threshold`}
                      value={row.threshold}
                      onChange={(e) => {
                        const v = Number(e.target.value);
                        update(i, { threshold: Number.isNaN(v) ? '' : v });
                      }}
                    />
                    <p className="hint">0–1. Below this, the answer is flagged instead of trusted.</p>
                  </td>
                  <td className="nowrap">
                    <button
                      type="button"
                      className="icon-btn qfe-remove"
                      aria-label={`Remove field ${row.name || i + 1}`}
                      onClick={() => remove(i)}
                    >
                      ×
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <button type="button" className="btn btn-secondary btn-sm" onClick={add}>
        + Add field
      </button>
      <p className="hint">
        These are the facts written into the results sheet after each call. The agent never invents a value — if it
        cannot capture a field confidently it marks the call for human review instead.
      </p>
    </div>
  );
}

/** Array rows -> API map shape. */
export function serializeExtractionSchema(rows) {
  const schema = {};
  (rows || []).forEach((r) => {
    const name = String(r.name || '').trim();
    if (!name) return;
    schema[name] = {
      type: r.type || 'string',
      description: String(r.description || '').trim(),
      validation: r.required ? 'required' : 'optional',
      confidence_threshold:
        typeof r.threshold === 'number' && !Number.isNaN(r.threshold) ? r.threshold : 0.6,
    };
  });
  return schema;
}

/** API map shape -> array rows. */
export function deserializeExtractionSchema(schema) {
  if (!schema || typeof schema !== 'object') return [];
  return Object.entries(schema).map(([name, f]) => ({
    name,
    type: f && f.type ? f.type : 'string',
    description: f && f.description ? f.description : '',
    required: Boolean(f && f.validation === 'required'),
    threshold: f && typeof f.confidence_threshold === 'number' ? f.confidence_threshold : 0.6,
  }));
}
