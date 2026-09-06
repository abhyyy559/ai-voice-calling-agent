import React from 'react';
import StatusBadge from './StatusBadge.jsx';

/** Per-contact accordion for a DryRunReport. Includes a client-side CSV download. */
export default function DryRunReport({ report }) {
  if (!report) return null;
  const results = report.results || [];

  function downloadCsv() {
    const header = ['contact_id', 'name', 'phone', 'persona', 'status', 'outcome', 'turns', 'fields'];
    const lines = [header.join(',')];
    for (const r of results) {
      const fields = (r.extracted_fields || [])
        .map((f) => `${f.field_name}=${f.field_value}`)
        .join('; ')
        .replace(/"/g, '""');
      lines.push(
        [r.contact_id, `"${r.name || ''}"`, r.phone, r.persona, r.status, `"${r.outcome || ''}"`, r.turns, `"${fields}"`].join(',')
      );
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dry-run-campaign-${report.campaign_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="card">
      <div className="page-head">
        <div>
          <h3 className="page-title">Dry-run report (SIMULATION — no calls placed)</h3>
          <p className="page-sub">
            {report.contacts_run} of {report.contacts_total} contacts simulated
            {report.persona ? ` · persona: ${report.persona}` : ' · personas: round-robin'}.
          </p>
        </div>
        <div className="form-actions">
          <button className="btn btn-secondary btn-sm" onClick={downloadCsv}>
            Download CSV
          </button>
        </div>
      </div>
      {results.map((r) => (
        <details key={r.contact_id} className="card">
          <summary>
            {r.name} · {r.phone} · <StatusBadge status={r.status} /> · {r.persona} · {r.turns} turns
          </summary>
          <h4>Transcript</h4>
          {(r.transcript || []).map((t, i) => (
            <p key={i}>
              <strong>{t.role === 'agent' ? 'Agent' : 'Caller'}:</strong> {t.text}
            </p>
          ))}
          <h4>Extracted fields</h4>
          {(r.extracted_fields || []).length === 0 && <p className="hint">No fields recorded.</p>}
          <ul>
            {(r.extracted_fields || []).map((f, i) => (
              <li key={i}>
                <code>{f.field_name}</code>: {String(f.field_value)} ({Math.round((f.confidence || 0) * 100)}%)
              </li>
            ))}
          </ul>
          {r.outcome && (
            <p>
              Outcome: <code>{r.outcome}</code>
            </p>
          )}
        </details>
      ))}
    </div>
  );
}
