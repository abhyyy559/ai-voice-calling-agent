import React from 'react';

/**
 * Ordered question-flow editor.
 *
 * `steps` is an array of { question, expectedField }. The numeric `step`
 * required by the API is assigned from array order at serialize time, so
 * reordering here is always safe.
 */
export default function QuestionFlowEditor({ steps, onChange, error }) {
  const rows = Array.isArray(steps) ? steps : [];

  function update(index, patch) {
    const next = rows.map((s, i) => (i === index ? { ...s, ...patch } : s));
    onChange(next);
  }

  function move(index, delta) {
    const target = index + delta;
    if (target < 0 || target >= rows.length) return;
    const next = [...rows];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  }

  function remove(index) {
    onChange(rows.filter((_, i) => i !== index));
  }

  function add() {
    onChange([...rows, { question: '', expectedField: '' }]);
  }

  return (
    <div className="qfe">
      {error && <div className="banner banner-error">{error}</div>}
      {!rows.length ? (
        <div className="empty-state qfe-empty">
          No questions yet. Add the questions the agent should ask during the call, in order.
        </div>
      ) : (
        <ol className="qfe-list">
          {rows.map((step, i) => (
            <li key={i} className="qfe-row">
              <div className="qfe-num" title={`Step ${i + 1}`}>
                {i + 1}
              </div>
              <div className="qfe-fields">
                <div className="field qfe-field">
                  <label htmlFor={`qfe-q-${i}`}>
                    Question <span className="req-star">*</span>
                  </label>
                  <input
                    id={`qfe-q-${i}`}
                    type="text"
                    value={step.question || ''}
                    placeholder="e.g. May I know the reason for missing classes today?"
                    onChange={(e) => update(i, { question: e.target.value })}
                  />
                </div>
                <div className="field qfe-field">
                  <label htmlFor={`qfe-hint-${i}`}>Expected field hint</label>
                  <input
                    id={`qfe-hint-${i}`}
                    type="text"
                    value={step.expectedField || ''}
                    placeholder="e.g. reason_for_absence"
                    onChange={(e) => update(i, { expectedField: e.target.value })}
                  />
                  <p className="hint">Which extraction field this question feeds — helps the agent record answers accurately.</p>
                </div>
              </div>
              <div className="qfe-actions" aria-label={`Actions for step ${i + 1}`}>
                <button
                  type="button"
                  className="icon-btn"
                  aria-label={`Move step ${i + 1} up`}
                  disabled={i === 0}
                  onClick={() => move(i, -1)}
                >
                  ↑
                </button>
                <button
                  type="button"
                  className="icon-btn"
                  aria-label={`Move step ${i + 1} down`}
                  disabled={i === rows.length - 1}
                  onClick={() => move(i, 1)}
                >
                  ↓
                </button>
                <button
                  type="button"
                  className="icon-btn qfe-remove"
                  aria-label={`Remove step ${i + 1}`}
                  onClick={() => remove(i)}
                >
                  ×
                </button>
              </div>
            </li>
          ))}
        </ol>
      )}
      <button type="button" className="btn btn-secondary btn-sm" onClick={add}>
        + Add question
      </button>
      <p className="hint">
        Questions are asked top to bottom and renumbered automatically on save. The agent asks each question until it
        gets a usable answer (up to its retry limit), then moves on.
      </p>
    </div>
  );
}
