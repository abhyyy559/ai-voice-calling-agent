# How to use this package

## What's in here
```
PRD.md                                the spec — what to build, in what order, and why
CLAUDE.md                             project memory Claude Code reads every session
KICKOFF_PROMPT.md                     the literal first message to paste into Claude Code
.claude/agents/*.md                   8 subagents, one per project layer
.claude/commands/*.md                 3 slash commands (/new-domain-flow, /latency-check, /compliance-check)
```
(`AI_Voice_Calling_Agent_India_Research.md` from the earlier research turn is the market/vendor research these decisions are based on — keep it in the repo root too, `CLAUDE.md` and `PRD.md` both reference it.)

## Setup steps
1. Create a new empty git repo for the project (or use an existing empty one).
2. Copy every file in this package into the repo root, preserving the folder structure — `PRD.md`, `CLAUDE.md`, `KICKOFF_PROMPT.md`, `README_SETUP.md`, and the whole `.claude/` folder (including `.claude/agents/` and `.claude/commands/`) go at the repo root, not nested inside another folder.
3. Also drop `AI_Voice_Calling_Agent_India_Research.md` into the repo root.
4. `git add . && git commit -m "project scaffold: PRD, CLAUDE.md, subagents"` — commit this before running Claude Code, so the setup itself is version-controlled.
5. Open Claude Code in this repo directory.
6. Paste the contents of `KICKOFF_PROMPT.md` (everything below the `---` line) as your first message.

## Things to have ready before you start
- Plivo (or Exotel) account + API credentials, and a phone number you can safely receive test calls on.
- Deepgram API key.
- Cartesia API key.
- An LLM API key — Groq is the recommended default for cost/latency (see PRD.md §3); OpenAI/Anthropic as an alternative.
- Decide who's answering the "open questions" in PRD.md §11 (retention period, DLT classification) before Milestone M3 — these need a person, not code.

## A note on subagent behavior
Claude Code loads `.claude/agents/*.md` at session start — if you edit an agent file mid-session, restart the session to pick up the change. Claude will generally pick the right subagent automatically based on each one's `description` field, but you can always force it: "use the backend-agent to add a migration for X."

## When you're ready for Telugu (Phase 2)
Don't start this early. When you get there, it's worth writing a short Phase-2 addendum to `PRD.md` (Telugu-specific NFRs, Sarvam integration details) and possibly a 9th subagent (`localization-agent`) scoped narrowly to the Sarvam STT/TTS swap — reuse `voice-pipeline-agent` and `conversation-ai-agent` for everything else rather than duplicating them.
