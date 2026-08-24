import React, { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import StatusBadge from '../components/StatusBadge.jsx';

const PAGE_SIZE = 25;
const LATENCY_TARGET_MS = 900;

function fmtDuration(seconds) {
  if (seconds == null || Number.isNaN(Number(seconds))) return '—';
  const s = Math.max(0, Math.round(Number(seconds)));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

/** "2m ago" style relative stamp with absolute time in the tooltip. */
function relTime(value) {
  if (!value) return { label: '—', full: '' };
  const then = new Date(value).getTime();
  if (Number.isNaN(then)) return { label: String(value), full: String(value) };
  const diffSec = Math.max(0, Math.round((Date.now() - then) / 1000));
  let label;
  if (diffSec < 45) label = 'just now';
  else if (diffSec < 3600) label = `${Math.round(diffSec / 60)}m ago`;
  else if (diffSec < 86400) label = `${Math.round(diffSec / 3600)}h ago`;
  else if (diffSec < 86400 * 30) label = `${Math.round(diffSec / 86400)}d ago`;
  else label = new Date(value).toLocaleDateString();
  return {
    label,
    full: new Date(value).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }),
  };
}

function KindIcon({ kind }) {
  if (kind === 'playground' || kind === 'web') {
    return (
      <span className="kind-icon web" title="Web test (Playground)" aria-label="Web call">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <rect x="2.5" y="4" width="19" height="13" rx="2.5" />
          <path d="M8 21h8M12 17v4" />
        </svg>
      </span>
    );
  }
  return (
    <span className="kind-icon" title="Phone call" aria-label="Phone call">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />
      </svg>
    </span>
  );
}

/** Call History — Vapi-style index of every org call, paginated client-side. */
export default function CallsIndexPage() {
  const navigate = useNavigate();
  const [calls, setCalls] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  function load() {
    setLoading(true);
    setError(null);
    api
      .listCalls({ limit: 500 })
      .then((rows) => setCalls(Array.isArray(rows) ? rows : []))
      .catch((e) => setError(e.message || String(e)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  const pageCount = calls ? Math.max(1, Math.ceil(calls.length / PAGE_SIZE)) : 1;
  const safePage = Math.min(page, pageCount);
  const pageRows = useMemo(
    () => (calls ? calls.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE) : []),
    [calls, safePage]
  );

  useEffect(() => {
    setPage(1);
  }, [calls]);

  return (
    <div>
      <div className="page-head">
        <div>
          <h2 className="page-title">Call history</h2>
          <p className="page-sub">Every call this organization has placed or simulated — newest first.</p>
        </div>
        <button type="button" className="btn btn-secondary btn-sm" onClick={load} disabled={loading}>
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="banner banner-error">
          {error}{' '}
          <button type="button" className="btn btn-secondary btn-sm" onClick={load}>
            Retry
          </button>
        </div>
      )}

      <div className="card flush">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Call</th>
                <th>Status</th>
                <th>Type</th>
                <th>Agent</th>
                <th>Contact</th>
                <th className="nowrap">Duration</th>
                <th className="nowrap">Latency e2e</th>
                <th className="nowrap">Started</th>
              </tr>
            </thead>
            <tbody>
              {!loading && !error && calls && calls.length === 0 && (
                <tr>
                  <td colSpan={8} className="table-state">
                    No calls yet — run one from the <Link to="/playground">Playground</Link> or launch a{' '}
                    <Link to="/campaigns">campaign</Link>.
                  </td>
                </tr>
              )}
              {pageRows.map((call) => {
                const started = relTime(call.started_at || call.created_at);
                const latency =
                  call.avg_e2e_ms != null ? `${Math.round(call.avg_e2e_ms).toLocaleString()} ms` : null;
                return (
                  <tr key={call.id} className="clickable" onClick={() => navigate(`/calls/${call.id}`)}>
                    <td className="cell-strong nowrap">#{call.id}</td>
                    <td>
                      <StatusBadge status={call.status} />
                      {call.flagged_for_human && (
                        <span className="badge badge-red-outline" style={{ marginLeft: 6 }} title="Flagged for human review">
                          flagged
                        </span>
                      )}
                    </td>
                    <td>
                      <KindIcon kind={call.kind} />
                    </td>
                    <td>{call.agent_name || <span className="text-muted">—</span>}</td>
                    <td>
                      {call.contact_name ? (
                        <>
                          {call.contact_name}
                          {call.contact_phone && <span className="text-muted"> · {call.contact_phone}</span>}
                        </>
                      ) : (
                        <span className="text-muted">{call.kind === 'playground' ? 'Browser test' : '—'}</span>
                      )}
                    </td>
                    <td className="nowrap">{fmtDuration(call.duration_seconds)}</td>
                    <td className="nowrap">
                      {latency ? (
                        <span
                          className={`latency-pill${call.avg_e2e_ms > LATENCY_TARGET_MS ? ' slow' : ''}`}
                          title="Average end-to-end turn latency across this call"
                        >
                          {latency}
                        </span>
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td className="nowrap rel-time" title={started.full}>
                      {started.label}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {calls && calls.length > 0 && (
          <div className="pagination">
            <span className="page-info">
              Showing {(safePage - 1) * PAGE_SIZE + 1}–{Math.min(safePage * PAGE_SIZE, calls.length)} of {calls.length}{' '}
              calls
            </span>
            <div className="page-btns">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={safePage <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                ← Prev
              </button>
              <span className="page-num">
                Page {safePage} of {pageCount}
              </span>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                disabled={safePage >= pageCount}
                onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
