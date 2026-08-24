import React from 'react';

const ESCALATION_ACTIONS = [
  { value: '', label: 'Plain rule (text only)' },
  { value: 'transfer', label: 'Transfer to human' },
  { value: 'flag', label: 'Flag for review' },
  { value: 'end_call', label: 'End the call' },
];

/**
 * Shared "Company Context" editor: organization facts, system prompt,
 * mandatory AI disclosure and escalation rules.
 *
 * Used by both the /agents/new builder wizard (step 2) and the agent
 * workspace (/agents/:id, Context tab).
 *
 * value:   { contextRows: [{key,value}], systemPrompt, disclosureScript,
 *            escalationRules: [{trigger, action}] }
 * onChange(patch): merge `patch` into the parent config object.
 * errors:  { company_context?, system_prompt?, disclosure_script?,
 *            escalation_rules? } — per-field message strings.
 */
export default function ContextFieldsEditor({ value, onChange, errors = {} }) {
  const config = {
    contextRows: [],
    systemPrompt: '',
    disclosureScript: '',
    escalationRules: [],
    ...(value || {}),
  };

  function patch(part) {
    onChange({ ...config, ...part });
  }

  return (
    <div>
      <div className="field">
        <label>Facts about your organization</label>
        {!config.contextRows.length && (
          <p className="hint">No facts yet — add things like institute name, course details, office hours.</p>
        )}
        {(config.contextRows || []).map((row, i) => (
          <div className="context-row" key={i}>
            <input
              type="text"
              aria-label={`Fact ${i + 1} label`}
              placeholder="Label, e.g. institute_name"
              value={row.key}
              onChange={(e) =>
                patch({
                  contextRows: config.contextRows.map((r, j) => (j === i ? { ...r, key: e.target.value } : r)),
                })
              }
            />
            <input
              type="text"
              aria-label={`Fact ${i + 1} value`}
              placeholder="Value, e.g. Sunrise Degree College"
              value={row.value}
              onChange={(e) =>
                patch({
                  contextRows: config.contextRows.map((r, j) => (j === i ? { ...r, value: e.target.value } : r)),
                })
              }
            />
            <button
              type="button"
              className="icon-btn qfe-remove"
              aria-label={`Remove fact ${i + 1}`}
              onClick={() => patch({ contextRows: config.contextRows.filter((_, j) => j !== i) })}
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => patch({ contextRows: [...(config.contextRows || []), { key: '', value: '' }] })}
        >
          + Add fact
        </button>
        {errors.company_context && <p className="hint hint-error">{errors.company_context}</p>}
      </div>

      <div className="field">
        <label htmlFor="cf-prompt">
          System prompt <span className="req-star">*</span>
        </label>
        <textarea
          id="cf-prompt"
          rows="5"
          value={config.systemPrompt}
          onChange={(e) => patch({ systemPrompt: e.target.value })}
        />
        <p className="hint">
          High-level instructions for how the agent behaves (persona, tone, hard rules). The question flow is injected
          automatically — you do not need to repeat it here.
        </p>
        {errors.system_prompt && <p className="hint hint-error">{errors.system_prompt}</p>}
      </div>

      <div className="field">
        <label htmlFor="cf-disclosure">
          Mandatory AI disclosure <span className="req-star">*</span>
        </label>
        <textarea
          id="cf-disclosure"
          rows="2"
          value={config.disclosureScript}
          onChange={(e) => patch({ disclosureScript: e.target.value })}
        />
        <p className="hint">
          Spoken verbatim as the very first thing on every call, so the listener knows they are talking to an AI
          (regulatory requirement).
        </p>
        {errors.disclosure_script && <p className="hint hint-error">{errors.disclosure_script}</p>}
      </div>

      <div className="field">
        <label>
          Escalation rules <span className="req-star">*</span>
        </label>
        {(config.escalationRules || []).map((rule, i) => (
          <div className="escalation-row" key={i}>
            <input
              type="text"
              aria-label={`Escalation rule ${i + 1} trigger`}
              placeholder="Trigger, e.g. The caller becomes distressed"
              value={rule.trigger}
              onChange={(e) =>
                patch({
                  escalationRules: config.escalationRules.map((r, j) =>
                    j === i ? { ...r, trigger: e.target.value } : r
                  ),
                })
              }
            />
            <select
              aria-label={`Escalation rule ${i + 1} action`}
              value={rule.action || ''}
              onChange={(e) =>
                patch({
                  escalationRules: config.escalationRules.map((r, j) =>
                    j === i ? { ...r, action: e.target.value } : r
                  ),
                })
              }
            >
              {ESCALATION_ACTIONS.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
            <button
              type="button"
              className="icon-btn qfe-remove"
              aria-label={`Remove escalation rule ${i + 1}`}
              onClick={() => patch({ escalationRules: config.escalationRules.filter((_, j) => j !== i) })}
            >
              ×
            </button>
          </div>
        ))}
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => patch({ escalationRules: [...(config.escalationRules || []), { trigger: '', action: 'flag' }] })}
        >
          + Add rule
        </button>
        <p className="hint">When a trigger matches, the agent stops and follows the action instead of improvising.</p>
        {errors.escalation_rules && <p className="hint hint-error">{errors.escalation_rules}</p>}
      </div>
    </div>
  );
}
