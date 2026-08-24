import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authApi, setSession } from '../api.js';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state && location.state.from ? location.state.from : '/';

  // Landing-page "Register" CTAs deep-link into the register tab.
  const [mode, setMode] = useState(location.state && location.state.mode === 'register' ? 'register' : 'login');
  const [form, setForm] = useState({ orgName: '', email: '', password: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const isRegister = mode === 'register';

  function switchMode(next) {
    setMode(next);
    setError(null);
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = isRegister
        ? await authApi.register({
            orgName: form.orgName.trim(),
            email: form.email.trim(),
            password: form.password,
          })
        : await authApi.login({ email: form.email.trim(), password: form.password });
      if (!res || !res.token) {
        throw new Error('Server did not return a session token.');
      }
      setSession(res.token, res.user);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Could not sign in.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-screen">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="brand-mark">V</div>
          <div>
            <div className="brand-name">VocalIQ</div>
            <div className="brand-sub">Voice calling console</div>
          </div>
        </div>

        <div className="tabs auth-tabs">
          <button
            type="button"
            className={`tab${!isRegister ? ' active' : ''}`}
            onClick={() => switchMode('login')}
          >
            Sign in
          </button>
          <button
            type="button"
            className={`tab${isRegister ? ' active' : ''}`}
            onClick={() => switchMode('register')}
          >
            Create organization
          </button>
        </div>

        {isRegister ? (
          <p className="hint auth-hint">
            Registering creates your organization and its first (owner) account in one step. Everything you build —
            agents, campaigns, contacts — lives inside that organization.
          </p>
        ) : (
          <p className="hint auth-hint">Sign in to manage agents, run playground tests and launch campaigns.</p>
        )}

        <form onSubmit={submit}>
          {isRegister && (
            <div className="field">
              <label htmlFor="login-org">
                Organization name <span className="req-star">*</span>
              </label>
              <input
                id="login-org"
                type="text"
                autoComplete="organization"
                autoFocus
                value={form.orgName}
                placeholder="e.g. Sunrise Degree College"
                onChange={(e) => setForm({ ...form, orgName: e.target.value })}
              />
            </div>
          )}

          <div className="field">
            <label htmlFor="login-email">
              Work email <span className="req-star">*</span>
            </label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              value={form.email}
              placeholder="you@company.com"
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <div className="field">
            <label htmlFor="login-password">
              Password <span className="req-star">*</span>
            </label>
            <input
              id="login-password"
              type="password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              value={form.password}
              placeholder={isRegister ? 'At least 8 characters' : 'Your password'}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>

          {error && <div className="banner banner-error">{error}</div>}

          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={
                busy ||
                !form.email.trim() ||
                !form.password ||
                (isRegister && !form.orgName.trim())
              }
            >
              {busy ? 'Please wait…' : isRegister ? 'Create organization' : 'Sign in'}
            </button>
          </div>
        </form>

        {!isRegister && (
          <p className="hint auth-demo-hint">
            Local dev seeded account: <code>demo@example.com</code> / <code>demo1234</code> (created by{' '}
            <code>backend/scripts/seed_demo.py</code>).
          </p>
        )}

        <div className="auth-back">
          <Link className="btn btn-ghost btn-sm" to="/">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
