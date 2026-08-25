# Phase 1 Finish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every finishable Phase 1 item — ship the cost-dashboard UI card, add the landing-page motion pass, verify everything green, and refresh status docs.

**Architecture:** Finish half-built in-flight cost work (backend `/api/analytics/costs` already written uncommitted; only the Overview UI card is missing), add a CSS-only scroll-reveal layer to the landing page, then run integration verification and land three logical commits. Two frontend units touch disjoint files and run in parallel.

**Tech Stack:** FastAPI + SQLAlchemy + pytest (backend, venv at `backend\.venv`), React 18 + Vite (frontend, no test runner — `npm run build` is the gate), plain CSS design system in `frontend/src/styles.css`.

## Global Constraints

- Build ON TOP of existing uncommitted working-tree changes; never revert or stash-drop them (`git status` shows: `analytics.py`, `schemas.py`, `api.js`, `OverviewPage.jsx` modified; `backend/tests/test_costs.py` untracked).
- Zero new npm dependencies. Zero new API endpoints. No auth changes.
- Respect `prefers-reduced-motion`; all animation CSS lives behind that media query.
- Use the existing dark token palette (`--accent #6366f1`, `--accent2 #22d3ee`, surfaces/borders from `:root` in `styles.css`) — no hardcoded light colors anywhere.
- File boundaries: Task 2 touches ONLY `frontend/src/pages/OverviewPage.jsx`. Task 3 touches ONLY `frontend/src/hooks/useReveal.js` (new), `frontend/src/pages/LandingPage.jsx`, `frontend/src/styles.css` (append-only).
- Shell is Windows PowerShell 5.1. Backend tests: run from `backend/` with `.. \backend\.venv\Scripts\python.exe -m pytest` equivalent — exact commands below. Frontend: `npm run build` from `frontend/`.
- Commits happen only in Task 4/5 by the orchestrator, after gates pass.

## Key interface (already exists, consumed verbatim)

`analyticsApi.costs()` → `GET /api/analytics/costs` (JWT-authed) returns:

```json
{
  "total_minutes": 13.0,
  "est_cost_usd": 0.325,
  "per_call": [{ "call_id": 1, "minutes": 2.0, "est_cost_usd": 0.05 }],
  "monthly": { "2026-08": { "minutes": 3.0, "est_cost_usd": 0.075 } }
}
```

Month keys are `"YYYY-MM"` in UTC (`new Date().toISOString().slice(0, 7)` on the client matches the server's `strftime("%Y-%m")` closely enough for display; both are UTC-day-based buckets).

---

### Task 1: Verify in-flight backend cost endpoint (orchestrator, no edits expected)

**Files:** none modified. Read-only verification of `backend/app/routers/analytics.py`, `backend/app/schemas.py`, `backend/tests/test_costs.py`.

**Interfaces:**
- Consumes: nothing new.
- Produces: confidence that `/api/analytics/costs` + `AnalyticsCostsOut` are correct before UI rides on them.

- [ ] **Step 1: Run the two cost tests in isolation**

Run (workdir: `backend`):
```powershell
.venv\Scripts\python.exe -m pytest tests\test_costs.py -v
```
Expected: `2 passed` (`test_costs_endpoint_org_scoped`, `test_costs_requires_auth`). If FAIL: read the assertion, fix `analytics.py` minimally (endpoint logic already mirrors the test), re-run until green. Do not weaken assertions.

- [ ] **Step 2: Run the FULL backend suite**

Run (workdir: `backend`):
```powershell
.venv\Scripts\python.exe -m pytest -q
```
Expected: baseline 77 + 2 new = **79 passed**, 0 failed.

---

### Task 2: Cost-dashboard stat card on Overview (frontend-agent)

**Files:**
- Modify: `frontend/src/pages/OverviewPage.jsx` (only this file)

**Interfaces:**
- Consumes: `analyticsApi.costs()` from `../api.js` (already imported there; `costs` state + `monthCosts` variable ALREADY EXIST in the component around lines 43 and 71-72 — reuse them, do not re-create).
- Produces: rendered "Est. Spend" card; nothing downstream depends on it.

- [ ] **Step 1: Insert the Est. Spend card**

In `OverviewPage.jsx`, find the end of the "Fields Captured" StatCard (line ~136):

```jsx
<StatCard label="Fields Captured" value={summary.total_extracted_fields} foot={<span>structured values extracted</span>} />
```

Insert immediately AFTER it, still inside the `.stat-grid` div:

```jsx
            <StatCard
              label="Est. Spend"
              value={monthCosts ? `$${monthCosts.est_cost_usd.toFixed(2)}` : costs ? '$0.00' : '—'}
              foot={
                <span>
                  {monthCosts
                    ? `${monthCosts.minutes.toLocaleString()} min this month`
                    : 'no billable minutes yet'}{' '}
                  · telephony+STT+LLM+TTS @ ~$0.025/min est.
                </span>
              }
            />
```

Semantics: costs loaded but empty month → `$0.00`; fetch failed (`costs === null`) → `—`; loaded with data → dollars + minutes. No error banner ever (silent fallback per spec).

- [ ] **Step 2: Verify the production build**

Run (workdir: `frontend`):
```powershell
npm run build
```
Expected: exit 0, `✓ built in …s`. Any JSX syntax error fails here.

- [ ] **Step 3: Report back**

Do NOT commit. Report: build result + the exact lines inserted.

---

### Task 3: Landing page scroll-reveal motion pass (frontend-agent, parallel with Task 2)

**Files:**
- Create: `frontend/src/hooks/useReveal.js`
- Modify: `frontend/src/pages/LandingPage.jsx`
- Modify: `frontend/src/styles.css` (append-only, end of file)

**Interfaces:**
- Consumes: nothing.
- Produces: `useReveal()` hook — returns a React ref; attach it to any container; every descendant with `[data-reveal]` gets class `revealed` once it enters the viewport (one-way, then unobserved).

- [ ] **Step 1: Create the hook**

Create `frontend/src/hooks/useReveal.js` with exactly:

```js
import { useEffect, useRef } from 'react';

/**
 * Scroll-reveal: returns a ref for a container element. Every descendant
 * carrying `[data-reveal]` gets the `revealed` class the first time it
 * enters the viewport (one-way). Falls back to instantly-visible when
 * IntersectionObserver is unavailable.
 */
export default function useReveal() {
  const ref = useRef(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) return undefined;
    const targets = Array.from(root.querySelectorAll('[data-reveal]'));
    if (targets.length === 0 || !('IntersectionObserver' in window)) {
      targets.forEach((el) => el.classList.add('revealed'));
      return undefined;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 },
    );
    targets.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  return ref;
}
```

- [ ] **Step 2: Wire it into LandingPage.jsx**

Three edits to `frontend/src/pages/LandingPage.jsx`:

(a) After line 3 (`import { getToken } from '../api.js';`) add:

```js
import useReveal from '../hooks/useReveal';
```

(b) Inside `export default function LandingPage() {` — BEFORE the early-return `if (getToken())` line — add:

```js
  const revealRef = useReveal();
```

(Hooks must run unconditionally; placing it before the early return keeps React's rules-of-hooks satisfied.)

(c) Change the outer container opening tag from:

```jsx
    <div className="landing">
```

to:

```jsx
    <div className="landing" ref={revealRef}>
```

(d) Mark hero children — add `data-reveal` to these four existing elements:

```jsx
<span className="land-eyebrow" data-reveal>AI voice calling for teams in India</span>
<h1 className="land-title" data-reveal>Build AI voice agents that talk to your customers</h1>
<p className="land-tagline" data-reveal>
  Train them here, hear them speak, then launch calling campaigns.
</p>
<div className="land-cta-row" data-reveal>
```

(e) Stagger the three step cards — change the `STEPS.map` block to:

```jsx
            {STEPS.map((s, i) => (
              <div key={s.n} className="land-step-card" data-reveal style={{ transitionDelay: `${i * 90}ms` }}>
                <div className="land-step-num">{s.n}</div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </div>
            ))}
```

- [ ] **Step 3: Append the motion CSS**

Append to the END of `frontend/src/styles.css`:

```css
/* ==========================================================================
   Landing motion — scroll-reveal + glass accents
   Animation gated behind prefers-reduced-motion: no-preference.
   ========================================================================== */

.land-step-card,
.land-hero .land-eyebrow {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

@media (prefers-reduced-motion: no-preference) {
  [data-reveal] {
    opacity: 0;
    transform: translateY(14px);
    transition:
      opacity 0.55s ease,
      transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
    will-change: opacity, transform;
  }

  [data-reveal].revealed {
    opacity: 1;
    transform: none;
  }
}
```

Note: with reduced-motion, `[data-reveal]` never gets hidden styles, so content is always visible — the `revealed` class becomes a harmless no-op.

- [ ] **Step 4: Verify the production build**

Run (workdir: `frontend`):
```powershell
npm run build
```
Expected: exit 0. (If Task 2 landed concurrently and broke something unrelated to these files, report it — do not fix OverviewPage.)

- [ ] **Step 5: Report back**

Do NOT commit. Report: build result + files created/modified.

---

### Task 4: Integration verification + the three feature commits (orchestrator)

**Files:** commits only; no source edits expected.

**Interfaces:**
- Consumes: Tasks 1-3 outputs all green.
- Produces: commits `feat(p1-costs)`, `feat(landing)`.

- [ ] **Step 1: Full backend suite once more**

Run (workdir: `backend`):
```powershell
.venv\Scripts\python.exe -m pytest -q
```
Expected: `79 passed`.

- [ ] **Step 2: Frontend build once more**

Run (workdir: `frontend`):
```powershell
npm run build
```
Expected: exit 0.

- [ ] **Step 3: Commit unit 1 — cost dashboard (backend endpoint + test + frontend wiring)**

Run (repo root):
```powershell
git add backend/app/routers/analytics.py backend/app/schemas.py backend/tests/test_costs.py frontend/src/api.js frontend/src/pages/OverviewPage.jsx
if ($?) { git commit -m "feat(p1-costs): estimated-spend card on Overview (/api/analytics/costs)" }
```

- [ ] **Step 4: Commit unit 2 — landing motion**

Run (repo root):
```powershell
git add frontend/src/hooks/useReveal.js frontend/src/pages/LandingPage.jsx frontend/src/styles.css
if ($?) { git commit -m "feat(landing): scroll-reveal motion pass (reduced-motion safe)" }
```

---

### Task 5: Docs refresh + closeout commit (orchestrator)

**Files:**
- Modify: `PROJECT_STATUS.md`
- Modify: `PROJECT_LOG.md`

- [ ] **Step 1: Update PROJECT_STATUS.md**

(a) Replace the header line:
```
Last updated: 2026-08-25 · Phase: **1 (Web) COMPLETE** · Head: `3abc15e`
```
with:
```
Last updated: 2026-08-25 · Phase: **1 COMPLETE (closed out)** · See `git log` for head.
```

(b) In §3 "Pending — P0", tick the boxes and annotate:
```
- [x] **P0-1 STT latency**: DONE — Deepgram `endpointing_ms=200` shipped (commit `7d28763`); EOU vs transcription delay split logged in turn_latency. Fresh live measurement still owed at next test-call session.
- [x] **P0-2 Personalized opening**: DONE end-to-end (commit `6b24f86`) — contact fields persist on calls.context, packed into room/token metadata, CALLER CONTEXT prompt section + verify-relationship rule in voice + text modes, migration 0003.
- [x] **P0-3 Strict-guardrails block** in every prompt: refuse off-topic questions ("Who is India's PM?"), never disclose other students' data, wrap up fast (calls cost money), offer human handoff when caller drifts or demands more help
- [x] **P0-4 Caption lag in audio mode**: publish partial transcripts (not just finals) over the data channel
- [ ] **P0-5 Groq Dev tier** (owner action) to remove p95 spikes + TPM 429s
```

(c) In §4 "Pending — P1", tick what shipped today and leave the blocked one:
```
- [x] Cost dashboard: org-scoped GET /api/analytics/costs + "Est. Spend" card on Overview ($/min constants in analytics.PRICING_USD_PER_MINUTE — update per invoice)
- [x] Export v2 columns: call status/duration/extracted fields/custom fields + E2E Latency column (shipped commit `0d3087f`)
- [x] Landing page motion pass: scroll-reveal + glassmorphism accents, prefers-reduced-motion safe (public mic demo intentionally deferred — new auth surface)
- [x] Frontend container healthcheck IPv6 false-negative fix
- [ ] Parallel outbound calling demo (3–4 simultaneous) — BLOCKED on owner: Twilio keys/tunnel; dialer concurrency already built
```

(d) Append at the end of the file:

```markdown
## Update 2026-08-25 (closeout #2)

- [x] P0-1/P0-2 marked done (were committed in 7d28763 / 6b24f86; doc lagged)
- [x] P1 cost dashboard shipped: /api/analytics/costs + Overview "Est. Spend" card (79 backend tests green)
- [x] P1 landing motion pass shipped (useReveal hook + CSS reveal layer, zero deps)
- [ ] Owner-blocked: P0-5 Groq Dev tier, Twilio keys for parallel-calls demo
- [ ] Next up (needs owner go-ahead): Phase 2 roadmap (Telugu/Sarvam, BYO providers, phone purchasing, live transfer, auth hardening)
```

- [ ] **Step 2: Append PROJECT_LOG.md entry**

Append to the END of `PROJECT_LOG.md`:

```markdown

---

## 2026-08-25 — Phase 1 closeout (cost dashboard + landing polish)

- **Cost dashboard**: backend `GET /api/analytics/costs` (org-scoped, monthly buckets, flat $/min pricing consts) + "Est. Spend" stat card on Overview. Rates are estimates — update `PRICING_USD_PER_MINUTE` per provider invoices.
- **Landing motion**: `useReveal` IntersectionObserver hook, staggered step-card reveals, glassmorphism accents; fully disabled under `prefers-reduced-motion`.
- **Verification**: 79/79 backend tests, `vite build` clean.
- **Still owner-blocked**: Groq Dev tier (P0-5), Twilio keys/tunnel (parallel-calls demo).
- Design spec: `docs/superpowers/specs/2026-08-25-phase1-finish-design.md`.
```

- [ ] **Step 3: Commit unit 3 — docs**

Run (repo root):
```powershell
git add PROJECT_STATUS.md PROJECT_LOG.md docs/superpowers/specs/2026-08-25-phase1-finish-design.md docs/superpowers/plans/2026-08-25-phase1-finish.md
if ($?) { git commit -m "docs(status): phase-1 closeout - cost dashboard + landing motion shipped" }
```

(Note: the spec amendment — Unit B boundary extended to include `styles.css` — is folded into this commit.)

- [ ] **Step 4: Final state check**

Run:
```powershell
git status --short; git log --oneline -5
```
Expected: working tree clean (except untracked runtime artifacts ignored by .gitignore), last 5 commits ending with the docs closeout.
