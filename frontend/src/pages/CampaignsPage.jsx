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
  const [form, setForm] = useState({ name: '', domain_config_id: '' });
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
  }, []);

  async function submitNew() {
    setCreating(true);
    setCreateError(null);
    try {
      const created = await api.createCampaign({
        name: form.name.trim(),
        domain_config_id: form.domain_config_id,
      });
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
                disabled={creating || !form.name.trim() || !form.domain_config_id}
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
            {domainsError && <p className="hint hint-error">{domainsError}</p>}
            {!domainsError && domains.length === 0 && (
              <p className="hint">No domain configs available yet — add one first (see /domain-configs).</p>
            )}
          </div>
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
