import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { API_BASE } from '../api.js';
import usePoll from '../hooks/usePoll.js';
import StatusBadge from '../components/StatusBadge.jsx';

const TERMINAL_STATUSES = new Set(['completed', 'failed', 'no_answer', 'busy', 'canceled', 'cancelled', 'invalid']);

const AGENT_SPEAKERS = new Set(['agent', 'ai', 'bot', 'assistant', 'system', 'voice_agent']);

function speakerIsAgent(speaker) {
  return AGENT_SPEAKERS.has(String(speaker || '').toLowerCase());
}

function fmtDateTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function fmtDuration(seconds) {
  if (seconds == null || Number.isNaN(Number(seconds))) return '—';
  const s = Math.max(0, Math.round(Number(seconds)));
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, '0')}`;
}

function fmtClock(value) {
  if (value == null) return null;
  if (typeof value === 'number' || /^\d+(\.\d+)?$/.test(String(value))) {
    const s = Math.max(0, Math.round(Number(value)));
    return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  }
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function fmtNum(value, maxFractionDigits = 4) {
  const n = Number(value);
  if (value == null || Number.isNaN(n)) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: maxFractionDigits });
}

function titleCase(s) {
  return String(s)
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (ch) => ch.toUpperCase());
}

function ConfidenceBar({ value }) {
  if (value == null || value === '' || Number.isNaN(Number(value))) {
    return <span className="text-muted">—</span>;
  }
  const num = Number(value);
  const pct = num <= 1 ? num * 100 : num;
  const clamped = Math.min(100, Math.max(0, pct));
  const cls = clamped >= 80 ? 'high' : clamped >= 50 ? 'mid' : 'low';
  return (
    <div className="conf">
      <div className={`conf-bar conf-${cls}`}>
        <div className="conf-fill" style={{ width: `${clamped}%` }} />
      </div>
      <span className="conf-pct">{Math.round(clamped)}%</span>
    </div>
  );
}

function StatRow({ items }) {
  if (!items.length) return null;
  return (
    <div className="stat-row">
      {items.map(([label, value]) => (
        <div key={label} className="stat-chip">
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
      ))}
    </div>
  );
}

function resolveUrl(url) {
  if (!url) return null;
  if (/^https?:\/\//i.test(url)) return url;
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`;
}

export default function CallDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [isLive, setIsLive] = useState(true);

  const { data: call, error, loading, reload } = usePoll(`/api/calls/${id}`, 3000, isLive);

  useEffect(() => {
    if (call && call.status && TERMINAL_STATUSES.has(call.status)) setIsLive(false);
  }, [call]);

  if (error && !call) {
    return (
      <div>
        <button className="btn btn-ghost" onClick={() => navigate(-1)}>
          ← Back
        </button>
        <div className="banner banner-error">
          {error}{' '}
          <button className="btn btn-secondary btn-sm" onClick={reload}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading && !call) {
    return (
      <div className="loading-page">
        <span className="spinner" /> Loading call…
      </div>
    );
  }

  if (!call) return null;

  const live = call.status && !TERMINAL_STATUSES.has(call.status);
  const transcript = call.transcript || [];
  const extracted = call.extracted_fields || [];
  const latencyEntries = call.latency ? Object.entries(call.latency) : [];
  const costEntries = call.cost ? Object.entries(call.cost) : [];
  const costSorted = costEntries
    .filter(([k]) => k !== 'total')
    .concat(costEntries.filter(([k]) => k === 'total'));
  const recordingUrl = resolveUrl(call.recording_url);

  return (
    <div className="call-detail">
      <button className="btn btn-ghost" onClick={() => navigate(-1)}>
        ← Back
      </button>

      <div className="page-head">
        <div>
          <div className="title-row">
            <h2 className="page-title">Call {call.id}</h2>
            <StatusBadge status={call.status} />
            {live && (
              <span className="live-indicator">
                <span className="live-dot" /> Live — refreshing every 3 seconds
              </span>
            )}
            {call.flagged_for_human ? <StatusBadge status="flagged" /> : null}
          </div>
          {call.outcome && (
            <p className="meta-line">
              <span>
                <strong>Outcome:</strong> <span className="chip">{String(call.outcome)}</span>
              </span>
            </p>
          )}
          <p className="meta-line">
            <span>
              <strong>Started:</strong> {fmtDateTime(call.started_at)}
            </span>
            {call.ended_at && (
              <span>
                <strong>Ended:</strong> {fmtDateTime(call.ended_at)}
              </span>
            )}
            <span>
              <strong>Duration:</strong> {fmtDuration(call.duration_seconds)}
            </span>
          </p>
        </div>
      </div>

      {error && <div className="banner banner-error">{error}</div>}

      {call.summary ? (
        <div className="card">
          <h3 className="card-title">AI summary</h3>
          <p className="summary-text">{call.summary}</p>
        </div>
      ) : (
        <div className="card">
          <h3 className="card-title">AI summary</h3>
          <p className="hint">No summary yet{live ? ' — appears when the call completes.' : '.'}</p>
        </div>
      )}

      {latencyEntries.length > 0 && (
        <div className="card">
          <h3 className="card-title">Latency</h3>
          <StatRow items={latencyEntries.map(([k, v]) => [titleCase(k).replace(/ Ms$/i, ' (ms)'), `${fmtNum(v, 0)} ms`])} />
        </div>
      )}

      {costSorted.length > 0 && (
        <div className="card">
          <h3 className="card-title">Cost breakdown</h3>
          <StatRow items={costSorted.map(([k, v]) => [titleCase(k), fmtNum(v, 4)])} />
        </div>
      )}

      {recordingUrl && (
        <div className="card">
          <h3 className="card-title">Recording</h3>
          <audio controls preload="none" src={recordingUrl} />
          <p className="hint">
            <a href={recordingUrl} target="_blank" rel="noreferrer">
              Open recording in a new tab
            </a>
          </p>
        </div>
      )}

      <div className="card">
        <h3 className="card-title">Extracted fields</h3>
        {extracted.length === 0 ? (
          <p className="hint">No structured fields extracted{live ? ' yet.' : ' for this call.'}</p>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Value</th>
                  <th style={{ width: '180px' }}>Confidence</th>
                  <th>Source turn</th>
                </tr>
              </thead>
              <tbody>
                {extracted.map((f, i) => (
                  <tr key={f.field_name != null ? `${f.field_name}-${i}` : i}>
                    <td className="cell-strong">{f.field_name}</td>
                    <td>{f.field_value != null ? String(f.field_value) : '—'}</td>
                    <td>
                      <ConfidenceBar value={f.confidence} />
                    </td>
                    <td>
                      {f.source_turn_index != null ? (
                        <button
                          type="button"
                          className="link-btn"
                          onClick={() => {
                            const el = document.getElementById(`turn-${f.source_turn_index}`);
                            if (el) {
                              el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                              el.classList.add('flash');
                              setTimeout(() => el.classList.remove('flash'), 1200);
                            }
                          }}
                        >
                          Turn #{f.source_turn_index}
                        </button>
                      ) : (
                        '—'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">Transcript</h3>
        {transcript.length === 0 ? (
          <p className="hint">No transcript{live ? ' yet — turns appear here as the call progresses.' : ' available.'}</p>
        ) : (
          <div className="transcript">
            {transcript.map((t, i) => {
              const agent = speakerIsAgent(t.speaker);
              const clock = fmtClock(t.timestamp);
              return (
                <div
                  key={t.turn_index != null ? `turn-${t.turn_index}` : i}
                  id={`turn-${t.turn_index != null ? t.turn_index : i}`}
                  className={`bubble-row ${agent ? 'agent' : 'caller'}`}
                >
                  <div className={`bubble ${agent ? 'bubble-agent' : 'bubble-caller'}`}>
                    <div className="bubble-meta">
                      <span className="bubble-speaker">{agent ? 'Agent' : titleCase(t.speaker || 'Caller')}</span>
                      {clock && <span className="bubble-time">{clock}</span>}
                    </div>
                    <div className="bubble-text">{t.text}</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
