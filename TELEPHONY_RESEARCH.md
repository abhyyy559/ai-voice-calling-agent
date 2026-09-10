# Telephony Research — EchoSarathi AI Voice Calling (India)

**Status:** recommendation, awaiting approval. **Twilio trial is the BACKUP plan.**
**Usage profile:** website (browser playground) is primary and costs zero telephony; live phone demos are rare. Optimize for pay-as-you-go, no monthly commitments.
**Date:** 2026-09-10. Prices from public rate cards/docs; re-check at purchase time.

## Recommendation (highlighted)

**Primary: Plivo (SIP trunking + LiveKit). Backup: Twilio trial (creds already in `.env`).**

Why Plivo primary:
- Official Plivo ↔ LiveKit integration guide exists (inbound + outbound trunks, TLS/SRTP, `*.zt.plivo.com` termination). LiveKit docs list Plivo alongside Twilio/Telnyx as a supported trunk provider.
- $10 free signup credit, no card required — covers hundreds of demo minutes.
- Cheapest SIP minute rates of the lot (US reference: inbound $0.0028/min, outbound $0.0046/min, local number $0.50/mo; India legs billed in INR, SIP/browser from ~₹0.34/min).
- Repo already has `PlivoClient` + `/plivo/*` webhooks (`backend/app/services/telephony.py`, `backend/app/routers/plivo.py`) — same shape as the Twilio path, so integration is days, not weeks.
- India data region + Mumbai hosting keeps data local (PRD constraint).

Why Twilio stays backup:
- Credentials + US number (`+17372508034`) already in `.env`; `TwilioClient` + `/twilio/*` media-streams bridge already built and closest to working today.
- Trial: 75 voice minutes, calls only to verified numbers (max 5), trial greeting plays, 10-min cap, 30-day expiry. Twilio's own India guidelines: outbound to India must originate from international (non-Indian) numbers — our US number qualifies.
- Paid India ≈ $0.0699/min local — ~10x Plivo SIP. Fine for rare demos, bad as primary.

## Provider comparison

| | Plivo (primary) | Twilio (backup) | Exotel (alt, India-native) | Telnyx/Vonage (not recommended now) |
|---|---|---|---|---|
| Trial/free | $10 credit, no card; ~90-day trial reported | 75 voice min, no card, 30-day expiry | 7-day trial + $5 credit, 1 trial ExoPhone, 10 whitelisted numbers | Free signup, metered from $0.007/min US |
| Number (initial) | US $0.50/mo instant; India 080/022 after KYC (auto-review ~5 min with GST/COI/Udyam + seal) | Trial number free; paid ~$1–2/mo | Trial ExoPhone free; paid plans from ~₹1,000/mo bundles | $1/mo |
| Per-min India outbound | SIP rates in INR from ~₹0.34/min | ~$0.0699/min | ~₹0.80–1.00/min | International deck, no India edge |
| KYC to call YOUR phone | None for US-number demos | Verify number in console (OTP, 2 min) | Whitelist via dashboard OTP (trial) | Verify sender IDs |
| KYC for production India | Company doc + seal (same as all India PSTN) | Same TRAI/DoT rules apply | 1–3 business days, business email + PAN/GST | Weak India story |
| LiveKit guide | Official inbound+outbound SIP guide | Official SIP + TwiML guides | AgentStream WS voicebot API (custom work) | Official SIP guides |
| Repo status | Client + webhooks exist (fallback) | Client + media bridge exist (primary today) | No client — new integration | No client — new integration |
| AI-voice fit | Purpose-built SIP-for-agents page, TLS/SRTP, unlimited channels | Media Streams `<Stream>` works, trial message interrupts demo feel | Enterprise IVR strength, agent streaming is newer | Great tech, no India presence |

Rough demo math (5-min call): Twilio paid ≈ $0.35 · Plivo SIP ≈ $0.03–0.05 · Exotel ≈ ₹4–5. At "rare demos" volume, all are pocket change — decide on KYC speed and integration cost, not minutes.

## What "a call to my phone" needs (any provider)

1. Provider account + a caller-ID number (trial/verified OK for demos).
2. Backend reachable from the public internet — webhooks + media WS can't point at `localhost`. Demo: `ngrok http 8000` → set `PUBLIC_BASE_URL` / `PUBLIC_WS_BASE_URL` in `.env` → restart backend.
3. `POST /api/test-call` with your contact card (target must be in `TEST_PHONE_NUMBERS`; consent enforcement auto-bypasses allowlisted numbers as `test_allowlist`).
4. Answer the phone; the same agent from the playground talks (STT→LLM→TTS over the provider media stream bridged into the LiveKit room).

## Deployment plan

**Phase A — demo today (this session, ~30 min after approval):**
- Twilio backup path (zero new integration): verify `+917842594002` in Twilio Console → `ngrok http 8000` → set public URLs in `.env` → `docker compose up -d backend` → `POST /api/test-call` → phone rings.
- Fallback if Twilio trial is exhausted: Plivo US-region signup ($10 credit) → rent US number (instant, no KYC) → set `PLIVO_*` in `.env` → same test-call flow over the Plivo router.

**Phase B — production (Mumbai, when demos become pilots):**
- VPS in `ap-south-1` (or DigitalOcean BLR) running this same `infra/docker-compose.yml`, real domain + TLS (replaces ngrok), LiveKit Cloud Mumbai or self-hosted with SIP service.
- Plivo India-region account → KYC (GST/Udyam + seal) → rent 080/022 number → service/transactional voice; 140/160-series + DLT registration only when running promotional or BFSI traffic.
- Keep Twilio as provider-level fallback in `telephony.py` (already abstracted) + the STT/LLM/TTS fallback chains from the platform plan.

## Compliance notes (India, non-negotiable for production)

- DLT registration before any non-test traffic; test allowlist (`TEST_PHONE_NUMBERS`) + `consent_source=test_allowlist` is the only bypass, and only for your own verified numbers.
- Calling hours 9:00–21:00 Asia/Kolkata enforced by dialer config; recording retention 90 days; never place campaign calls from this research flow — only single consented test calls.

## Decision required

- [ ] Approve **Plivo primary / Twilio backup** (recommended), or
- [ ] Approve **Twilio-only** (fastest today, keep Plivo later), or
- [ ] Pick **Exotel** (if a company KYC pack is ready and India-native billing matters more than integration speed).

After approval: I wire the chosen path (env + public URL + test call) and report the live-call result in this same session.
