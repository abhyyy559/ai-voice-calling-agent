export const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

function extractErrorDetail(body) {
  if (body == null) return null;
  if (typeof body === 'string') return body;
  if (typeof body.detail === 'string') return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d) => (d && d.msg ? d.msg : JSON.stringify(d))).join('; ');
  }
  if (body.detail && typeof body.detail === 'object') return JSON.stringify(body.detail);
  if (typeof body.message === 'string') return body.message;
  if (typeof body.error === 'string') return body.error;
  return JSON.stringify(body);
}

/**
 * Minimal fetch wrapper. JSON in / JSON out, FormData supported.
 * Throws ApiError with a human-readable message on non-2xx responses.
 */
export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body != null && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(`Cannot reach the server at ${API_BASE}. Is the backend running?`, 0, null);
  }

  if (!res.ok) {
    let body = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }
    const detail = extractErrorDetail(body);
    throw new ApiError(detail || `Request failed (${res.status} ${res.statusText})`, res.status, body);
  }

  if (res.status === 204) return null;
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export const api = {
  listCampaigns: () => apiFetch('/api/campaigns'),
  createCampaign: (data) => apiFetch('/api/campaigns', { method: 'POST', body: JSON.stringify(data) }),
  getCampaign: (id) => apiFetch(`/api/campaigns/${id}`),
  launchCampaign: (id) => apiFetch(`/api/campaigns/${id}/launch`, { method: 'POST' }),
  pauseCampaign: (id) => apiFetch(`/api/campaigns/${id}/pause`, { method: 'POST' }),
  cancelCampaign: (id) => apiFetch(`/api/campaigns/${id}/cancel`, { method: 'POST' }),
  getCampaignDashboard: (id) => apiFetch(`/api/campaigns/${id}/dashboard`),

  importContacts: (campaignId, formData) =>
    apiFetch(`/api/campaigns/${campaignId}/contacts/import`, { method: 'POST', body: formData }),
  listContacts: (campaignId, { page = 1, pageSize = 50, status = '' } = {}) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    if (status) params.set('status', status);
    return apiFetch(`/api/campaigns/${campaignId}/contacts?${params.toString()}`);
  },
  updateContact: (contactId, data) =>
    apiFetch(`/api/contacts/${contactId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  deleteContact: (contactId) => apiFetch(`/api/contacts/${contactId}`, { method: 'DELETE' }),

  listDomainConfigs: () => apiFetch('/api/domain-configs'),
  listCampaignCalls: (campaignId) => apiFetch(`/api/campaigns/${campaignId}/calls`),
  getCall: (callId) => apiFetch(`/api/calls/${callId}`),
  placeTestCall: (data) => apiFetch('/api/test-call', { method: 'POST', body: JSON.stringify(data) }),
};

export function campaignExportUrl(campaignId, format) {
  return `${API_BASE}/api/campaigns/${campaignId}/export?format=${encodeURIComponent(format)}`;
}
