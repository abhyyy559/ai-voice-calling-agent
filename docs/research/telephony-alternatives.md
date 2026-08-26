# Telephony Alternatives: Cutting VocalIQ's Biggest Cost Line — Legally

**Date:** 26 Aug 2026 · **Purpose:** options doc for slashing per-minute telephony spend on outbound AI voice calls terminating in India. All prices ex-GST unless noted; INR unless marked `$`. Every claim is cited inline with a source date. List prices are negotiation anchors, not quotes — re-verify before any contract.

---

## 0. TL;DR

| Question | Answer |
|---|---|
| Where does the money go today? | On Twilio we pay roughly **₹1.55–1.60/effective minute**: voice ~₹0.65–1.50/min + Media Streams $0.0044/min ≈ ₹0.37/min + recording/AMD extras. |
| Biggest single legal saving | **Move India legs to Plivo-class domestic routing: ₹0.38/min, audio streaming free → ~75% cut** (plivo.com/voice/pricing/in, retrieved Aug 2026). At 100k calls/mo ≈ **₹3.5 lakh/month avoided**. |
| Endgame rate | Direct carrier SIP (Jio/Tata/Airtel) lands at **~₹0.30–0.45/min all-in**, but only pays off around **20 lakh+ minutes/month** (caller.digital, 23 Jun 2026). |
| Cheapest legal ₹/min | **≈ ₹0.30–0.38/min telephony-only at scale. ₹0 is impossible** — PSTN termination is always billed by licensed access providers; DLT/KYC/DID carry non-zero floors (§6). |
| Legal landmine | Grey routes / SIM banks / eSIM banks are **criminal risk** (arrests Jan 2026; DoT shut 44 illegal exchanges Apr 2026), and the Feb 2025 TCCCPR amendment lets carriers bar our *entire legal* SIP trunk for 15 days on a first UCC violation (§2). |

---

## 1. The landscape: ways to buy Indian telephony minutes

### 1.1 Comparison table

Outbound calls to Indian mobiles assumed (our dominant cost); ~3 min avg/call.

| Dimension | **Global CPaaS (Twilio)** | **India CPaaS (Plivo)** | **India CPaaS (Exotel)** | **India CCaaS (Ozonetel / Knowlarity–Gupshup)** | **Direct carrier SIP (Airtel/Jio/Tata)** | **Self-hosted PBX + carrier SIP** |
|---|---|---|---|---|---|---|
| Outbound rate, India mobile | ~₹0.65 landline, **~₹1.20–1.50 mobile** (edesy.in, Jan 2026; frejun.com Voice API guide, May 2026) | **₹0.38/min** out & in (plivo.com/voice/pricing/in, retrieved Aug 2026) | Credit-based (~₹1/credit), est. **₹0.50–1.50/min**, opaque (prospeo.io 2026; edesy.in May 2026) | Knowlarity prepaid **₹0.40–0.60/min** after bundled mins (knowlarity.com/pricing/voice, Aug 2026); Ozonetel KooKoo **₹0.70/min + ₹500/mo** rental (prospeo.io 2026) | Benchmarks: **₹0.30–0.50 PSTN, ₹0.40–0.70 mobile termination**; high-volume direct-SIP contracts **₹0.60–1.20/min** (frejun.com Jul 2026 citing TRAI; caller.digital 23 Jun 2026) | Same as carrier SIP **+ your infra** — software layer free; aggregator margin removed |
| Platform/add-on fees | **Media Streams +$0.0044/min**, recording +$0.0025/min, AMD $0.0075/call (quiq.com Twilio breakdown, 2 Aug 2026) | Audio streaming & recording **free/included** (plivo.com/pricing, retrieved Aug 2026) | Bundled credits; dialer/SMS metered separately (cloudtalk.io, 2 Jul 2026) | Plan bundles; toll-free inbound ₹1.05/min extra | Channel rental + DID only | DevOps time; infra ₹10–50k/mo at scale |
| DID rental | ~$2.00/mo ≈ ₹200 (twilio.com voice pricing IN, May 2026) | **₹200/mo** (plivo.com) | Bundled/via sales | ₹250–1,500/mo typical (caller.digital, 10 Jul 2026) | ₹250–1,500/mo per DID | As carrier SIP |
| Setup effort | Hours, self-serve | **Days**: business KYC mandatory; DIDs 24–48 h (support.plivo.com Nov 2024; caller.digital Jun 2026) | Days–weeks; UL-VNO licensee, DLT hand-holding (frejun.com May 2026) | Weeks, sales-led; implementation often ₹25k–₹5L (prospeo.io 2026) | **Weeks–months**: enterprise KYC, link commissioning, static-IP/SBC work | Weeks–months on top of carrier SIP; "you become your own CPaaS" (caller.digital, Jun 2026) |
| Concurrency ceiling | 1 CPS free → up to 30 CPS provisioned; elastic concurrency (quiq.com Aug 2026) | PAYG hard-capped **2 RPS / 50 concurrent**; Enterprise from **$1,000/mo** (plivo.com/pricing; costbench.com 20 Jul 2026) | Sales-defined; thousands possible on contract | Prepaid channels 10–40; bespoke above | Jio: **10–5,000 channels/link**, pay for active channels (jio.com/business SIP Trunk, retrieved Aug 2026); TTBS **20–1,500 simultaneous** (tatatelebusiness.com); Airtel 30/number standard, more by quote | Hardware-bound: FreeSWITCH "thousands/node" (hirevoipdeveloper.com 7 Jul 2026); Asterisk tested **4,542 concurrent on 48 cores** (vitalpbx.com Oct 2023); rtpengine kernel module **10k+/instance** (17 Jul 2026) |
| Compliance burden (DLT/TRAI) | Self-managed; thinnest India tooling (frejun.com May 2026) | Native DLT workflow; enforces **KYC + India media anchoring** (support.plivo.com Nov 2024) | Strongest built-in DLT header/template/consent flows (frejun.com May 2026) | Mature posture; slower product velocity post-Gupshup acquisition (caller.digital Jun 2026) | Carrier runs scrubbing; you still register as PE/TM yourself | You own all of it: scrubbing, chain binding, traceability logs |
| KYC | Account + India docs for IN numbers | Business KYC before renting IN numbers (support.plivo.com Nov 2024) | Full business KYC | Full KYC + physical verification under 2025 rules | Heaviest: company docs, signatory verification; physical verification/biometrics now mandated (sigmachambers.in TCCCPR analysis 2025) | As whichever carrier you ride |
| Failure modes | Price shock at scale; **Media Streams has no India region** (US1 default, IE1/AU1 optional) → cross-border media hop = latency + DPDP optics (twilio.com/docs, 19 Aug 2026); vendor outage | Silent concurrency cliff at 50 calls; media-anchoring hangups if a leg leaves India ("Violates Media Anchoring", docs.plivo.com) | Credit exhaustion halts all calls instantly; opaque rates | Call-drop complaints at scale (61 G2 mentions, prospeo.io 2026); slow AI-media-streaming API evolution (caller.digital Jun 2026) | You own failover — one carrier outage = full stop until second trunk; long procurement; channel minimums waste money at low volume | Every CPaaS feature becomes your bug: retries, AMD, DTMF, status webhooks, NAT/SBC hardening, toll fraud |

### 1.2 Analysis at our volumes

**1k–10k calls/month (3k–30k min): managed CPaaS wins outright.** Carrier SIP economics invert at low volume: channel rentals (~₹350–700/channel/mo market norm, callin.io Mar 2025) plus minimums exceed what these minutes should ever cost. Plivo's flat ₹0.38/min with zero platform fee is the floor. Exotel/Knowlarity beat Plivo only if we need their DLT hand-holding or CCaaS features — we don't; LiveKit Agents *is* our contact center.

**100k calls/month (300k min): aggregator margin starts to hurt.** Aggregators charge ₹0.80–1.80/min retail on outbound mobile vs ₹0.60–1.20 on direct SIP contracts; enterprises cut direct deals around **20 lakh+ min/month** (caller.digital, 23 Jun 2026). Our crossover sits between ~100k–200k calls/mo — not before. Plivo's PAYG concurrency cap also bites near this tier (§4 math).

**Concurrency reality check (Erlang, not marketing):**
- 10k calls/mo ≈ 333 calls/day inside a ~6-hour calling window ≈ 56/hr ≈ **~3 concurrent** average. Trivial everywhere.
- 100k calls/mo ≈ 556/hr ≈ 9 CPS avg ≈ **~28 concurrent** (3-min holding time), peak ~45–60. Exactly where Plivo PAYG (50) and Knowlarity prepaid (10–40 ch) hit ceilings — and where a 60-channel carrier trunk becomes rational.

**Why not Twilio at any volume:** 2–3× India-rooted pricing, thinnest India compliance tooling, no India region for Media Streams (cross-border audio hop contradicts our localization stance), and per-feature surcharges stack invisibly (quiq.com, 2 Aug 2026). It survives only as a multi-country escape hatch — not our Phase-1 market.

---

## 2. The eSIM / SIM-bank grey-route question — documented so we never touch it

Grey routing = terminating calls through consumer SIMs held in SIM boxes/banks (or scaled consumer eSIM profiles) instead of licensed interconnect, dodging termination fees. Offers appear at ₹0.05–0.10/min. Verdict: **criminal, unreliable, banned for this project.**

**Illegal, with active enforcement:**
- Delhi Police IFSO busted an interstate SIM-box racket, seizing **thousands of illegally obtained SIMs** (ETTelecom/ANI, 10 Jan 2026); AP CID + DoT arrested **14 members** of an international SIM-box network, ~₹20 crore fraud (Communication Today, 27 Dec 2025); Chennai police seized **14 high-capacity Quectel SIM boxes** (Sep 2025, undercoverist.org); DoT dismantled **44 illegal telecom centres** nationwide per MHA's report to the Supreme Court (the420.in, 29 Apr 2026).
- Bulk SIM acquisition breaches DoT KYC/subscriber norms; **~4 million SIMs blacklisted via AI detection** (the420.in, 6 Aug 2025).
- **TCCCPR Second Amendment Regulations (12 Feb 2025)** obliges every access provider to deploy methods detecting "SIM Farm/SIM box type usage" and AI/ML-based proactive UCC monitoring, plus evidence-gathering honeypots (≥10 per service area) (trai.gov.in regulation PDF, Feb 2025). Carriers are mandated to hunt exactly this traffic.

**Unreliable even before getting caught:** carrier anti-spam firewalls **silently drop** grey/unregistered traffic — dead-ring calls, collapsing answer rates mid-campaign, unstable CLI, zero SLA recourse (grey routes ≈23% of A2P traffic and the top blocked-delivery source; voxsolutions.co CFO guide, 17 Jun 2026).

**Project policy:** grey routes are prohibited in code, vendors, and vendor conversations. Legal substitutes: DLT registration + designated-series numbers; volume negotiation (§4); shorter conversations via domain-config tuning.

**Compliance floors on the LEGAL path (Feb 2025 amendment; sigmachambers.in 2025):**
- Commercial calls may not originate on ordinary 10-digit numbers. Designated series: **140** promotional, **160 transactional/service — 160-series is not DND-scrubbed**, fitting our absent-student notification use case.
- Robocall/auto-dialer use must be **pre-declared** to the originating access provider.
- Penalties: **first UCC violation → ALL telecom resources (SIP trunks AND SIMs) barred 15 days; second → disconnection across all access providers** (Regulation 25 as amended, trai.gov.in, 12 Feb 2025). One sloppy campaign freezes our whole dialer for half a month — compliance is a cost line.
- Watch-item: *IndiaMART v. TRAI* (Delhi HC, listed Mar 2026; barandbench.com 9 Mar 2026) challenges complaint-driven barring for B2B callers; plan as if the rule stands.

---

## 3. Open-source stacks that pair with carrier SIP (replacing the Twilio Media Streams bridge)

Today: a CPaaS places the call and **Media Streams** pushes 8 kHz mulaw audio over WebSocket to our bridge, which relays to Deepgram → LLM → Cartesia. Three open-source paths replicate this on infrastructure we control:

### Path A — LiveKit SIP server (recommended; matches our locked LiveKit decision)

The open-source **`livekit/sip`** service is a SIP↔WebRTC bridge: define an outbound trunk pointing at any standard SIP provider (`<trunk-id>.zt.plivo.com`, `sip.telnyx.com`, …) plus inbound trunks + dispatch rules (docs.livekit.io/telephony outbound-trunk & sip-trunk-setup guides, rendered Aug 2026; github.com/livekit/sip). Self-hosted LiveKit carries "full support" for SIP/telephony — SIP runs as a separate service next to our existing LiveKit server (docs.livekit.io/intro/cloud comparison, 8 Aug 2026). Plivo publishes a first-party LiveKit guide and states its trunks "speak standard SIP… whether you self-host LiveKit or run it on LiveKit Cloud," with India media anchoring satisfied by running LiveKit in the India region (plivo.com/livekit, retrieved Aug 2026).

- **What replaces Media Streams:** nothing — the callee joins the LiveKit room as a participant; agents subscribe directly. The WebSocket relay layer disappears (fewer hops, lower latency, no per-stream fee).
- **What breaks / must be rebuilt:** call-status events → LiveKit webhooks; answering-machine detection → native AMD in LiveKit Agents (docs.livekit.io/telephony/features/answering-machine-detection, Jun 2026); DTMF → handled by livekit/sip (RFC2833/INFO); retry/redial logic stays in our backend dialer worker untouched.
- **What it saves:** the entire media-streaming surcharge category ($0.0044/min on Twilio; free on Plivo and free-once-self-hosted), plus CPaaS call-control margin when later paired with a raw carrier trunk.
- **Effort:** days–weeks: static egress IP or IP-ACL trunk auth, TLS/SRTP, one new service in docker-compose.

### Path B — FreeSWITCH + mod_audio_fork / mod_audio_stream

FreeSWITCH attaches a channel media bug and streams **bidirectional L16 PCM over WebSocket** (`uuid_audio_fork <uuid> start <wss-url> mono 16k`), accepting returned audio plus JSON control messages for barge-in/interruption (github.com/mdslaney/drachtio-freeswitch-modules README; callsphere.ai production walkthrough, 7 Apr 2026). That source calls it "structurally identical to the Twilio Media Streams bridge… but on infrastructure you control" — our FastAPI WSS bridge survives nearly intact; only framing changes (PCM vs base64 mulaw).

- **What breaks:** TwiML call control, mark/clear buffer semantics, Twilio-side AMD/recording — rebuilt as ESL logic or dropped. Tuned FreeSWITCH sustains "thousands" of concurrent calls/node (hirevoipdeveloper.com scaling guide, 7 Jul 2026).
- **Pick over A only if** we need deep dialplan control (predictive pacing, per-leg recording) livekit/sip doesn't expose.

### Path C — Kamailio + rtpengine (carrier-grade core for direct SIP)

Kamailio = signaling proxy; rtpengine = media proxy whose kernel module forwards RTP in-kernel — **10,000+ concurrent calls per instance** at modest CPU (hirevoipdeveloper.com rtpengine explainer, 17 Jul 2026); this pair is what tier-1 carriers run. Topology: carrier trunk → Kamailio (auth, topology hiding, fraud filtering) → rtpengine (RTP anchored in Mumbai) → agent stack via A/B behind it.

- **Use when:** direct carrier SIP at ~1M+ min/mo, multi-carrier failover, SBC duties. Overkill below that.
- **Gotchas:** rtpengine ng-control protocol on a private VLAN; strict-source learning on; `max-sessions` sized by load tests, not spec sheets (same source). Home-grown SBC scripts are easy to get wrong (irontec/itsbc README).

### What open source actually saves

**Platform fees, not physics** — the carrier still bills per-minute termination regardless of who bridges audio. Versus Twilio we delete: voice-rate premium (~₹0.8–1.1/min), Media Streams $0.0044/min, recording $0.0025/min, AMD $0.0075/call (quiq.com, 2 Aug 2026). Versus Plivo we delete only future Enterprise-tier/concurrency premiums. Hence the staged plan: **Path A on Plivo now; Paths A/C on carrier SIP when volume justifies** — not a big-bang PBX build.

Asterisk footnote: viable (4,542 concurrent tested on 48 cores, vitalpbx.com Oct 2023; community benchmarks ≈50 calls/core without transcoding, ~20 with), but weakest fit: its strengths are desk-phone PBX features we don't need; G.729 transcoding is CPU-hungry and licensed ($8/channel, asterisk.org, Jan 2025). Carriers give us G.711 end-to-end, so this rarely matters.

---

## 4. True cost model — 1k / 10k / 100k calls per month

**Assumptions:** 3.0 min avg connected call; we pay connected minutes only; FX ≈ ₹87/USD (Aug 2026); GST +18% excluded; DLT telemarketer/entity registration **₹5,900 one-time** (₹5,000+GST at Airtel/Jio/Vi DLT portals; BSNL ₹3,330; headers/templates ~free; 3–7 working days — smsgatewayhub.com & 2factor.in DLT guides, 2025–26).

Monthly telephony-only cost (platform fee + per-minute + DID/channel rentals):

| Option (rate basis) | 1k calls (3k min) | 10k calls (30k min) | 100k calls (300k min) |
|---|---|---|---|
| **Twilio** (₹1.20/min avg mobile + Media Streams ₹0.37/min + ₹200 DID) | **~₹4,900** | **~₹47,000** | **~₹471,000** |
| **Plivo PAYG** (₹0.38/min + ₹200 DID) | **~₹1,340** ✅ best | **~₹11,600** ✅ best | ~₹114,200* ⚠️ 50-concurrent cap borderline → Enterprise +$1,000/mo ⇒ ~₹201,000 |
| **Exotel** (est. ₹0.60–1.00/min blended + bundle) | ~₹2,600–3,800 | ~₹19,000–31,000 | ~₹185,000–305,000 (negotiable) |
| **Knowlarity prepaid** (Advance ₹16,800/yr ⇒ ₹1,400/mo incl 1,200 min, then ₹0.60/min, 10 ch) | ~₹2,600 | ~₹18,700 | Premium Plus (₹60k/yr, 40 ch, 10k free min, ₹0.40/min): ~₹126,000 |
| **Ozonetel KooKoo** (₹500 rental + ₹0.70/min out, +₹0.50/min port on entry plan) | ~₹3,200 | ~₹21,700 | ~₹210,700+ before sales discounts |
| **Carrier SIP direct** (₹0.35/min usage + channels @ ~₹400/ch/mo + ₹500 DID; install amortized) | ~₹5,300 ❌ minimums dominate | ~₹14,500 | ~₹130,500 (60 ch) → **~₹115,000** negotiated at scale ✅ best-at-scale |
| **Self-hosted (A/B/C) + carrier SIP** | carrier row + ₹8–15k infra (overkill) | carrier row + ₹10–20k infra | carrier row + ₹15–40k infra (media nodes + Kamailio/rtpengine) — buys independence, not cheaper minutes |
| **One-time, any legal path** | DLT **₹5,900** + KYC + (carrier-only) SIP install ₹5k–15k | — | — |

\* Peak Erlang at 100k calls/mo (~45–60 concurrent) straddles Plivo's PAYG cap; crossing it flips economics toward Enterprise tier or carrier SIP.

**Read-outs**
1. Per-connected-call cost drops **~₹4.90 → ~₹1.15** by moving Twilio→Plivo — a ~76% cut via a config-level trunk swap, zero agent-code change ("a configuration change, not a rewrite," plivo.com/livekit, Aug 2026).
2. Carrier-SIP crossover vs best CPaaS sits between ~100k–200k calls/mo (~300k–600k min), consistent with caller.digital's "direct SIP at 20 lakh+ minutes" guidance (23 Jun 2026). Below crossover, channel minimums lose money.
3. Fixed-cost gravity: at 1k calls/mo rentals are >50% of bill — boring pay-as-you-go wins. At 100k, per-minute dominates — every paisa is negotiable.
4. Telephony ≠ total cost: India full-stack AI voice sells at ₹6–12/min (bolti.co.in, 26 Jun 2026); at Plivo rates telephony is ~25–35% of unit economics. Keep logging STT/LLM/TTS vs telephony cost splits per call (CLAUDE.md convention) so the next optimisation targets the right line.

---

## 5. Migration sketch: off Twilio, onto the locked Plivo-first path

CLAUDE.md already locks "Plivo first (Exotel fallback), not Twilio." This executes that; the cascaded LiveKit architecture is untouched.

**Phase 0 — Compliance & accounts (week 1, all parallel).**
File DLT entity/telemarketer registration on a Jio/Airtel portal (₹5,900, 3–7 working days); register header + consent/content templates for the absent-student flow. Open Plivo account + business KYC (mandatory before IN numbers — support.plivo.com, Nov 2024). Buy 1–2 **160-series** service numbers; pre-declare auto-dialer use to the access provider (§2).
*Risks:* template rejections burn days — submit day one; KYC back-and-forth — keep incorporation/GST/signatory docs ready.

**Phase 1 — Parallel-run voice path (weeks 2–4).**
Deploy `livekit/sip`; create outbound trunk to Plivo (`<trunk-id>.zt.plivo.com`) and inbound trunk + dispatch rule (docs.livekit.io/telephony, Aug 2026). Pin LiveKit + Plivo media to India region for anchoring. Keep Twilio trunks configured as instant fallback. Test: answer rate, ASR accuracy on telephony audio, barge-in latency, AMD hit rate, DTMF, call-status webhooks.
*Exit criterion:* 2 weeks of parallel traffic with ≥ parity on connect rate + extraction accuracy.

**Phase 2 — Dialer cutover (month 2).**
Point the campaign worker at Plivo-originated calls; Twilio stays warm (disabled by default). Add Exotel as second provider behind a provider-abstraction interface (already our stated fallback) so no single vendor can halt campaigns. Verify in-India media anchoring on every call leg (hangup-cause monitoring for "Violates Media Anchoring").

**Phase 3 — Scale renegotiation (month 3+, trigger: >300k min/mo sustained or concurrency cap hits).**
Either Plivo Enterprise tier (custom concurrency, volume rates from $1k/mo commitment — plivo.com/pricing) **or** begin direct Jio/Tata SIP evaluation with Path C (Kamailio+rtpengine) fronting it. Keep CPaaS as failover trunk permanently.

**What stays throughout:** domain-config runtime (`/domain-configs`), agent pipeline (Deepgram/Groq/Cartesia), FastAPI backend, React frontend, consent/retention jobs. Only the telephony edge changes — which is exactly why the swap is cheap.

**Top migration risks:** DLT delay (mitigate: Phase 0 starts immediately); number porting lead times if we port the prototype number (ports take 2–4 weeks at some vendors vs 24–48 h for new DIDs — caller.digital, Jun 2026; prefer new 160-series numbers); anchoring misconfig silently failing calls (monitor hangup causes); concurrency cap surprises during a campaign burst (load-test at 1.5× planned CPS).

---

## 6. Honest bottom line

**Cheapest legal achievable telephony-only ₹/min:**
- **Now → 100k calls/mo: ~₹0.38/min** (Plivo domestic, streaming free) ≈ **₹1.15/call** at 3 min.
- **At scale (~20 lakh+ min/mo): ~₹0.30–0.45/min all-in** via negotiated carrier SIP (usage + channel rentals + DID blended), per TRAI-anchored market benchmarks (frejun.com Jul 2026; caller.digital Jun 2026). Self-hosting the bridge layer removes platform fees but cannot go below carrier termination — physics of the PSTN.

**Where ₹0 is impossible — explicitly:**
1. **PSTN termination is metered by licensed access providers.** Any legal call to an Indian mobile pays carriage; no software choice changes that. Only app-to-app WebRTC (both parties in our app) approaches ₹0 — useless for calling absent students' phones.
2. **Regulatory floor:** DLT registration ₹5,900 + KYC effort; designated-series number rentals; consent-management and traceability engineering mandated by TCCCPR (Feb 2025).
3. **Reliability floor:** SLA'd failover (second provider/trunk) costs money precisely because single-route grey-style "free" capacity gets silently blocked (§2).

**The one-sentence strategy:** cut ~75% today by replacing Twilio's India legs + Media Streams with Plivo + self-hosted LiveKit SIP (₹5,900 DLT once), stay pay-as-you-go until ~100k calls/mo, then trade aggregator margin for direct carrier SIP — and never, under any circumstances, let a ₹0.05/min SIM-bank offer through the door.

---

## Sources (accessed Aug 2026)

- Plivo India voice/SIP pricing ₹0.38/min, ₹200 DID, streaming included — plivo.com/voice/pricing/in & /sip-trunking/pricing/in
- Plivo PAYG caps (2 RPS / 50 concurrent), Enterprise $1k/mo — plivo.com/pricing; costbench.com (20 Jul 2026)
- Plivo India KYC + media anchoring rules — support.plivo.com "Domestic Calling in India" (18 Nov 2024)
- Twilio India outbound ₹0.65–1.50/min; DID $2/mo — twilio.com/voice/pricing/in (18 May 2026); edesy.in guides (Jan/May 2026); frejun.com Voice API guide (27 May 2026)
- Twilio surcharges (Media Streams $0.0044/min etc.), CPS limits, Media Streams regions — quiq.com Twilio pricing breakdown (2 Aug 2026); twilio.com/docs/voice/media-streams/websocket-messages (19 Aug 2026)
- Exotel credit model & plans — cloudtalk.io Exotel guide (2 Jul 2026); prospeo.io (2026)
- Knowlarity prepaid plans ₹16,800–60,000/yr, ₹0.20–0.30/30 s — knowlarity.com/pricing/voice (22 Aug 2026); Gupshup acquisition — gupshup.ai press releases (2022/2025)
- Ozonetel CloudAgent $25–55/agent/mo; KooKoo ₹500/mo + ₹0.70/min — prospeo.io Ozonetel/KooKoo analyses (2026); cloudtalk.io (28 Apr 2026)
- Carrier SIP benchmarks ₹0.30–0.70/min; channel rentals ₹350–700/mo; direct-SIP threshold 20 lakh+ min/mo — frejun.com SIP trunk guide (10 Jul 2026); caller.digital telephony-partner comparison (23 Jun 2026) & voice-AI cost breakdown (10 Jul 2026); callin.io (11 Mar 2025)
- Jio SIP Trunk 10–5,000 channels, unlimited-domestic rental plans, 140xx trunks — jio.com/business/services/voice-and-collaboration/sip-trunk (retrieved Aug 2026); indicative entry tariffs — call-soft.com (2026)
- Airtel SIP trunk 30 simultaneous/number — airtel.in/b2b/sip-trunk; TTBS 20–1,500 channels — tatatelebusiness.com; Smartflo ₹950–1,250/license/mo, OBD ₹0.48–0.60/min effective — tatatelebusiness.com/features/smartflo; infinian.net (19 Feb 2026)
- TCCCPR Second Amendment Regulations (12 Feb 2025): SIM-farm detection mandate, honeypots, 140/160 series, 10-digit ban, 15-day barring/disconnection penalties — trai.gov.in Regulation_12022025 PDF; sigmachambers.in analysis (2025); barandbench.com *IndiaMART v. TRAI* (9 Mar 2026); PIB releases (Mar–Jun 2025)
- DLT registration ₹5,900 (BSNL ₹3,330), process/timelines — smsgatewayhub.com/dlt-registration; 2factor.in (2025); digintra.com (2026)
- SIM-box enforcement: ETTelecom/ANI (10 Jan 2026); Communication Today/AP CID (27 Dec 2025); the420.in DoT-44-exchange report to SC (29 Apr 2026) & 4M-SIM blacklist (6 Aug 2025); undercoverist.org Chennai seizures (6 Oct 2025)
- Grey-route economics — voxsolutions.co CFO guide (17 Jun 2026); Subex bypass-fraud analysis (5 Jun 2026)
- LiveKit open-source SIP server, self-hosted support, trunk config, native AMD — github.com/livekit/sip; docs.livekit.io/telephony/* (rendered Jun–Aug 2026); docs.livekit.io/intro/cloud (8 Aug 2026); plivo.com/livekit integration (retrieved Aug 2026)
- FreeSWITCH mod_audio_fork bidirectional WebSocket PCM bridge — drachtio-freeswitch-modules README (github); callsphere.ai walkthrough (7 Apr 2026); arkade-ai/mod_audio_stream (2025–26)
- Capacity: FreeSWITCH thousands/node (hirevoipdeveloper.com, 7 Jul 2026); rtpengine kernel module 10k+ concurrent (17 Jul 2026); Asterisk 4,542 concurrent/48 cores (vitalpbx.com, 7 Oct 2023); Asterisk community benchmarks & G.729 license (asterisk.org, 18 Jan 2025)


