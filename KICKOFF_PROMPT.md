## What this file is
This is the actual first message to paste into Claude Code, once `PRD.md`, `CLAUDE.md`, and the `.claude/` folder are sitting in your project root (setup steps in `README_SETUP.md`). Everything below the line is the prompt — copy from there down.

---

Read PRD.md and CLAUDE.md fully before doing anything else.

This is Phase 0 of the project: scaffold only, no feature implementation yet. Do the following, in order, and check in with me between major steps rather than doing everything silently:

1. Confirm you've read PRD.md and CLAUDE.md and briefly summarize back to me: the locked tech stack, the 8 subagents and what each owns, and the current milestone (M0 — scaffold).
2. Create the repo layout described in CLAUDE.md: /backend, /voice-agent, /frontend, /domain-configs, /infra, plus a root .env.example.
3. Delegate to devops-agent to set up docker-compose for local dev (Postgres, Redis, empty backend/voice-agent/frontend service stubs) and populate .env.example with placeholders for every credential we already know we'll need: Plivo (or Exotel), Deepgram, Cartesia, an LLM provider (Groq and/or OpenAI), and Postgres/Redis connection strings.
4. Delegate to backend-agent to scaffold the FastAPI app skeleton and the initial Postgres schema/migration based on PRD.md §6 — models only, no business logic yet.
5. Delegate to voice-pipeline-agent to scaffold a minimal LiveKit Agents service that can join a room and speak one hardcoded line via Cartesia TTS — no STT, no LLM, no telephony yet. The goal of this step is just proving the LiveKit Agents + Cartesia wiring works.
6. Delegate to telephony-agent to scaffold the Plivo integration needed to place a single outbound test call to a number I provide, connecting the audio to the LiveKit Agents service from step 5 — so that by the end of this milestone, a real (test) phone rings and the agent speaks one line.
7. Stop there. Don't build the conversation flow, the frontend, or the campaign dialer yet — that's the next milestone (M1) once step 6 is proven working end-to-end on an actual call.

After each delegated step, report what was created/changed and any decisions the subagent had to make that weren't already specified in PRD.md or CLAUDE.md, so I can confirm or correct them before we move on.
