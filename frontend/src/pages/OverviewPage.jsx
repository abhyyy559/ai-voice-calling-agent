import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { analyticsApi } from '../api.js';
import StatusBadge from '../components/StatusBadge.jsx';

const LATENCY_TARGET_MS = 900;

function fmtDuration(seconds) {
  if (seconds == null || Number.isNaN(Number(seconds))) return '—';
  const s = Math.max(0, Math.round(Number(seconds)));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function fmtDateTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function StatCard({ label, value, unit, foot }) {
  return (
    <div className="stat-card">
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {foot && <div className="stat-card-foot">{foot}</div>}
    </div>
  );
}

/** Overview — org-wide analytics landing page (Vapi/Retell-style home). */
export default function OverviewPage() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    setError(null);
    analyticsApi
      .summary()
      .then(setSummary)
      .catch((e) => setError(e.message || String(e)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  const medianLatency =
    summary && summary.median_e2e_ms != null
      ? Math.round(summary.median_e2e_ms)
      : summary && summary.avg_e2e_ms != null
        ? Math.round(summary.avg_e2e_ms)
        : null;
  const latencyOnTarget = medianLatency != null && medianLatency <= LATENCY_TARGET_MS;
  const maxDayCount = summary ? Math.max(1, ...summary.calls_last_7d.map((d) => d.count)) : 1;

  return (
    <div>
      <div className="page-head">
        <div>
          <h2 className="page-title">Overview</h2>
          <p className="page-sub">
            How your voice agents are performing — volume, success rate, end-to-end latency and captured data.
          </p>
        </div>
        <div className="head-actions">
          <Link to="/agents/new" className="btn btn-primary">
            + New Agent
          </Link>
        </div>
      </div>

      {error && (
        <div className="banner banner-error">
          {error}{' '}
          <button type="button" className="btn btn-secondary btn-sm" onClick={load}>
            Retry
          </button>
        </div>
      )}

      {loading && !summary && (
        <div className="loading-page">
          <span className="spinner" /> Loading analytics…
        </div>
      )}

      {summary && (
        <>
          <div className="stat-grid">
            <StatCard label="Total Calls" value={summary.total_calls} foot={<span>{summary.completed_calls} completed</span>} />
            <StatCard
              label="Success Rate"
              value={summary.success_rate_pct}
              unit="%"
              foot={<span>completed ÷ all calls</span>}
            />
            <StatCard
              label="Median Latency"
              value={medianLatency != null ? medianLatency.toLocaleString() : '—'}
              unit={medianLatency != null ? 'ms' : undefined}
              foot={
                <span
                  className={`target-badge${latencyOnTarget || medianLatency == null ? '' : ' miss'}`}
                  title={`End-to-end turn latency target: ≤ ${LATENCY_TARGET_MS} ms`}
                >
                  {medianLatency == null ? (
                    'target ≤ 900ms'
                  ) : latencyOnTarget ? (
                    <>
                      ✓ on target · ≤900ms
                    </>
                  ) : (
                    <>▲ over target · ≤900ms</>
                  )}
                </span>
              }
            />
            <StatCard label="Fields Captured" value={summary.total_extracted_fields} foot={<span>structured values extracted</span>} />
          </div>

          <div className="overview-grid">
            <div className="card">
              <h3 className="card-title">Calls — last 7 days</h3>
              <div className="bar-chart" role="img" aria-label="Bar chart of calls per day over the last seven days">
                {summary.calls_last_7d.map((day) => {
                  const h = day.count === 0 ? 0 : Math.max(4, Math.round((day.count / maxDayCount) * 100));
                  const date = new Date(`${day.date}T00:00:00`);
                  const label = Number.isNaN(date.getTime())
                    ? day.date.slice(5)
                    : date.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric' });
                  return (
                    <div key={day.date} className="bar-col" title={`${day.date}: ${day.count} calls`}>
                      <span className="bar-count">{day.count > 0 ? day.count : ''}</span>
                      <div className="bar-track">
                        <div className={`bar-fill${day.count === 0 ? ' zero' : ''}`} style={{ height: `${h}%` }} />
                      </div>
                      <span className="bar-date">{label}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="card flush">
              <div className="card-head">
                <h3 className="card-title">Recent calls</h3>
              </div>
              <div className="table-wrap">
                <table className="data-table mini-table">
                  <thead>
                    <tr>
                      <th>Call</th>
                      <th>Status</th>
                      <th>Agent</th>
                      <th className="nowrap">When</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.recent_calls.length === 0 && (
                      <tr>
                        <td colSpan={4} className="table-state">
                          No calls yet — run one from the{' '}
                          <Link to="/playground">Playground</Link>.
                        </td>
                      </tr>
                    )}
                    {summary.recent_calls.map((call) => (
                      <tr key={call.id} className="clickable" onClick={() => navigate(`/calls/${call.id}`)}>
                        <td>
                          <Link to={`/calls/${call.id}`} onClick={(e) => e.stopPropagation()}>
                            #{call.id}
                          </Link>
                        </td>
                        <td>
                          <StatusBadge status={call.status} />
                        </td>
                        <td>{call.agent_name || <span className="text-muted">—</span>}</td>
                        <td className="nowrap">
                          <span title={fmtDateTime(call.started_at)}>{fmtDateTime(call.started_at)}</span>
                          {call.duration_seconds != null && (
                            <span className="text-muted"> · {fmtDuration(call.duration_seconds)}</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {summary.recent_calls.length > 0 && (
                <div className="pagination" style={{ borderTop: 'none' }}>
                  <Link to="/calls" className="btn btn-ghost btn-sm">
                    View all calls →
                  </Link>
                </div>
              )}
            </div>
          </div>

          <p className="hint" style={{ marginTop: 16 }}>
            Latency is the median end-to-end turn time measured across every transcript turn. p95:{' '}
            {summary.p95_e2e_ms != null ? `${Math.round(summary.p95_e2e_ms).toLocaleString()} ms` : '—'} · avg:{' '}
            {summary.avg_e2e_ms != null ? `${Math.round(summary.avg_e2e_ms).toLocaleString()} ms` : '—'}.
          </p>
        </>
      )}
    </div>
  );
}
