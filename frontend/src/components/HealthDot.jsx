import React from 'react';

/**
 * Small colored status dot with a label.
 * state: 'ok' | 'down' | 'unknown'
 */
export default function HealthDot({ label, state = 'unknown', note, title }) {
  return (
    <div className={`health-dot health-${state}`} title={title || (note ? `${label}: ${note}` : label)}>
      <span className="health-dot-circle" aria-hidden="true" />
      <div className="health-dot-text">
        <span className="health-dot-label">{label}</span>
        {note && <span className="health-dot-note">{note}</span>}
      </div>
      <span className="visually-hidden">{state === 'ok' ? 'healthy' : state === 'down' ? 'down' : 'unknown'}</span>
    </div>
  );
}

/** Map a boolean-ish value to a HealthDot state. */
export function boolToState(v) {
  if (v === true) return 'ok';
  if (v === false) return 'down';
  return 'unknown';
}
