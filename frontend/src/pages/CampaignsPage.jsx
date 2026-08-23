import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api.js';
import usePoll from '../hooks/usePoll.js';
import StatusBadge from '../components/StatusBadge.jsx';
import DataTable from '../components/DataTable.jsx';
import Modal from '../components/Modal.jsx';

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
  });
}

function CountsMini({ counts }) {
  if (!counts || counts.total == null) return <span className="text-muted">—</span>;
  const parts = [`${counts.total} total`];
  if (counts.completed) parts.push(`${counts.completed} completed`);
  if (counts.failed) parts.push(`${counts.failed} failed`);
  return <span className="counts-mini">{parts.join(' · ')}</span>;
}

export default function CampaignsPage() {
  const navigate = useNavigate();
  const { data: campaigns, error, loading, reload } = usePoll('/api/campaigns', 5000);

  const [showNew, setShowNew] = useState(false);
  const [domains, setDomains] = useState([]);
  const [domainsError, setDomainsError] = useState(null);
  const [agents, setAgents] = useState([]);
  const [agentsError, setAgentsError] = useState(null);
  const [form, setForm] = useState({ name: '', domain_config_id: '', agent_version_id: '' });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  useEffect(() => {
    api
      .listDomainConfigs()
      .then((list) => {
        setDomains(Array.isArray(list) ? list : []);
        setDomainsError(null);
      })
      .catch((e) => setDomainsError(e.message));
    api
      .listAgents()
      .then((list) => {
        setAgents(Array.isArray(list) ? list.filter((a) => a.current_version_id != null) : []);
        setAgentsError(null);
      })
      .catch((e) => setAgentsError(e.message));
  }, []);

  // Agents are the primary path; the legacy domain-config select only shows
  // when no agent has a saved version yet.
  const hasAgentVersions = agents.length > 0;

  async function submitNew() {
    setCreating(true);
    setCreateError(null);
    try {
      const payload = { name: form.name.trim() };
      if (hasAgentVersions) {
        payload.agent_version_id = Number(form.agent_version_id);
      } else {
        payload.domain_config_id = form.domain_config_id;
      }
      const created = await api.createCampaign(payload);
      setShowNew(false);
      reload();
      if (created && created.id != null) {
        navigate(`/campaigns/${created.id}`);
      }
    } catch (e) {
      setCreateError(e.message || 'Could not create campaign.');
    } finally {
      setCreating(false);
    }
  }

  const columns = [
    {
      key: 'name',
      label: 'Campaign',
      render: (c) => <span className="cell-strong">{c.name || `Campaign ${c.id}`}</span>,
    },
    { key: 'domain_config_name', label: 'Call domain', render: (c) => c.domain_config_name || '—' },
    { key: 'status', label: 'Status', render: (c) => <StatusBadge status={c.status} /> },
    { key: 'counts', label: 'Contacts', render: (c) => <CountsMini counts={c.counts} /> },
    { key: 'created_at', label: 'Created', render: (c) => fmtDateTime(c.created_at), className: 'nowrap' },
  ];

  return (
    <div>
      <div className="page-head">
        <div>
          <h2 className="page-title">Campaigns</h2>
          <p className="page-sub">Upload contacts, launch calling campaigns, and monitor live progress.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowNew(true)}>
          + New Campaign
        </button>
      </div>

      {error && (
        <div className="banner banner-error">
          {error}{' '}
          <button className="btn btn-secondary btn-sm" onClick={reload}>
            Retry
          </button>
        </div>
      )}

      <div className="card flush">
        <DataTable
          columns={columns}
          rows={campaigns || []}
          rowKey={(c) => c.id}
          onRowClick={(c) => navigate(`/campaigns/${c.id}`)}
          loading={loading}
          empty="No campaigns yet. Create your first campaign to get started."
        />
      </div>

      {showNew && (
        <Modal
          title="New campaign"
          onClose={() => setShowNew(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowNew(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                disabled={
                  creating ||
                  !form.name.trim() ||
                  (hasAgentVersions ? !form.agent_version_id : !form.domain_config_id)
                }
                onClick={submitNew}
              >
                {creating ? 'Creating…' : 'Create campaign'}
              </button>
            </>
          }
        >
          <div className="field">
            <label htmlFor="camp-name">Campaign name</label>
            <input
              id="camp-name"
              type="text"
              autoFocus
              value={form.name}
              placeholder="e.g. Absent students follow-up — Aug 23"
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          {hasAgentVersions ? (
            <div className="field">
              <label htmlFor="camp-agent">Agent (pinned version)</label>
              <select
                id="camp-agent"
                value={form.agent_version_id}
                onChange={(e) => setForm({ ...form, agent_version_id: e.target.value })}
              >
                <option value="">Select an agent…</option>
                {agents.map((a) => (
                  <option key={a.id} value={a.current_version_id}>
                    {a.name} — current version
                  </option>
                ))}
              </select>
              {agentsError && <p className="hint hint-error">{agentsError}</p>}
              <p className="hint">
                The campaign calls with the agent's current saved version. Editing the agent later never changes a
                running campaign until you point it at the new version.
              </p>
            </div>
          ) : (
            <div className="field">
              <label htmlFor="camp-domain">Call domain</label>
              <select
                id="camp-domain"
                value={form.domain_config_id}
                onChange={(e) => setForm({ ...form, domain_config_id: e.target.value })}
              >
                <option value="">Select a call domain…</option>
                {domains.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.display_name || d.name}
                    {d.version != null ? ` (v${d.version})` : ''}
                  </option>
                ))}
              </select>
              {(domainsError || agentsError) && (
                <p className="hint hint-error">{domainsError || agentsError}</p>
              )}
              {!domainsError && domains.length === 0 && (
                <p className="hint">
                  No call domains available yet — build an agent instead for full control of the conversation.
                </p>
              )}
            </div>
          )}
          {createError && <div className="banner banner-error">{createError}</div>}
          <p className="hint">
            After creating the campaign you will upload its contact list. Calls only run inside the 9 AM–9 PM IST
            calling window once launched.
          </p>
        </Modal>
      )}
    </div>
  );
}
