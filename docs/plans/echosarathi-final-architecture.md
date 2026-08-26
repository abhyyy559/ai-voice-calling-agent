# VocalIQ / EchoSarathi — Final Multilingual Voice-Agent Architecture

**CONFIDENTIAL — internal only.** §5 (closed-source stack + negotiated economics) is the actual moat and should never leave the team. §6 (open-source/BYOK edition) is the only part safe to make public.

**Date:** August 26, 2026
**Synthesized from:** `multilingual.md` (multilingual-researcher agent, Phase-2 report) and `telephony-alternatives.md` (telephony cost-optimization report), both dated Aug 26 2026. No new vendor claims are introduced here — this document combines, re-does the arithmetic across, and makes product decisions on top of those two reports. Where something is unresolved in the source material, it's carried forward as unresolved, not quietly settled.

---

## 1. Executive Summary

**Two-tier product strategy:**

| | Open-source / BYOK edition | Closed-source managed edition |
|---|---|---|
| Who runs the infra | Customer, on their own vendor accounts | You, on negotiated enterprise rates |
| Who pays STT/LLM/TTS/telephony vendors | Customer, directly | You (COGS target: **₹2–2.5/min**) |
| What you sell | The orchestration framework + domain-config tooling (subscription/license) | The full managed call, billed ~₹3–5/min per your existing pricing |
| What's public | Agent pipeline scaffolding, domain-config schema, provider-abstraction interface | Nothing — this is §5 |
| What's confidential | — | Negotiated rates, tuned guardrail thresholds, escalation logic, domain-configs, compliance playbook |

This isn't just a licensing gimmick — it's the reason the confidentiality requirement makes structural sense. The BYOK edition's value is the *engineering* (a working, tested, config-driven pipeline). The managed edition's value is the *economics and tuning* (which vendors, at what negotiated rate, with what thresholds) — and economics/tuning are exactly what's cheap for a competitor to copy if they can see it, and expensive for them to rediscover if they can't.

**Is ₹2–2.5/min achievable?** Yes, at *negotiated* rates — but not with margin to spare at *sticker* rates. Your own multilingual report's sensitivity analysis puts the stack at ≈₹1.1–2.0/min expected, ≈₹1.9–3.4/min worst-case-sticker. Full combined math with the (cheaper than assumed) telephony numbers from your telephony report is in §5.4 — short version: **on target at negotiated rates, over target if you pay every vendor's list price.** Treat ₹2.5/min as something you negotiate your way under, not something that falls out automatically.

**Languages:** Telugu, Hindi, English fluency + mid-call code-switching is achievable with the stack your own research already points to (Sarvam Saaras v3 STT + Sarvam-M/30B LLM + Bulbul v3 TTS) — but "the agent switches its own spoken language when the caller switches" is **application logic you still have to build**, not a feature any single vendor ships. Detail in §3.4 — this is the one place in your ask that's a real engineering task, not a vendor-selection task.

**Telephony:** literal zero-telephony-vendor isn't legally possible. What's actually rare and enterprise-grade is self-hosting the SIP/media bridge (`livekit/sip`) instead of renting a CPaaS's proprietary streaming layer — that's the "nobody else is doing this" version of your ask. Parallel calling is solved with a primary+overflow hybrid, not a single alternative provider. Detail in §4.

---

## 2. Language & Voice Architecture

### 2.1 Speech-to-Text

| Model | Telugu accuracy | Code-switching | Streaming | 8kHz telephony fit | Cost |
|---|---|---|---|---|---|
| **Sarvam Saaras v3** ✅ recommended | ~19.3% avg WER, code-mixed <12% [VENDOR] | **Native** — dedicated `codemix` output mode | <150ms first-token | Purpose-built for 8kHz telephony | ₹0.50/min (verify — pricing page shows ₹30/hr, marketing shows ₹1.5/min; **unresolved discrepancy, resolve before contract**) |
| Deepgram Nova-3 `te` (incumbent, A/B) | No public Telugu WER yet | Multilingual code-switch endpoint | <300ms | Telephony-grade heritage | ≈₹0.44/min |
| AI4Bharat IndicWhisper/Conformer (open) | 28.8% avg Telugu (worse) | Weak | No native streaming | Explicitly "future work" per AI4Bharat themselves | Free weights, GPU-hour only |

**Decision:** Saaras v3 primary, Nova-3 `te` as A/B (already wired). Open-weight options are not production-ready for telephony-domain Telugu today — don't let the open-source narrative pull you toward them prematurely; this is a case where the closed API genuinely earns its ₹0.50/min.

### 2.2 LLM

| Model | Telugu/Tenglish evidence | Notes |
|---|---|---|
| **Sarvam-M / Sarvam-30B (non-think)** ✅ recommended | Only model with published conversational Telugu/Tenglish evidence (Indic Vibe Check 8.12/9 vs Llama-4-Scout 7.58) [VENDOR — Sarvam's own eval, favorable-but-interested] | General reasoning is mediocre (#121/137 independent rank) — irrelevant for constrained call flows, would matter if you ever need open-ended reasoning |
| Groq GPT-OSS-120B (escalation tier) | No Telugu-specific benchmarks — evidence gap | Rule-based escalation for hard turns only; forced migration anyway since Llama-3.3-70B was deprecated Aug 16, 2026 |

**Unresolved and load-bearing:** Sarvam-M's function-calling/field-extraction accuracy has **no independent benchmark** — your own report flags this as the one claim to verify in your qa-eval harness before committing. Token cost either way is a rounding error (<₹0.05–0.30/min) — this is a quality decision, not a price one.

### 2.3 TTS + Voice Cloning

| Engine | Telugu naturalness | Cloning | Cost |
|---|---|---|---|
| **Sarvam Bulbul v3** ✅ recommended | Won a 20k+ vote blind study; docs admit per-language variance (rare vendor honesty, worth trusting) | Consent-based enterprise cloning only — **no self-serve cloning exists yet** | ₹1.05–1.80/min (v3) or ₹0.53–0.90/min if v2 pricing negotiated — **dominant cost line, negotiate here first** |
| Cartesia Sonic (latency fallback) | No independent Telugu MOS | Self-serve instant cloning | ~₹1.8–3.0/min |
| F5-TTS / XTTS-v2 (open) | N/A | Zero-shot | ❌ **Legally barred for commercial use, and neither speaks Telugu** — do not consider these regardless of cost |

**The honest gap:** there is no commercial-safe open-source Telugu voice cloner today. This is the single biggest strategic gap in the whole stack per your own research — don't plan around one appearing on your timeline.

### 2.4 Mid-Call Code-Switching — the part you have to build

This is the one place where "pick a vendor" doesn't finish the job. Saaras v3's `codemix` mode gives you an accurate transcript when a caller mixes Telugu and English in one utterance — but *deciding which language the agent should speak back in, turn by turn,* is orchestration logic on top of that, not a toggle any vendor exposes. The design:

1. **Per-turn language signal**: Saaras's codemix transcript already tags mixed spans; use the dominant language of the caller's last turn (not the whole call) as the switch trigger — a caller who drops into English for one sentence and back to Telugu shouldn't flip the agent's voice for the rest of the call.
2. **Response-language selection**: prompt Sarvam-M with the detected turn language and instruct it to respond in kind — it's trained on code-mixed and romanized forms, so this is within its documented capability, not a stretch.
3. **Voice routing**: maintain a **per-language voice mapping** in the agent/domain-config (your own research's UX section already recommends exactly this pattern for the admin dashboard) so the TTS call picks the right Bulbul voice for the response language automatically — never hardcode a voice ID.
4. **Fallback discipline**: keep the translation-in-the-middle cascade (STT→IndicTrans2→English LLM→IndicTrans2→TTS) *only* as an emergency path for a pure-Telugu turn if Sarvam-M fumbles — never the standing path. Your own latency budget math shows it barely fits even without code-switching overhead; treating it as primary would blow the ≤900ms turn target you're already thin on.

Net effect: code-switching is buildable on the stack you already have, on a 1–2 week timeline of orchestration work — not a new vendor search.

---

## 3. Telephony Architecture — Enterprise-Grade, Parallel-Capable

### 3.1 Correcting "no telephone clouds" — the physical constraint

Every legal call to an Indian mobile pays PSTN termination to a licensed access provider. No software choice removes that — your own telephony report is explicit that ₹0 telephony is impossible, and that the only sub-₹0.10/min offers on the market are illegal SIM-box/grey routes (documented arrests through 2026, carriers are mandated to actively hunt this traffic, first violation bars *all* your telecom resources for 15 days). This isn't a compliance nicety to route around — it's a hard floor.

**What's actually achievable, and what's genuinely rare:** most vendors in this space (and most competitors) run their agent pipeline through a CPaaS's proprietary media-streaming bridge (Twilio Media Streams, or equivalent), paying a per-stream surcharge on top of the per-minute rate. Self-hosting the bridge — `livekit/sip`, which matches your already-locked LiveKit decision — removes that middle layer entirely. The callee joins your LiveKit room directly; there's no separate streaming fee, fewer network hops, and you own the entire pipeline from carrier trunk to agent. **That's the enterprise-grade, not-personal-tier version of your ask** — a self-hosted, production SIP bridge is a fundamentally different posture than a personal Twilio account, even while the underlying carrier connection (Plivo, then eventually direct carrier SIP) is unavoidably still "a telephony vendor" in the strict sense.

### 3.2 Recommended path

| Stage | What | Concurrency ceiling | When |
|---|---|---|---|
| **Now** | `livekit/sip` self-hosted bridge → Plivo domestic trunk (₹0.38/min, streaming free) | 50 concurrent (PAYG cap) | Immediately — config-level trunk swap, no agent code changes |
| **Overflow / parallel burst** | Second provider (Exotel) behind the same provider-abstraction interface, absorbing calls once Plivo's ceiling is hit | Sales-defined, effectively higher | As soon as campaign concurrency approaches ~40-50 |
| **At scale (>100k calls/mo or >300k min/mo sustained)** | Direct carrier SIP (Jio/Tata/Airtel) fronted by Kamailio (signaling) + rtpengine (media, kernel-mode RTP forwarding) | **10,000+ concurrent per instance** — tier-1 carrier-grade | Trigger-based, not calendar-based |

This is the hybrid you described: the primary path (Plivo via self-hosted LiveKit SIP) carries baseline traffic; a second path absorbs parallel overflow; and the carrier-grade path (Path C) is the ceiling-breaker once volume justifies the operational overhead. None of this is "pick one alternative" — it's a provider-abstraction layer with a defined escalation order, which is also what makes a single vendor outage non-fatal to a campaign.

**Reality check on jumping straight to Path C:** your own cost model shows direct carrier SIP is *more* expensive than Plivo below ~100k–200k calls/month — channel rental minimums dominate at low volume. If current call volume is closer to college-pilot scale (thousands/month), starting there would work against your own cost-cutting goal, not for it. The self-hosted bridge (Path A) is what gets you the "enterprise, own-the-stack" posture *today* without paying the carrier-SIP premium before you've earned it.

### 3.3 Concurrency math at representative volumes (from your own report)

| Volume | Avg concurrent (3-min avg call) | Fits on |
|---|---|---|
| 10k calls/mo | ~3 concurrent | Trivially inside Plivo's 50-cap |
| 100k calls/mo | ~28 average, peak 45–60 | **Right at Plivo's ceiling** — this is where overflow provider #2 or Path C becomes necessary, not optional |

---

## 4. Combined Unit Economics (Closed-Source Managed Tier)

Recomputing your multilingual report's stack total with the more precise telephony figures from your telephony report (₹0.38/min Plivo PAYG rather than the ₹0.80 placeholder used in the multilingual doc's own table):

| Component | Choice | ₹/min | Confidence |
|---|---|---|---|
| Telephony | Plivo (self-hosted LiveKit bridge) | 0.38 | [INDEP, vendor pricing page] |
| STT | Saaras v3 | 0.50 | [VENDOR — pricing page vs marketing discrepancy unresolved] |
| LLM | Sarvam-M/30B + Groq escalation | 0.05–0.30 | Token cost, low risk |
| TTS | Bulbul v3 (v2 pricing if negotiated: 0.53–0.90) | 0.55–1.80 | Dominant cost line |
| Cloning | Sarvam enterprise (bundled) | ~0–0.30 | Enterprise-deal dependent |
| Orchestration | LiveKit Agents (self-hosted) | ~0 | Infra cost only |
| **Total** | | **≈1.48–3.28/min sticker → ≈0.98–1.88/min at negotiated TTS + expected LLM usage** | |

**Against your ₹2–2.5/min target:** comfortably inside it at negotiated rates; the sticker-price ceiling (~3.28) would miss it. **TTS is the lever** — it's the single largest and most negotiable line item. Priority order for protecting margin: (1) negotiate Bulbul v2 pricing, (2) tune domain-configs toward shorter agent phrasing to cut TTS chars/min, (3) revisit self-hosting Indic Parler-TTS only past >1M chars/month, where the amortized math starts to work (₹0.05–0.25/min self-hosted vs ₹0.55+ API).

**Margin against your stated ₹3–5/min customer price:** even at sticker-price worst case (₹3.28), you're inside a ₹3–5/min sell price, though thin at the ₹3 end. At negotiated rates you're looking at 40–65% gross margin on the managed tier — healthy, and worth protecting by locking TTS pricing before scaling volume.

---

## 5. Open-Source / BYOK Edition — What's Actually Public

To keep the confidentiality boundary real rather than nominal:

**Safe to open-source:**
- The provider-abstraction interface itself (the pattern, not your specific negotiated endpoints)
- Domain-config *schema* (the shape of a call flow), not your populated domain-configs (e.g., the absent-student flow's actual prompts/logic)
- The LiveKit SIP bridge integration pattern
- Generic guardrail *scaffolding* (the check types), not your tuned thresholds

**Never in the open edition:**
- Negotiated rate cards with any vendor
- Populated domain-configs for real customer flows
- Tuned guardrail floors/thresholds (these took real iteration to get right and are directly reusable by anyone who sees them)
- Compliance playbook specifics (DLT template wording, consent scripts)
- Any qa-eval harness results that reveal which vendor combination actually performs best in production

The BYOK customer gets a working, honest framework and pays retail vendor prices for the privilege of running it themselves — which is a legitimate product on its own, and structurally can't undercut your managed tier's margin since they're paying full freight to the vendors you've negotiated volume discounts with.

---

## 6. Open Risks — Carried Forward, Not Resolved Here

These are unresolved in your source research and should block signing anything, not just architecture planning:

1. **Sarvam STT pricing discrepancy** (₹30/hr vs ₹1.5/min marketing) — get this in writing before contracting.
2. **Sarvam-M function-calling/extraction accuracy** — no independent benchmark exists; run your domain-config harness against it before committing the LLM tier.
3. **Bulbul v3 Telugu MOS on your actual scripts** — blind-test candidate voices with real users; Sarvam's own docs admit per-language variance.
4. **No commercial-safe open Telugu voice cloner exists** — don't plan a self-host cloning fallback around one appearing.
5. **Concurrency ceiling proximity** — 100k calls/month sits right at Plivo's 50-concurrent cap; load-test at 1.5× planned peak CPS before a campaign, not during one.

---

## 7. Immediate Next Actions

1. Get Sarvam's STT pricing discrepancy resolved in writing — it's a 3x swing (₹0.50 vs ₹1.5/min) that changes the whole economics table.
2. Stand up the qa-eval harness for Sarvam-M function-calling before any commitment — this is the one unverified claim the whole LLM tier depends on.
3. Deploy `livekit/sip` against Plivo now (Phase 0/1 from your telephony report) — this is the fastest concrete step toward the "own the bridge" architecture and doesn't wait on any of the above.
4. Design the per-language voice-mapping schema in the domain-config format now, even before code-switching logic is built — it's needed either way and unblocks the TTS voice-gallery UX work in parallel.
5. Negotiate Bulbul v2 pricing before scaling call volume — this is your single biggest lever on hitting ₹2–2.5/min with margin to spare.
