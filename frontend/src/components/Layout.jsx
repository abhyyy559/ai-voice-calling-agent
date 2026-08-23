import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

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

const navClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`;

export default function Layout() {
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
        <nav className="sidebar-nav">
          <NavLink to="/" end className={navClass}>
            <CampaignsIcon />
            Campaigns
          </NavLink>
          <NavLink to="/test-call" className={navClass}>
            <PhoneIcon />
            Test Call
          </NavLink>
        </nav>
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
