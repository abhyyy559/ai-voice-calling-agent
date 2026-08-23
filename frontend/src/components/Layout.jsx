import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { clearSession, getStoredUser } from '../api.js';

function DashboardIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M3 3h8v8H3V3zm10 0h8v5h-8V3zM3 13h8v8H3v-8zm10-3h8v11h-8V10z" />
    </svg>
  );
}

function AgentsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2a4 4 0 1 1 0 8 4 4 0 0 1 0-8zM4 22c0-4.4 3.6-7 8-7s8 2.6 8 7H4z" />
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2a3 3 0 0 1 3 3v6a3 3 0 1 1-6 0V5a3 3 0 0 1 3-3zM5 11h2a5 5 0 0 0 10 0h2a7 7 0 0 1-6 6.93V21h3v2H8v-2h3v-3.07A7 7 0 0 1 5 11z" />
    </svg>
  );
}

function CampaignsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M4 6h16v2H4V6zm0 5h16v2H4v-2zm0 5h10v2H4v-2z" />
    </svg>
  );
}

function PhoneIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M6.6 10.8c1.5 2.9 3.8 5.2 6.7 6.7l2.2-2.2c.3-.3.7-.4 1.1-.3 1.2.4 2.5.6 3.9.6.6 0 1 .5 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.5.4-1 1-1h3.5c.5 0 1 .4 1 1 0 1.4.2 2.7.6 3.9.1.4 0 .8-.3 1.1l-2.2 2.3z" />
    </svg>
  );
}

function WrenchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M22 5.5a5.5 5.5 0 0 1-7.8 5L7 17.7A2.3 2.3 0 1 1 3.7 14l7.3-7.2A5.5 5.5 0 0 1 18.5 0L15 3.5 17.5 6 21 2.5c.6.9 1 1.9 1 3z" transform="scale(0.95) translate(0.5 1)" />
    </svg>
  );
}

const NAV_ITEMS = [
  { to: '/', end: true, icon: <DashboardIcon />, label: 'Dashboard' },
  { to: '/agents', icon: <AgentsIcon />, label: 'Agents' },
  { to: '/playground', icon: <PlayIcon />, label: 'Playground' },
  { to: '/campaigns', icon: <CampaignsIcon />, label: 'Campaigns' },
  { to: '/test-call', icon: <PhoneIcon />, label: 'Test Call' },
  { to: '/dev', icon: <WrenchIcon />, label: 'Dev Tools' },
];

const navClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`;

export default function Layout() {
  const navigate = useNavigate();
  const user = getStoredUser();

  function logout() {
    clearSession();
    navigate('/login', { replace: true });
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark">AI</div>
          <div>
            <div className="brand-name">Voice Calling Agent</div>
            <div className="brand-sub">Admin console</div>
          </div>
        </div>
        <nav className="sidebar-nav" aria-label="Main navigation">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={navClass}>
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-user">
          <div className="sidebar-user-email" title={user && user.email ? user.email : ''}>
            {(user && user.email) || 'Signed in'}
          </div>
          <button type="button" className="btn btn-ghost btn-sm sidebar-logout" onClick={logout}>
            Sign out
          </button>
        </div>
        <div className="sidebar-footer">Phase 1 · English · India</div>
      </aside>
      <div className="main-area">
        <header className="topbar">
          <h1>AI Voice Calling Agent</h1>
          <span className="topbar-tag">Admin</span>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
