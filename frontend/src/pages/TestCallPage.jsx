import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api.js';
import StatusBadge from '../components/StatusBadge.jsx';

export default function TestCallPage() {
  const [domains, setDomains] = useState([]);
  const [domainsError, setDomainsError] = useState(null);
  const [domainId, setDomainId] = useState('');
  const [to, setTo] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api
      .listDomainConfigs()
      .then((list) => {
        setDomains(Array.isArray(list) ? list : []);
        setDomainsError(null);
      })
      .catch((e) => setDomainsError(e.message));
  }, []);

  async function placeCall() {
    setBusy(true);
    setError(null);
    setResult(null);
    const payload = { domain_config_id: domainId };
    const trimmed = to.trim();
    if (trimmed) payload.to = trimmed;
    try {
      const res = await api.placeTestCall(payload);
      setResult(res || {});
    } catch (e) {
      setError(e.message || 'Could not place test call.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="narrow">
      <div className="page-head">
        <div>
          <h2 className="page-title">Test call</h2>
          <p className="page-sub">
            Place a single call using a call domain config to verify the voice pipeline end-to-end.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="field">
          <label htmlFor="tc-domain">Call domain</label>
          <select id="tc-domain" value={domainId} onChange={(e) => setDomainId(e.target.value)}>
            <option value="">Select a call domain…</option>
            {domains.map((d) => (
              <option key={d.id} value={d.id}>
                {d.display_name || d.name}
                {d.version != null ? ` (v${d.version})` : ''}
              </option>
            ))}
          </select>
          {domainsError && <p className="hint hint-error">{domainsError}</p>}
          {!domainsError && domains.length === 0 && (
            <p className="hint">No domain configs available yet — add one first (see /domain-configs).</p>
          )}
        </div>

        <div className="field">
          <label htmlFor="tc-to">Call destination (optional)</label>
          <input
            id="tc-to"
            type="tel"
            value={to}
            placeholder="Uses the configured test number if left blank"
            onChange={(e) => setTo(e.target.value)}
          />
          <p className="hint">
            Leave blank to dial the configured sandbox/test number. Only use numbers you are authorized to call.
          </p>
        </div>

        {error && <div className="banner banner-error">{error}</div>}

        <div className="form-actions">
          <button className="btn btn-primary" disabled={busy || !domainId} onClick={placeCall}>
            {busy ? 'Placing call…' : 'Place test call'}
          </button>
        </div>

        {result && (
          <div className="banner banner-success">
            <strong>Test call placed.</strong>
            <div className="result-grid">
              <span>
                Status: <StatusBadge status={result.status} />
              </span>
              {result.call_id != null && (
                <span>
                  Call ID: <code>{String(result.call_id)}</code>
                </span>
              )}
              {result.provider_call_id && (
                <span>
                  Provider call ID: <code>{String(result.provider_call_id)}</code>
                </span>
              )}
            </div>
            {result.call_id != null && (
              <p className="result-link">
                <Link to={`/calls/${result.call_id}`}>View live call detail →</Link>
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
