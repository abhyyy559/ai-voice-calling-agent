# Phase 1 Finish — Design

Date: 2026-08-25 · Status: Approved by owner · Execution: subagent-driven

## Goal

Close every Phase 1 item that can be finished in code this session. Owner-blocked items
(Groq Dev tier upgrade, Twilio keys/tunnel for the parallel-calls demo, real DLT
registration) are explicitly out of scope.

## Current state (verified before design)

- Working tree contains uncommitted, half-finished cost-dashboard work:
  - `backend/app/routers/analytics.py` — new `/api/analytics/costs` endpoint +
    `PRICING_USD_PER_MINUTE` constants (complete)
  - `backend/app/schemas.py` — `AnalyticsCostsOut`, `PerCallCostOut`, `MonthlyCostOut`
    (complete)
  - `frontend/src/api.js` — `analyticsApi.costs()` added (complete)
  - `frontend/src/pages/OverviewPage.jsx` — costs state + fetch wired;
    **UI card missing** (`monthCosts` computed but never rendered)
  - `backend/tests/test_costs.py` — untracked, unverified
- P0-1 (STT endpointing) and P0-2 (personalized opening) were committed earlier
  (`7d28763`, `6b24f86`) but PROJECT_STATUS.md still lists them as open.
- Export v2 columns already landed (`0d3087f`) with test coverage.
- Baseline: 77 backend tests green; frontend builds clean.

## Work units

### Unit A — Cost-dashboard UI card (frontend-agent)

File boundary: `frontend/src/pages/OverviewPage.jsx` only.

- Render one "Est. spend this month" stat card using the existing `StatCard`
  component / dark indigo-cyan token palette.
- Shows current-month bucket from `costs.monthly[YYYY-MM]`: `est_cost_usd`
  (primary) and `total_minutes` (foot).
- Footnote: rate basis ("telephony+STT+LLM+TTS @ ~$0.025/min est.").
- Silent fallback when fetch fails or org has no calls yet (state already null-safe).
- Builds on top of the existing uncommitted changes; must not revert them.

### Unit B — Landing motion pass (frontend-agent, parallel with A)

File boundary: `frontend/src/pages/LandingPage.jsx` plus at most one new small hook
file (e.g. `src/hooks/useReveal.js`). No other files.

- Scroll-reveal fade/rise on hero and feature cards via IntersectionObserver.
- Glassmorphism accents consistent with existing token palette.
- Honors `prefers-reduced-motion` (no animation when set).
- Zero new npm dependencies, zero new endpoints.

### Unit C — Backend verification (main session)

- Run full backend suite: `backend\.venv\Scripts\python.exe -m pytest` from `backend/`.
- Confirm `test_costs.py` passes; fix only if red (expected green — endpoint was
  written against the test).
- No file edits expected.

### Unit D — Integration verification (main session)

- Frontend production build after both agents land: `npm run build` in `frontend/`.
- Full backend suite re-run once more (cheap, catches cross-unit surprises).

### Unit E — Docs refresh (main session)

`PROJECT_STATUS.md`:

- Mark P0-1 and P0-2 done (committed earlier), keep P0-5 owner-blocked.
- Mark P1 done: cost dashboard, export v2 (already shipped), landing motion pass,
  healthcheck fix.
- Keep parallel-outbound-calls demo listed as blocked on Twilio keys.
- Date-stamped update entry for today's work.

`PROJECT_LOG.md`: short dated entry mirroring the same deltas.

## Verification gates (all must pass before commits)

1. Backend pytest suite fully green (including `test_costs.py`).
2. `npm run build` exits clean.

## Commits (3, logical units)

1. `feat(p1-costs): estimated-spend card on Overview` — analytics UI wiring files
   (`OverviewPage.jsx`, `api.js`) + backend cost files (`analytics.py`, `schemas.py`,
   `tests/test_costs.py`).
2. `feat(landing): scroll-reveal motion pass` — LandingPage + reveal hook.
3. `docs(status): phase-1 closeout` — PROJECT_STATUS.md, PROJECT_LOG.md.

## Out of scope

P0-5 Groq Dev tier · parallel outbound calling demo (Twilio keys) · DLT registration ·
Phase 2 roadmap (Telugu/Sarvam, BYO providers, phone purchasing, live transfer,
auth hardening) · any refactor beyond the named files.

## Risks & mitigations

- Two frontend agents in parallel: disjoint file sets (`OverviewPage.jsx` vs
  `LandingPage.jsx`); integration build in Unit D catches anything either broke.
- Uncommitted work could be clobbered: every agent instruction explicitly says
  "build on top of existing working-tree changes; do not revert."
- Cost numbers are estimates by design (flat $/min constants); card copy says
  "est." so nobody mistakes it for invoiced reality.
