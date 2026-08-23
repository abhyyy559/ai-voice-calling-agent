import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { agentsApi } from '../api.js';
import StatusBadge from '../components/StatusBadge.jsx';
import DataTable from '../components/DataTable.jsx';

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

export default function AgentsPage() {
  const navigate = useNavigate();
  const [agents, setAgents] = useState(null);
  const [versionInfo, setVersionInfo] = useState({}); // agent_id -> {version, created_at}
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    agentsApi
      .list()
      .then(async (list) => {
        if (cancelled) return;
        const rows = Array.isArray(list) ? list : [];
        setAgents(rows);
        // AgentOut carries current_version_id but not the human version number,
        // so hydrate "vN" from each agent's immutable version history.
        await Promise.all(
          rows
            .filter((a) => a.current_version_id != null)
            .map(async (a) => {
              try {
                const versions = await agentsApi.listVersions(a.id);
                if (cancelled || !Array.isArray(versions) || versions.length === 0) return;
                const latest = versions[versions.length - 1];
                setVersionInfo((prev) => ({
                  ...prev,
                  [a.id]: { version: latest.version, created_at: latest.created_at },
                }));
              } catch {
                /* leave '—'; the row still renders */
              }
            })
        );
      })
      .catch((e) => {
        if (!cancelled) setError(e.message || String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [nonce]);

  const columns = [
    {
      key: 'name',
      label: 'Agent',
      render: (a) => (
        <div>
          <span className="cell-strong">{a.name}</span>
          <div className="agent-desc-cell">{a.description || <span className="text-muted">No description</span>}</div>
        </div>
      ),
    },
    { key: 'status', label: 'Status', render: (a) => <StatusBadge status={a.status} /> },
    {
      key: 'version',
      label: 'Current version',
      render: (a) => {
        const info = versionInfo[a.id];
        if (!info) return a.current_version_id != null ? <span className="chip">#{a.current_version_id}</span> : <span className="text-muted">Not saved</span>;
        return (
          <span className="chip">
            v{info.version}
          </span>
        );
      },
    },
    { key: 'updated_at', label: 'Updated', render: (a) => fmtDateTime(a.updated_at), className: 'nowrap' },
    {
      key: 'actions',
      label: '',
      className: 'nowrap',
      render: (a) => (
        <div className="row-actions" onClick={(e) => e.stopPropagation()}>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => navigate(`/agents/${a.id}/edit`)}>
            Edit
          </button>
          {a.current_version_id != null && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => navigate(`/playground/${a.current_version_id}`)}
            >
              Test
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div className="page-head">
        <div>
          <h2 className="page-title">Agents</h2>
          <p className="page-sub">
            Your AI callers. Each agent keeps its conversation flow, extraction fields and voice settings as numbered,
            immutable versions.
          </p>
        </div>
        <button type="button" className="btn btn-primary" onClick={() => navigate('/agents/new')}>
          + New Agent
        </button>
      </div>

      {error && (
        <div className="banner banner-error">
          {error}{' '}
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setNonce((n) => n + 1)}>
            Retry
          </button>
        </div>
      )}

      <div className="card flush">
        <DataTable
          columns={columns}
          rows={agents || []}
          rowKey={(a) => a.id}
          onRowClick={(a) => navigate(`/agents/${a.id}/edit`)}
          loading={loading}
          empty="No agents yet. Create your first agent to start building a call flow."
          emptyAction={
            <button type="button" className="btn btn-primary" onClick={() => navigate('/agents/new')}>
              + Create your first agent
            </button>
          }
        />
      </div>

      {!loading && agents && agents.length > 0 && (
        <p className="hint">
          Tip: an agent becomes callable once you save at least one version from the builder wizard.
        </p>
      )}
    </div>
  );
}
