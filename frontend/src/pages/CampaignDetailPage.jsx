import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, campaignExportUrl } from '../api.js';
import usePoll from '../hooks/usePoll.js';
import StatusBadge, { statusLabel } from '../components/StatusBadge.jsx';
import Modal from '../components/Modal.jsx';
import DataTable from '../components/DataTable.jsx';
import CountsCards from '../components/CountsCards.jsx';
import ColumnMapper, { EMPTY_MAPPING, guessMapping, parseCsvHeader } from '../components/ColumnMapper.jsx';

const PAGE_SIZE = 50;
const CONTACT_STATUS_FILTERS = [
  'pending_review',
  'invalid',
  'queued',
  'calling',
  'completed',
  'no_answer',
  'busy',
  'failed',
  'opted_out',
];
const LAUNCHABLE = ['draft', 'created', 'paused'];
const CANCELED_like = ['canceled', 'cancelled'];

// Calling window enforced by POST /api/campaigns/{id}/launch (PRD §8):
// 9 AM – 9 PM IST, start inclusive / end exclusive. Mirrored client-side so
// users get told WHY launching is blocked instead of a bare 422 after clicking.
const CALLING_HOURS_START = 9;
const CALLING_HOURS_END = 21;

function istNow() {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Asia/Kolkata',
    hour: 'numeric',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(new Date());
  const get = (type) => Number(parts.find((p) => p.type === type)?.value);
  let hour = get('hour');
  if (hour === 24) hour = 0;
  return {
    hour,
    label: `${String(hour).padStart(2, '0')}:${String(get('minute')).padStart(2, '0')}`,
  };
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
  });
}

function fmtDuration(seconds) {
  if (seconds == null || Number.isNaN(Number(seconds))) return '—';
  const s = Math.max(0, Math.round(Number(seconds)));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, '0')}`;
}

function consentValue(v) {
  if (v === true || v === 'true' || v === 1 || v === '1') return true;
  if (v === false || v === 'false' || v === 0 || v === '0') return false;
  return null;
}

function friendlyActionError(e) {
  const msg = e?.message || 'Action failed.';
  if (msg.startsWith('outside calling hours')) {
    return `Launch blocked: calls only run between 9 AM and 9 PM IST. ${msg} — try again once the window opens.`;
  }
  if (msg === 'campaign has no contacts to call') {
    return 'This campaign has no contacts yet — upload a contact list on the Contacts tab, then launch.';
  }
  return msg;
}

export default function CampaignDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tab, setTab] = useState('contacts');

  // ---- campaign + dashboard (poll every 3s while running) ----
  const [campaignStatus, setCampaignStatus] = useState(null);
  const running = campaignStatus === 'running';

  const {
    data: campaign,
    error: campaignError,
    loading: campaignLoading,
    reload: reloadCampaign,
  } = usePoll(`/api/campaigns/${id}`, 3000, running);
  const { data: dash, error: dashError, reload: reloadDash } = usePoll(`/api/campaigns/${id}/dashboard`, 3000, running);

  useEffect(() => {
    if (campaign && campaign.status) setCampaignStatus(campaign.status);
  }, [campaign]);
  useEffect(() => {
    if (dash && dash.campaign && dash.campaign.status) setCampaignStatus(dash.campaign.status);
  }, [dash]);

  // ---- lifecycle actions ----
  const [actionBusy, setActionBusy] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  async function runAction(fn) {
    setActionBusy(true);
    setActionError(null);
    try {
      await fn();
      reloadCampaign();
      reloadDash();
    } catch (e) {
      setActionError(friendlyActionError(e));
    } finally {
      setActionBusy(false);
      setShowCancelConfirm(false);
    }
  }

  // ---- launch pre-checks (server stays the source of truth; this just
  // explains the common rejections BEFORE the click instead of after) ----
  const [istClock, setIstClock] = useState(istNow);
  useEffect(() => {
    const timer = setInterval(() => setIstClock(istNow()), 30_000);
    return () => clearInterval(timer);
  }, []);
  const contactTotal = campaign?.counts?.total;
  const hasContacts = contactTotal == null ? true : contactTotal > 0;
  const withinCallingHours =
    istClock.hour >= CALLING_HOURS_START && istClock.hour < CALLING_HOURS_END;
  const launchBlockedReason = !hasContacts
    ? 'Upload contacts first — a campaign needs at least one contact before it can be launched.'
    : !withinCallingHours
      ? `Calls only run between 9 AM and 9 PM IST. It is currently ${istClock.label} IST, so launching is paused until the window opens.`
      : null;

  // ---- contacts list ----
  const [contactsData, setContactsData] = useState(null);
  const [contactsLoading, setContactsLoading] = useState(false);
  const [contactsError, setContactsError] = useState(null);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('all');
  const [contactsNonce, setContactsNonce] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setContactsLoading(true);
    api
      .listContacts(id, {
        page,
        pageSize: PAGE_SIZE,
        status: statusFilter === 'all' ? '' : statusFilter,
      })
      .then((d) => {
        if (!cancelled) {
          setContactsData(d);
          setContactsError(null);
        }
      })
      .catch((e) => {
        if (!cancelled) setContactsError(e.message);
      })
      .finally(() => {
        if (!cancelled) setContactsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id, page, statusFilter, contactsNonce]);

  const refreshContacts = () => setContactsNonce((n) => n + 1);
  const totalPages = contactsData ? Math.max(1, Math.ceil((contactsData.total || 0) / (contactsData.page_size || PAGE_SIZE))) : 1;

  // ---- import ----
  const [file, setFile] = useState(null);
  const [fileKey, setFileKey] = useState(0);
  const [headers, setHeaders] = useState(null);
  const [mapping, setMapping] = useState({ ...EMPTY_MAPPING });
  const [customRows, setCustomRows] = useState([]);
  const [consentDefault, setConsentDefault] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [importError, setImportError] = useState(null);

  async function onFileChange(e) {
    const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
    setFile(f);
    setImportResult(null);
    setImportError(null);
    setCustomRows([]);
    if (!f) {
      setHeaders(null);
      setMapping({ ...EMPTY_MAPPING });
      return;
    }
    if (/\.(csv|tsv|txt)$/i.test(f.name)) {
      try {
        const text = await f.text();
        const hdrs = parseCsvHeader(text);
        setHeaders(hdrs.length ? hdrs : null);
        setMapping(hdrs.length ? guessMapping(hdrs) : { ...EMPTY_MAPPING });
      } catch {
        setHeaders(null);
        setMapping({ ...EMPTY_MAPPING });
      }
    } else {
      // XLSX: cannot parse headers client-side without a spreadsheet lib.
      setHeaders(null);
      setMapping({ ...EMPTY_MAPPING });
    }
  }

  function resetImportPanel() {
    setFile(null);
    setFileKey((k) => k + 1);
    setHeaders(null);
    setMapping({ ...EMPTY_MAPPING });
    setCustomRows([]);
  }

  async function doImport() {
    if (!file || !mapping.phone_col) return;
    setImporting(true);
    setImportError(null);
    setImportResult(null);
    const custom = {};
    customRows.forEach((r) => {
      if (r.field && r.col) custom[r.field] = r.col;
    });
    const fd = new FormData();
    fd.append('file', file);
    fd.append(
      'mapping',
      JSON.stringify({
        name_col: mapping.name_col || null,
        phone_col: mapping.phone_col || null,
        id_col: mapping.id_col || null,
        consent_col: mapping.consent_col || null,
        custom,
      })
    );
    fd.append('consent_default', consentDefault ? 'true' : 'false');
    try {
      const result = await api.importContacts(id, fd);
      setImportResult(result || {});
      resetImportPanel();
      setPage(1);
      refreshContacts();
      reloadDash();
    } catch (e) {
      setImportError(e.message || 'Import failed.');
    } finally {
      setImporting(false);
    }
  }

  // ---- edit / delete contact ----
  const [editContact, setEditContact] = useState(null);
  const [editForm, setEditForm] = useState({ name: '', phone: '', consent: false });
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  function openEdit(c) {
    setEditContact(c);
    setEditError(null);
    setEditForm({
      name: c.name || '',
      phone: c.phone || '',
      consent: consentValue(c.consent) === true,
    });
  }

  async function saveEdit() {
    setEditSaving(true);
    setEditError(null);
    try {
      await api.updateContact(editContact.id, {
        name: editForm.name.trim(),
        phone: editForm.phone.trim(),
        consent: editForm.consent,
      });
      setEditContact(null);
      refreshContacts();
    } catch (e) {
      setEditError(e.message || 'Could not save changes.');
    } finally {
      setEditSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleteBusy(true);
    setDeleteError(null);
    try {
      await api.deleteContact(deleteTarget.id);
      setDeleteTarget(null);
      refreshContacts();
    } catch (e) {
      setDeleteError(e.message || 'Could not delete contact.');
    } finally {
      setDeleteBusy(false);
    }
  }

  // ---- derived ----
  const canLaunch = LAUNCHABLE.includes(campaignStatus);
  const canPause = campaignStatus === 'running';
  const canCancel =
    campaignStatus != null && campaignStatus !== 'completed' && !CANCELED_like.includes(campaignStatus);

  const contactColumns = [
    {
      key: 'name',
      label: 'Name',
      render: (c) => <span className="cell-strong">{c.name || '—'}</span>,
    },
    { key: 'phone', label: 'Phone' },
    { key: 'external_id', label: 'External ID', render: (c) => c.external_id || '—' },
    { key: 'status', label: 'Status', render: (c) => <StatusBadge status={c.status} /> },
    {
      key: 'consent',
      label: 'Consent',
      render: (c) => {
        const v = consentValue(c.consent);
        if (v === true) return <span className="chip chip-green">Yes</span>;
        if (v === false) return <span className="chip chip-red">No</span>;
        return <span className="text-muted">—</span>;
      },
    },
    { key: 'attempt_count', label: 'Attempts' },
    {
      key: 'custom_fields',
      label: 'Custom fields',
      render: (c) => {
        const cf = c.custom_fields;
        if (!cf || typeof cf !== 'object' || Array.isArray(cf) || Object.keys(cf).length === 0) {
          return <span className="text-muted">—</span>;
        }
        const entries = Object.entries(cf);
        return (
          <span className="cf-chips" title={JSON.stringify(cf, null, 2)}>
            {entries.slice(0, 2).map(([k, v]) => (
              <span key={k} className="chip">
                {k}: {String(v)}
              </span>
            ))}
            {entries.length > 2 && <span className="chip chip-more">+{entries.length - 2}</span>}
          </span>
        );
      },
    },
    {
      key: 'actions',
      label: '',
      render: (c) => (
        <div className="row-actions" onClick={(e) => e.stopPropagation()}>
          <button className="btn btn-secondary btn-sm" onClick={() => openEdit(c)}>
            Edit
          </button>
          <button className="btn btn-danger-outline btn-sm" onClick={() => setDeleteTarget(c)}>
            Delete
          </button>
        </div>
      ),
      className: 'nowrap',
    },
  ];

  const callColumns = [
    {
      key: 'contact_name',
      label: 'Contact',
      render: (c) => <span className="cell-strong">{c.contact_name || '—'}</span>,
    },
    { key: 'phone', label: 'Phone' },
    { key: 'status', label: 'Status', render: (c) => <StatusBadge status={c.status} /> },
    {
      key: 'outcome',
      label: 'Outcome',
      render: (c) => (c.outcome ? <span className="chip">{String(c.outcome)}</span> : <span className="text-muted">—</span>),
    },
    { key: 'started_at', label: 'Started', render: (c) => fmtDateTime(c.started_at), className: 'nowrap' },
    {
      key: 'duration_seconds',
      label: 'Duration',
      render: (c) => fmtDuration(c.duration_seconds),
      className: 'nowrap',
    },
    {
      key: 'flagged_for_human',
      label: 'Flag',
      render: (c) => (c.flagged_for_human ? <StatusBadge status="flagged" /> : <span className="text-muted">—</span>),
    },
  ];

  // ---- render ----
  if (campaignError && !campaign) {
    return (
      <div>
        <Link to="/" className="back-link">
          ← Campaigns
        </Link>
        <div className="banner banner-error">
          {campaignError}{' '}
          <button className="btn btn-secondary btn-sm" onClick={reloadCampaign}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (campaignLoading && !campaign) {
    return (
      <div className="loading-page">
        <span className="spinner" /> Loading campaign…
      </div>
    );
  }

  return (
    <div>
      <Link to="/" className="back-link">
        ← Campaigns
      </Link>

      <div className="page-head detail-head">
        <div>
          <div className="title-row">
            <h2 className="page-title">{campaign.name || `Campaign ${id}`}</h2>
            <StatusBadge status={campaignStatus || campaign.status} />
            {running && (
              <span className="live-indicator">
                <span className="live-dot" /> Live
              </span>
            )}
          </div>
          <p className="meta-line">
            <span>
              <strong>Domain:</strong> {campaign.domain_config_name || '—'}
            </span>
            <span>
              <strong>Created:</strong> {fmtDateTime(campaign.created_at)}
            </span>
            <span>
              <strong>ID:</strong> {campaign.id}
            </span>
          </p>
        </div>
        <div className="head-actions">
          {canLaunch && (
            <button
              className="btn btn-primary"
              disabled={actionBusy || !!launchBlockedReason}
              title={launchBlockedReason || undefined}
              onClick={() => runAction(() => api.launchCampaign(id))}
            >
              Launch campaign
            </button>
          )}
          {canPause && (
            <button className="btn btn-secondary" disabled={actionBusy} onClick={() => runAction(() => api.pauseCampaign(id))}>
              Pause
            </button>
          )}
          {canCancel && (
            <button className="btn btn-danger-outline" disabled={actionBusy} onClick={() => setShowCancelConfirm(true)}>
              Cancel
            </button>
          )}
          <div className="export-group">
            <span className="export-label">Export:</span>
            <button className="btn btn-secondary btn-sm" onClick={() => window.open(campaignExportUrl(id, 'csv'), '_blank')}>
              CSV
            </button>
            <button className="btn btn-secondary btn-sm" onClick={() => window.open(campaignExportUrl(id, 'xlsx'), '_blank')}>
              XLSX
            </button>
          </div>
        </div>
      </div>

      {actionError && <div className="banner banner-error">{actionError}</div>}
      {canLaunch && launchBlockedReason && !actionError && (
        <div className="banner banner-info">{launchBlockedReason}</div>
      )}

      <div className="tabs">
        <button className={`tab${tab === 'contacts' ? ' active' : ''}`} onClick={() => setTab('contacts')}>
          Contacts
        </button>
        <button className={`tab${tab === 'dashboard' ? ' active' : ''}`} onClick={() => setTab('dashboard')}>
          Dashboard
        </button>
      </div>

      {tab === 'contacts' && (
        <div className="stack">
          <div className="card upload-panel">
            <h3 className="card-title">Import contacts</h3>
            <p className="hint">
              Upload a CSV or XLSX contact list, then map its columns. CSV column headers are detected automatically;
              for XLSX you can type the exact column headers.
            </p>
            <div className="file-row">
              <input key={fileKey} type="file" accept=".csv,.tsv,.txt,.xlsx,.xls" onChange={onFileChange} />
            </div>

            {file && (
              <ColumnMapper
                headers={headers}
                mapping={mapping}
                onMappingChange={setMapping}
                customRows={customRows}
                onCustomRowsChange={setCustomRows}
                consentDefault={consentDefault}
                onConsentDefaultChange={setConsentDefault}
              />
            )}

            {file && (
              <div className="upload-actions">
                <button className="btn btn-primary" disabled={importing || !mapping.phone_col} onClick={doImport}>
                  {importing ? 'Importing…' : `Import “${file.name}”`}
                </button>
                {!mapping.phone_col && <span className="hint hint-error">Map the phone column to enable import.</span>}
              </div>
            )}

            {importError && <div className="banner banner-error">{importError}</div>}
            {importResult && (
              <div className={`banner ${importResult.imported > 0 ? 'banner-success' : 'banner-error'}`}>
                <strong>
                  Imported {importResult.imported ?? 0} contact{importResult.imported === 1 ? '' : 's'}
                </strong>
                {importResult.invalid ? ` · ${importResult.invalid} skipped as invalid` : ''}
                {importResult.errors && importResult.errors.length > 0 && (
                  <ul className="error-list">
                    {importResult.errors.slice(0, 8).map((err, i) => (
                      <li key={i}>{String(err)}</li>
                    ))}
                    {importResult.errors.length > 8 && <li>… and {importResult.errors.length - 8} more</li>}
                  </ul>
                )}
              </div>
            )}
          </div>

          <div className="card flush">
            <div className="table-toolbar">
              <h3 className="card-title">Contacts</h3>
              <div className="toolbar-right">
                <label className="filter-label" htmlFor="status-filter">
                  Status
                </label>
                <select
                  id="status-filter"
                  value={statusFilter}
                  onChange={(e) => {
                    setStatusFilter(e.target.value);
                    setPage(1);
                  }}
                >
                  <option value="all">All</option>
                  {CONTACT_STATUS_FILTERS.map((s) => (
                    <option key={s} value={s}>
                      {statusLabel(s)}
                    </option>
                  ))}
                </select>
                <button className="btn btn-secondary btn-sm" onClick={refreshContacts} disabled={contactsLoading}>
                  Refresh
                </button>
              </div>
            </div>
            {contactsError && <div className="banner banner-error inset">{contactsError}</div>}
            <DataTable
              columns={contactColumns}
              rows={(contactsData && contactsData.items) || []}
              rowKey={(c) => c.id}
              loading={contactsLoading}
              empty={statusFilter === 'all' ? 'No contacts yet — import a list above.' : 'No contacts match this filter.'}
            />
            <div className="pagination">
              <span className="page-info">
                {contactsData
                  ? contactsData.total === 0
                    ? '0 contacts'
                    : `Showing ${((contactsData.page || page) - 1) * (contactsData.page_size || PAGE_SIZE) + 1}–${Math.min(
                        (contactsData.page || page) * (contactsData.page_size || PAGE_SIZE),
                        contactsData.total
                      )} of ${contactsData.total}`
                  : ''}
              </span>
              <div className="page-btns">
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page <= 1 || contactsLoading}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Previous
                </button>
                <span className="page-num">
                  Page {page}
                  {totalPages > 1 ? ` of ${totalPages}` : ''}
                </span>
                <button
                  className="btn btn-secondary btn-sm"
                  disabled={page >= totalPages || contactsLoading}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {tab === 'dashboard' && (
        <div className="stack">
          {dashError && !dash && <div className="banner banner-error">{dashError}</div>}
          {!dash ? (
            <div className="loading-page">
              <span className="spinner" /> Loading dashboard…
            </div>
          ) : (
            <>
              {running ? (
                <div className="live-indicator big">
                  <span className="live-dot" /> Live — refreshing every 3 seconds
                </div>
              ) : (
                <p className="hint">Campaign is not running — showing the latest snapshot. Counts update while a campaign runs.</p>
              )}
              <CountsCards counts={dash.counts} inFlight={dash.in_flight} />
              <div className="card flush">
                <div className="table-toolbar">
                  <h3 className="card-title">Recent calls</h3>
                </div>
                <DataTable
                  columns={callColumns}
                  rows={dash.recent_calls || []}
                  rowKey={(c) => c.id}
                  onRowClick={(c) => navigate(`/calls/${c.id}`)}
                  empty="No calls yet for this campaign."
                />
              </div>
            </>
          )}
        </div>
      )}

      {showCancelConfirm && (
        <Modal
          title="Cancel this campaign?"
          onClose={() => setShowCancelConfirm(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowCancelConfirm(false)}>
                Keep campaign
              </button>
              <button
                className="btn btn-danger"
                disabled={actionBusy}
                onClick={() => runAction(() => api.cancelCampaign(id))}
              >
                {actionBusy ? 'Canceling…' : 'Yes, cancel campaign'}
              </button>
            </>
          }
        >
          <p>
            Canceling stops all calling for <strong>{campaign.name}</strong>. Contacts still queued will not be called,
            and this cannot be undone.
          </p>
        </Modal>
      )}

      {editContact && (
        <Modal
          title="Edit contact"
          onClose={() => setEditContact(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setEditContact(null)}>
                Cancel
              </button>
              <button className="btn btn-primary" disabled={editSaving || !editForm.phone.trim()} onClick={saveEdit}>
                {editSaving ? 'Saving…' : 'Save changes'}
              </button>
            </>
          }
        >
          <div className="field">
            <label htmlFor="edit-name">Name</label>
            <input
              id="edit-name"
              type="text"
              value={editForm.name}
              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="edit-phone">Phone</label>
            <input
              id="edit-phone"
              type="text"
              value={editForm.phone}
              onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
            />
          </div>
          <label className="check-row">
            <input
              type="checkbox"
              checked={editForm.consent}
              onChange={(e) => setEditForm({ ...editForm, consent: e.target.checked })}
            />
            <span>This contact has a recorded consent basis</span>
          </label>
          {editError && <div className="banner banner-error">{editError}</div>}
        </Modal>
      )}

      {deleteTarget && (
        <Modal
          title="Delete contact?"
          onClose={() => setDeleteTarget(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setDeleteTarget(null)}>
                No, keep it
              </button>
              <button className="btn btn-danger" disabled={deleteBusy} onClick={confirmDelete}>
                {deleteBusy ? 'Deleting…' : 'Yes, delete'}
              </button>
            </>
          }
        >
          <p>
            Delete <strong>{deleteTarget.name || deleteTarget.phone}</strong>
            {deleteTarget.phone ? ` (${deleteTarget.phone})` : ''} from this campaign? This cannot be undone.
          </p>
          {deleteError && <div className="banner banner-error">{deleteError}</div>}
        </Modal>
      )}
    </div>
  );
}
