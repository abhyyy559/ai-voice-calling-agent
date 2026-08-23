import React from 'react';
import { Link } from 'react-router-dom';

const FEATURES = [
  {
    title: 'Agents',
    to: '/agents',
    cta: 'Manage agents',
    body:
      'An agent is one AI caller persona — what it says, what it asks and what it writes down. Build or edit an agent here; every save creates a numbered version you can always roll back to.',
    tone: 'blue',
  },
  {
    title: 'Playground',
    to: '/playground',
    cta: 'Talk to an agent',
    body:
      'Test any saved agent version straight from your browser microphone — no phone numbers or call minutes used. You get the transcript, extracted fields and per-turn latency right after hanging up.',
    tone: 'purple',
  },
  {
    title: 'Campaigns',
    to: '/campaigns',
    cta: 'Open campaigns',
    body:
      'Campaigns run real outbound calls against a contact list, one pinned agent version at a time. Launch, pause or cancel, and watch live progress from the campaign dashboard.',
    tone: 'green',
  },
  {
    title: 'Contacts',
    to: '/campaigns',
    cta: 'Import contacts',
    body:
      'Contacts live inside campaigns. Upload a CSV or Excel list, map its columns once, and the platform validates phone numbers and consent before anyone is called.',
    tone: 'amber',
  },
  {
    title: 'Call Review & Export',
    to: '/campaigns',
    cta: 'Review calls',
    body:
      'Every finished call keeps its full transcript, the structured fields it collected, and cost/latency stats. Review flagged calls and export results to CSV or Excel in one click.',
    tone: 'blue',
  },
  {
    title: 'Compliance & Consent',
    to: '/dev',
    cta: 'View safeguards',
    body:
      'Calls only run inside the permitted calling window, contacts without recorded consent are never dialed, and every call opens with a mandatory AI disclosure. Current limits are shown under Dev Tools.',
    tone: 'green',
  },
  {
    title: 'Dev Tools',
    to: '/dev',
    cta: 'Open dev tools',
    body:
      'Developer-only diagnostics: live service health dots, which provider keys are configured, a browsable API catalog with try-it buttons, and the latency glossary. Removed entirely from production builds.',
    tone: 'red',
  },
];

export default function DashboardPage() {
  return (
    <div>
      <div className="page-head">
        <div>
          <h2 className="page-title">Dashboard</h2>
          <p className="page-sub">
            Everything this platform can do, in one place. Start by building an agent, test it in the Playground, then
            launch it as a campaign.
          </p>
        </div>
        <Link to="/agents/new" className="btn btn-primary">
          + New Agent
        </Link>
      </div>

      <div className="feature-grid">
        {FEATURES.map((f) => (
          <div key={f.title} className={`card feature-card feature-${f.tone}`}>
            <h3 className="feature-title">{f.title}</h3>
            <p className="feature-body">{f.body}</p>
            <Link to={f.to} className="feature-link">
              {f.cta} →
            </Link>
          </div>
        ))}
      </div>

      <div className="banner banner-info dashboard-flow-hint">
        <strong>Suggested first run:</strong> create an agent → save version 1 → talk to it in the Playground →
        create a campaign with contacts → launch inside calling hours.
      </div>
    </div>
  );
}
