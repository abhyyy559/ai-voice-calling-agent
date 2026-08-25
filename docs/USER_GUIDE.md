# User Guide — AI Voice Calling Agent

A beginner-friendly guide to the platform. No technical background needed —
every screen is explained in plain English, and every step below is something
you can do from your browser.

---

## 1. What is this product?

This platform lets you build an **AI voice agent** — a computer voice that can
phone people (or talk in your browser), hold a natural conversation in
English, ask a set of questions you define, and write down the answers in an
organised table.

**Typical use:** a college wants to call students who missed classes. Instead
of staff dialling dozens of numbers, you upload the list, and the AI calls each
student, politely asks what happened, records their reason, and gives you a
neat spreadsheet at the end. The same recipe works for surveys, appointment
reminders, lead qualification — it's all configuration, not new software.

Everything runs on Indian infrastructure and respects Indian rules: calls only
go out between **9 AM and 9 PM IST**, and consent is tracked for every contact.

---

## 2. The Golden Path (start to finish)

Follow these steps in order. Each one builds on the previous.

### Step 0 — Open the app and sign up

1. Start the local stack (one command):
   ```
   powershell -ExecutionPolicy Bypass -File scripts\dev-local.ps1
   ```
2. Open **http://localhost:3000** in Chrome or Edge.
3. Click **Sign up** and fill in three fields:
   * **Organisation name** — your company/college name; everything you create
     belongs to this organisation and is invisible to other organisations.
   * **Email** + **Password** — this becomes the owner login.

   > Demo shortcut: log in with `demo@example.com` / `demo1234` to explore a
   > pre-seeded account.

### Step 1 — Dashboard tour

After logging in you land on the **Dashboard**. In plain English:

* A row of **feature cards** acts as a map of the product: Agents, Playground,
  Campaigns, Calls, Dev Tools.
* Status tiles show whether the voice services behind the scenes are healthy
  (LiveKit, speech-to-text, text-to-speech, the LLM brain).
* If anything is red here, jump to [Troubleshooting](#4-troubleshooting) —
  the rest of the path won't work until providers are green.

### Step 2 — Create an agent ("train your caller")

An **agent** is your phone-caller persona. Click **Agents → New Agent** and
walk through six short steps:

| # | Step | What it means (one sentence) |
|---|------|------------------------------|
| 1 | **Basics** | Name your agent and describe in one line what it's for. |
| 2 | **Company Context** | Paste background facts the agent should know (e.g. "We are ABC College calling about attendance"). |
| 3 | **Question Flow** | Write the ordered questions the agent asks, with follow-ups allowed. |
| 4 | **Extraction Schema** | Define the answer fields to capture per call (e.g. `reason`, `will_return_date`) so results land in tidy columns. |
| 5 | **Voice Settings** | Choose how the agent sounds and speaks (voice style and pace). |
| 6 | **Review & Save Version** | Check everything, then click save — this freezes a numbered version. |

> **Versions matter:** a saved version never changes, even if you edit the
> agent later. Campaigns pin a version, so a running campaign always behaves
> exactly as tested.

### Step 3 — Test-drive it in the Playground (no phones involved)

The **Playground** is a browser-to-browser call with your agent — free,
instant, and nothing is dialed anywhere.

1. Open your agent's page and click **Test in Playground**.
2. Your browser asks for **microphone permission — click Allow**. Without it
   the agent cannot hear you (see troubleshooting).
3. Talk naturally: introduce yourself, let the agent ask its questions, answer
   out loud. You'll see live captions as you speak, then:
   * the full **transcript** of the conversation,
   * the **extracted fields** it filled from your schema,
   * **latency** figures showing how fast the agent reacts.

If the conversation feels wrong, edit the agent, save a **new version**, and
test again. Only move on when the playground conversation feels right.

### Step 4 — Create a campaign

A **campaign** = one contact list + one pinned agent version + one launch.

1. Go to **Campaigns → + New Campaign**, give it a name, pick your agent
   (its current version), click **Create campaign**.
2. On the campaign page, open the **Contacts** tab and upload a CSV or XLSX:
   * The system **auto-detects columns** — it looks for a phone column and a
     name column automatically and shows its guess; adjust if needed.
   * There's a review step: fix or drop rows marked invalid before anything
     is called.
3. Contacts arrive in *pending review* status. Rows without recorded consent
   stay parked there even after launch — that's the compliance gate working
   as designed.

### Step 5 — Launch (and why it may say no)

Click **Launch campaign**. Two built-in guardrails decide whether calls start:

* **Calling window:** outbound calls only run between **9 AM and 9 PM IST**.
  Outside that window the Launch button explains itself instead of failing
  mysteriously — come back during the window.
* **Telephony:** real outbound dialing needs a telephony provider connected.
  **Right now that isn't switched on yet, so campaigns cannot place real
  calls** — launching will be blocked until the provider is enabled and the
  compliance checklist is complete. This is temporary and deliberate; the UI
  will tell you plainly once it changes.

While a campaign runs, the **Dashboard tab** shows live counters (calling /
completed / failed / no-answer) and recent calls.

### Step 6 — Review results and export

When calls finish:

* Open any call from the campaign dashboard to read the full **transcript**
  and the **extracted field values** captured from the person.
* Use the **Export → CSV / XLSX** buttons on the campaign page to download
  everything as a spreadsheet.

---

## 3. Daily cheat-sheet

| I want to… | Do this |
|---|---|
| Start everything locally | `powershell -ExecutionPolicy Bypass -File scripts\dev-local.ps1` |
| Try the AI without calling anyone | Agents → your agent → Test in Playground |
| Change what the agent says | Edit agent → save → a new version number appears |
| See who was called and what they said | Campaign → Dashboard tab → click a call |
| Get results into Excel | Campaign page → Export → XLSX |

---

## 4. Troubleshooting

| Symptom | Likely cause & fix |
|---|---|
| Browser never asks for mic, or agent says "I can't hear you" | Microphone permission denied earlier. Click the lock/tune icon in the address bar → allow microphone → reload the Playground page. Also check no other app has exclusive use of the mic. |
| "Port already in use" / a service won't start | Something else owns :8000 (backend), :7880 (LiveKit) or :3000 (frontend). Close the old process or reboot; `scripts\dev-local.ps1` deliberately skips ports that are already listening, so a stale half-dead service must be killed by hand. |
| Dashboard shows a provider toggle as **false** (or Playground fails to start) | One API key is missing/wrong in the root `.env`. Which key: the toggle name maps to it — e.g. `deepgram` false → `DEEPGRAM_API_KEY`, `cartesia` false → `CARTESIA_API_KEY`, `groq`/`llm` false → `GROQ_API_KEY`. Fix the value, restart the backend + worker. |
| Agent joins the Playground but stays silent / session times out | The worker isn't registered with LiveKit. Open `worker_out.log` in the repo root — if it shows connection errors or nothing new, restart the stack with `scripts\dev-local.ps1`. |
| Launch says "outside calling hours" | It's before 9 AM or after 9 PM IST. That's a rule, not a bug — try again inside the window. |
| Launch says contacts missing | Upload the contact list on the campaign's Contacts tab first; rows marked invalid don't count. |
| Login loops back to the sign-in page | The backend isn't reachable. Check http://127.0.0.1:8000/api/health responds; if not, restart via the launcher script and check `logs\backend_err.log`. |

---

## 5. What's next / coming soon

* **Real outbound calls** — once the telephony provider is enabled and the
  India compliance gate (DLT registration + consent flow) clears, the Launch
  button starts actual dialing to your approved test list first.
* **More languages** — Telugu and other Indic-language support is planned as
  the next phase; today the agents speak English only.
* Richer analytics, retry policies for unanswered calls, and team member roles
  beyond owner/admin are also on the roadmap.

*Found a gap in this guide? Tell the team — this file lives at
`docs/USER_GUIDE.md`.*

## Real phone test call (Twilio beta)

Prereqs in `.env`: TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_PHONE_NUMBER,
destination mobile verified in the Twilio console (trial rule), plus a public tunnel:

    cloudflared tunnel --url http://localhost:8000

Put the printed https URL into `.env` as PUBLIC_BASE_URL=... , restart backend
(`docker compose -f infra/docker-compose.yml up -d backend --force-recreate`),
open UI -> Test Call -> enter your verified number -> Start. Answer the phone;
the Twilio trial preamble plays first, then the agent disclosure. Hang up from
either side; view transcript + export XLSX from Call Detail.
