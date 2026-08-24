import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { getToken } from '../api.js';

const STEPS = [
  {
    n: '1',
    title: 'Create & train an agent',
    body:
      'Describe who the agent calls and why: its questions, the fields it should note down, and its voice. Every save creates a numbered version you can roll back to.',
  },
  {
    n: '2',
    title: 'Test it live in your browser',
    body:
      'Talk to your agent straight from your microphone — no phone numbers or call minutes used. Watch live captions, then review the transcript and extracted details.',
  },
  {
    n: '3',
    title: 'Launch campaigns & review transcripts',
    body:
      'Upload a contact list as CSV or Excel, launch the campaign inside permitted calling hours, and watch progress live. Export transcripts and results anytime.',
  },
];

export default function LandingPage() {
  // Already signed in? The landing page is only for logged-out visitors.
  if (getToken()) return <Navigate to="/" replace />;

  return (
    <div className="landing">
      <header className="land-top">
        <div className="land-brand">
          <div className="brand-mark">V</div>
          <div>
            <div className="brand-name">VocalIQ</div>
            <div className="brand-sub">Voice calling console</div>
          </div>
        </div>
        <nav className="land-actions" aria-label="Account">
          <Link className="btn btn-secondary" to="/login">
            Log in
          </Link>
          <Link className="btn btn-primary" to="/login" state={{ mode: 'register' }}>
            Register
          </Link>
        </nav>
      </header>

      <main className="land-main">
        <section className="land-hero">
          <span className="land-eyebrow">AI voice calling for teams in India</span>
          <h1 className="land-title">Build AI voice agents that talk to your customers</h1>
          <p className="land-tagline">
            Train them here, hear them speak, then launch calling campaigns.
          </p>
          <div className="land-cta-row">
            <Link className="btn btn-primary btn-lg" to="/login" state={{ mode: 'register' }}>
              Get started free
            </Link>
            <Link className="btn btn-secondary btn-lg" to="/login">
              Log in
            </Link>
          </div>
        </section>

        <section className="land-steps" aria-label="How it works">
          <h2 className="land-section-title">How it works</h2>
          <p className="land-section-sub">Three steps from idea to a campaign that dials real people.</p>
          <div className="land-steps-grid">
            {STEPS.map((s) => (
              <div key={s.n} className="land-step-card">
                <div className="land-step-num">{s.n}</div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="land-footer">
        <span>English-first · India launch</span>
        <span className="land-footer-dot" aria-hidden="true">
          ·
        </span>
        <span>Calls run only inside permitted calling hours with recorded consent.</span>
      </footer>
    </div>
  );
}
