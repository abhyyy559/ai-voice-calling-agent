# AI Voice Calling Agent — Independent Technical & Commercial Research (India, Aug 2026)

**How to read this:** Given the size of this brief, I'm not tagging every sentence. Instead: figures with a `(Source: ..., 2026)` note are things I found in current, dated sources — treat vendor blog numbers as *provider claims* unless I say "independent benchmark." Anything under a **"My take"** or **"Recommendation"** heading is my own inference/judgment, not a cited fact. I've flagged the places where I think your brief is making an assumption worth challenging.

---

## 0. TL;DR — the four places I'd push back on the brief

1. **Don't evaluate SIM/eSIM at all.** It's not a real option for this use case — no programmability, no legal outbound-calling compliance path, no concurrency, no audio streaming. The real decision is *which cloud telephony/CPaaS provider*, not telephony architecture type.
2. **"Best latency" and "best voice quality" are not settled by picking one vendor.** The entire market has converged on a *cascaded* pipeline (STT → LLM → TTS) as the production default, specifically *because* your core requirement — structured data extraction ("why were you absent," "when will you return") — needs reliable tool-calling and auditable text at every stage. Speech-to-speech models (OpenAI Realtime, Gemini Live) are lower-latency in theory but worse at exactly the thing your admin-use-case needs most. This is the single biggest architectural decision in your brief, and I'd resolve it in the opposite direction of where "most natural conversation" intuition points.
3. **Telugu is not a "harder version of English" — it's a different vendor stack.** None of the providers that are strong in English (Deepgram, Cartesia, ElevenLabs, AssemblyAI) have credible production Telugu. The market has a genuine India-first specialist (Sarvam AI) that is *purpose-built* for this, including Telugu-English code-switching. Plan for a stack swap, not a stack extension, in Phase 2.
4. **Cost math: "AI is cheaper than a human caller" is not obviously true in India at your scale.** In the US, human agents cost $35–50k/year, making AI's ~$0.05–0.25/min trivially cheaper. In India, a telecaller costs roughly ₹15,000–25,000/month and handles ~2,500–3,500 calls/month at ~3 min average — that's roughly ₹2–3.5/min *fully loaded*, which is in the same range as, or cheaper than, a well-run AI stack at low volume once you include Indian STT/TTS/LLM/telephony costs. AI's actual advantage for your use case is concurrency, 24/7 availability, consistency of data capture, and not needing to staff a calling team every semester — not raw per-minute cost. Sell it internally on that basis, not on "cheaper than a human."

---

## 1. Telephony: the real decision is which CPaaS provider, not what "kind" of number

### Why SIM/eSIM is off the table
A physical/eSIM-based approach (a phone connected to a modem/GSM gateway) has no API-level call control, no reliable concurrency beyond the number of physical SIMs you buy, no programmatic WebSocket/RTP audio access for STT/TTS integration, and critically, **no path to DLT compliance** — Indian carriers treat bulk automated calling from a personal-SIM-style number as spam and will silently block or throttle it (Source: multiple TRAI-compliance guides, 2026). This isn't a trade-off to weigh against cloud telephony; it simply doesn't do the job.

### The real shortlist for India

| Provider | India fit | Outbound rate (typical) | Number rental | Streaming for voice AI | DLT handling | Notes |
|---|---|---|---|---|---|---|
| **Exotel** | India/APAC-native, UL-VNO licensed telecom operator | ~₹0.80–1.00/min (Source: Exotel migration guide, 2026) | Varies by plan | AgentStream — bidirectional WebSocket, 16-bit 8kHz PCM, <20–50ms media latency (provider claim) | Strongest — handles DLT/DND as part of the platform (Source: caller.digital, 2026) | Best "compliance handled for you" option; ~10–25% pricier than Plivo per-minute (Source: caller.digital, 2026) |
| **Plivo** | Global CPaaS with strong India presence | Local outbound ~₹0.60/min (Source: awaaz.ai, 2026) | ~₹250/month (Source: awaaz.ai, 2026) | Native SIP trunking + audio streaming; explicitly integrates with LiveKit and Pipecat (Source: Plivo pricing page, 2026) | Competent, self-managed DLT registration | Best "developer-first, cheapest to prototype on" option; 24–48hr Indian DID provisioning (Source: caller.digital, 2026) |
| **Ozonetel** | India CCaaS + telephony | Unlimited-minute agent pricing on some plans (unusual model) | — | Yes | Strong | Leans more contact-center-suite than raw API; good if you eventually want agent-desktop/CCaaS features |
| **Knowlarity (Vonage)** | India-native | — | — | Yes | Strong | Similar profile to Exotel |
| **Twilio** | Global, weakest India economics | ~₹1.20–1.50/min outbound, ~₹0.50–0.80 inbound (Source: Exotel migration guide citing Twilio's own India pricing, 2026) | — | Best-in-class docs, `<Stream>` verb, ConversationRelay | DLT is **self-managed with no platform tooling** (Source: frejun.com, 2026) | 50–100% more expensive than India-native providers for India-domestic calls; best documentation ecosystem but that's not worth the premium here |
| **Bolna (open-source India-focused agent framework)** | India-specific, ships **Sarvam + Twilio-India defaults out of the box** (Source: thinnest.ai framework comparison, 2026) | Depends on underlying telephony chosen | — | Built for exactly this stack | Handled at the framework level | Worth evaluating directly — it's the framework in this landscape closest to "built for an India + regional-language voice agent," see §12 |

**Reality check on the pricing figures above:** these numbers come from vendor blogs and comparison sites, not directly from a live quote. Treat them as *directionally correct, not contractual* — get an itemized INR quote from 2–3 providers before committing, since several sources explicitly warn that "quote only in USD" or vague per-minute figures are a red flag at contract stage (Source: frejun.com voice-api-india guide, 2026).

### KYC / DLT / regulatory requirements (this is not optional paperwork — see §10 for the full legal picture)
- Register as a **Principal Entity** on TRAI's DLT platform (PAN, GST, CIN, Aadhaar biometric auth required); one-time fee ~₹5,900 on the first TSP platform (Source: frejun.com TRAI guide, 2026).
- Choose the correct number series: **140-series** for promotional/marketing calls, **1600-series** (was 160) for BFSI/transactional service calls (Source: multiple TRAI-compliance guides, 2026). **Neither cleanly fits an educational-institution "why were you absent" call** — this is a genuine gray area (see §10). Get this classified correctly before your first campaign; carriers silently drop non-compliant calls rather than erroring (Source: autointerviewai.com, 2026).
- Registration typically takes 5–10 business days when documentation is correct, longer if resubmission is needed (Source: multiple sources, 2026).

### Recommendation
Prototype on **Plivo** (cheapest, cleanest API, works directly with LiveKit/Pipecat, fast DID provisioning) or **Exotel** if you'd rather have DLT/compliance handled for you at a ~15–25% cost premium. Do **not** start with Twilio for India-domestic calling — its India economics are worse on every axis and its DLT tooling is weaker, and its main advantage (documentation quality) matters less once you're using LiveKit/Pipecat docs instead of Twilio's. Register DLT in parallel with prototyping — it's the long pole, and calls will silently fail without it once you leave a sandbox/test-number phase.

---

## 2. Real-time voice architecture: the components, ranked by effect on perceived quality

A production voice agent is a pipeline, not a model:

**Telephony (PSTN/SIP) → Audio streaming (WebSocket/RTP) → VAD → STT (streaming) → Turn/endpoint detection → LLM (streaming, with tool calling) → TTS (streaming) → Audio playback**, wrapped in session/state management that tracks conversation history, call status, and structured data extraction per call.

Ranked by how much each one actually affects whether a caller thinks they're talking to a human (my inference, based on the aggregate of what the sourced benchmarks measure and emphasize):

1. **Turn detection / endpointing** — this is the component every serious 2026 source calls "the least understood and most important" (Source: autointerviewai.com, 2026). Get this wrong and nothing else matters: the agent either talks over people or leaves robotic dead air.
2. **TTS time-to-first-audio** — the single largest controllable contributor to perceived responsiveness (Source: codesota.com, burki.dev, 2026).
3. **STT streaming latency + accuracy on telephone-quality (8kHz, noisy) audio** — most STT benchmarks are run on clean audio; production phone audio is materially harder (Source: sarvam.ai, gladia.io, 2026).
4. **LLM time-to-first-token**, less so total generation time, since responses stream.
5. **Barge-in / interruption handling** — technically straightforward (stop TTS playback, flush buffer) but the *policy* around it (is this a real interruption or a backchannel "mhm"?) is where quality is actually won or lost.

**My take:** most teams over-invest in "which LLM" and under-invest in turn detection and TTS latency tuning. For your project, I'd budget engineering time in the opposite proportion to where the brief's question list implies effort — turn-taking tuning and TTS provider selection will move the needle on "feels human" far more than LLM choice will.

---

## 3. Latency: the pipeline and realistic targets

**Human conversational turn-taking gap averages ~200ms** (Source: reactify-solutions.com citing production 2026 figures). No cascaded system fully matches this yet, but the target for "doesn't feel robotic" is generally cited as **under ~800ms** end-of-caller-speech to start-of-agent-speech, with a hard ceiling around 900ms–1.2s before callers perceive it as "the AI is thinking" (Source: retellai.com, autointerviewai.com, 2026).

Realistic 2026 component budget for a well-tuned cascaded pipeline (my synthesis of the sourced benchmarks in §5–§7, not a single vendor's number):

| Stage | Typical range (2026, tuned) |
|---|---|
| VAD / end-of-turn detection | ~200–300ms (Silero VAD baseline; semantic/prosody turn detectors add ~20ms but cut false-cutoffs) (Source: reactify-solutions.com, livekit docs, 2026) |
| STT first-partial / streaming | 100–300ms (Deepgram Nova-3/Flux, AssemblyAI Universal-Streaming) (Source: assemblyai.com, futureagi.com, 2026) |
| LLM time-to-first-token | 200–300ms on a fast small model via Groq; 300–600ms+ on a standard hosted frontier model (Source: neuraplus-ai, reactify-solutions.com, 2026) |
| TTS time-to-first-audio | 40–90ms (Cartesia Sonic) to 75–300ms (ElevenLabs, depending on model tier) (Source: multiple TTS comparisons, 2026) |
| Network/orchestration overhead | 50–200ms depending on region pinning (Source: reactify-solutions.com, 2026) |
| **Realistic end-to-end (tuned, cascaded)** | **~600–900ms median**, matching what Retell/Vapi/LiveKit teams report in independent 2026 tests (Source: techsy.io head-to-head test, tested.media, 2026) |

**My take:** don't chase sub-500ms as a Phase-1 target — even the best-funded commercial platforms (Retell, Vapi) sit at 500–900ms median in independent testing, with P95 regularly exceeding 1.5s under load (Source: techsy.io, 2026). A more useful Phase-1 goal is "consistent 700–900ms with no P95 tail above ~1.5s," because *consistency* matters more to perceived quality than best-case latency (Source: retellai.com, 2026).

---

## 4. Interruption & turn-taking

The 2026 production pattern has three layers, and this is worth building deliberately rather than treating as a VAD afterthought:

1. **VAD (Voice Activity Detection)** — continuous per-frame confidence that incoming audio contains a voice. Silero VAD is the open-source default used across LiveKit, Pipecat, and most managed platforms.
2. **Endpointing** — deciding *when* the user's turn has actually ended. Pure silence-threshold endpointing (typically 700–1000ms of silence) is the baseline but can't distinguish a genuine pause from someone still thinking mid-sentence (Source: autointerviewai.com, 2026).
3. **Semantic/prosody turn detection** — the 2026 upgrade path: models that read pitch drop, rising intonation, and semantic completeness of the partial transcript to distinguish "done talking" from "thinking pause" from "backchannel" (uh-huh/mhm). LiveKit's Turn Detector v1 reports a **9.9% false-cutoff rate at a 300ms latency budget** in their own testing (Source: livekit/autointerviewai.com, 2026) — an independently-reproducible number worth validating on your own audio before trusting it wholesale. Deepgram's **Flux** model folds end-of-turn detection directly into the STT model, claiming under 300ms median with no external VAD needed (Source: coval.ai, 2026 — vendor claim).

For interruption handling specifically: when the caller speaks while the agent is talking, the system needs to distinguish a genuine interruption ("actually, wait—") from background noise or a backchannel, then immediately stop TTS playback and discard unplayed audio if it's genuine. This is largely a solved engineering pattern in LiveKit Agents and Pipecat (both ship "adaptive interruption handling" and "false interruption" guards out of the box per their docs) — I would not try to build this from scratch.

**My take:** For your college-absence use case specifically, students will frequently pause mid-explanation ("I was... um... I had a family thing"). A silence-only endpointer will cut them off. Budget explicit tuning time for endpointing thresholds against real Indian-English and Telugu speech patterns — this is exactly the kind of thing that reads fine in a demo and breaks on real calls.

---

## 5. Voice quality (TTS) — don't assume open-source is cheaper or better

| Provider | Time-to-first-audio | Strength | Weakness | Telugu? |
|---|---|---|---|---|
| **Cartesia Sonic** | ~40–90ms (Source: multiple 2026 comparisons) | Latency leader; State Space Model architecture, not transformer-based | Voice character/emotional range slightly behind ElevenLabs; latency *spread* is wider than ElevenLabs (Source: forasoft.com, 2026) | No |
| **ElevenLabs (Flash v2.5 / Turbo)** | ~75–300ms depending on model tier | Best voice realism/emotional expressiveness, cloning, broadest language count (32+) | Slower than Cartesia on the fast path; the highest-quality models (Multilingual v2) are 500–800ms — too slow for real-time turns | Limited — general multilingual, not Telugu-specialist |
| **Deepgram Aura-2** | ~90ms tuned | Bundled into Deepgram's Voice Agent API (single WebSocket for STT+LLM+TTS) | Newer, less proven on voice character | No |
| **Sarvam Bulbul V3** | Sub-250ms first-byte via WebSocket (provider claim, sarvam.ai 2026) | **Purpose-built for Telugu and 10 other Indian languages** — vowel harmony, Tenglish code-switching, Indian name/number pronunciation, top-ranked in a Josh Talks blind study of 20k+ votes (provider-cited study) | Not competitive for pure-English use vs. Cartesia/ElevenLabs | **Yes — this is the answer to your Telugu TTS question** |

**My take on "open-source vs. paid":** the brief specifically asks not to assume open-source is automatically cheaper/better, and the evidence supports that skepticism — self-hosted open-weight TTS (e.g., Kokoro) is genuinely cheaper at very high volume but requires you to own GPU infrastructure, and for a project whose *entire differentiator is voice quality*, that's the wrong place to cut corners in Phase 1. Rent a top-tier API until conversation quality is proven, then reconsider self-hosting purely as a cost optimization once volume justifies it.

**Recommendation:** Cartesia Sonic for English (latency-critical outbound calls, where every hundred milliseconds compounds into "feels robotic"). Sarvam Bulbul V3 for Telugu — there isn't a credible alternative with comparable Telugu-specific tuning (code-switching, prosody, name pronunciation) among the global providers.

---

## 6. Speech recognition (STT) — telephone audio is the hard case, and vendor benchmarks mostly don't test it

Independent 2026 benchmarking (Hamming.ai, 4M+ production calls) found **AssemblyAI's Universal-3 Pro Streaming faster *and* more accurate than Deepgram Nova-3** on real production call audio — 307ms P50 latency / 8.14% WER vs. Deepgram's 516ms / 9.87% (Source: assemblyai.com citing Hamming.ai, 2026 — note this is AssemblyAI's own blog citing a third-party benchmark, so treat the framing with mild skepticism even though the underlying benchmark is independent). Deepgram's counter is **Flux**, a model purpose-built for voice agents that folds end-of-turn detection into the STT step itself and posts the lowest end-of-speech latency as of mid-2026 (Source: coval.ai, futureagi.com, 2026).

Word error rate has genuinely plateaued among the top players on *clean* audio — Deepgram Nova-3, AssemblyAI Universal-3 Pro, OpenAI gpt-4o-transcribe, ElevenLabs Scribe v2, and Microsoft's MAI-Transcribe-1 all sit within 1–2 percentage points of each other on standard benchmarks (Source: coval.ai, 2026). **The real competitive surface has moved to streaming latency, end-of-turn detection, and multilingual/code-switching depth** — which is exactly where the India/Telugu question becomes decisive.

For Telugu (and Indian accents generally), **Sarvam's Saaras v3** is the standout: trained on 1M+ hours of real Indian audio specifically (not adapted from an English-first model), explicitly built for 8kHz noisy telephony audio rather than clean studio recordings, with native code-mixing/diarization support and <150ms time-to-first-token (provider claim, sarvam.ai 2026). **Gnani.ai** is the enterprise alternative — 14M+ hours of Indian telephony training data, #1 on 8 of 9 Indian languages on the "Kathbath Noisy" benchmark (provider claim), but it's an enterprise-only, custom-pricing platform rather than a self-serve API, which matters for a bootstrapped project.

**Recommendation:** Deepgram (Flux, for the built-in turn detection) or AssemblyAI for English. Sarvam Saaras v3 for Telugu — same reasoning as TTS above.

---

## 7. LLM strategy — this is where I'd most directly challenge the brief's framing

### Does this need a large reasoning model? Mostly no.
The actual reasoning load per turn in your use case (understand "I was absent because my grandmother was in the hospital," extract a reason, decide the next question, detect when the conversation is complete) is not a hard reasoning problem — it's closer to structured intent classification + slot-filling with natural-language wrapping. This is squarely in "small/fast model" territory, not "frontier reasoning model" territory.

**Groq's LPU-hosted open models** deliver genuinely large latency wins here: Llama 3.3 70B running at ~276+ tokens/sec on Groq vs. ~40–80 tokens/sec for GPT-4o on OpenAI's standard API (Source: apiscout.dev, 2026), and independent testing puts full voice-pipeline latency (STT + LLM + TTS) at ~330ms using Groq vs. ~880ms using an H100-hosted equivalent (Source: neuraplus-ai.github.io, 2026 — this is a third-party benchmark site, treat the exact numbers as illustrative rather than guaranteed on your traffic). Cost follows the same pattern: Groq's Llama 3.1 8B is $0.05/million input tokens; GPT-4o-mini is $0.15/$0.60 per million input/output (Source: baytechconsulting.com, aipricing.guru, 2026).

**Where you *do* want more model capability:** edge cases — an ambiguous or emotionally loaded response from a student, a request to speak to a human, detecting that the "reason for absence" needs escalation (e.g., mentions of a safety issue). My recommendation there isn't "use a bigger model for every turn" but "route": run the fast/cheap model by default, and have deterministic logic (keyword/intent triggers) escalate specific turns to a stronger model or to a human-handoff flow. This is standard practice in the platforms reviewed above (Vapi's server-side function calling, Bland's Pathways) and keeps both cost and latency low on the 95% of turns that don't need it.

### Cascaded vs. speech-to-speech — resolve this explicitly, don't default to whichever sounds more "cutting edge"
This is the architecture decision I think the brief under-weights. As of mid-2026:

- **Speech-to-speech models** (OpenAI Realtime `gpt-realtime`, Google Gemini Live) process audio-in/audio-out in a single model pass, cutting the STT→LLM→TTS latency chain. TTFA in independent testing ranges ~0.78s (xAI) to ~2.98s (Gemini 3.1 Flash Live), with OpenAI's `gpt-realtime-1.5` around 0.82s (Source: softcery.com Artificial Analysis-sourced benchmark, April 2026) — **notably, this is not obviously faster than a well-tuned cascaded pipeline** (§3 above put tuned cascaded at 600–900ms).
- **Cascaded pipelines** give you a text artifact at every stage — critical for exactly what your brief asks for: transcripts, structured summaries, audit logs, tool-calling for CSV-field extraction. Independent analysis is blunt about this trade-off: *"for agents that need 5+ tools with strict schema enforcement (booking, payments, healthcare intake, structured form filling), cascaded is the safer 2026 default"* (Source: futureagi.com, 2026) — **your absent-student use case is structured-form-filling.** Cascaded also remains the enterprise/compliance default because every stage is independently observable, loggable, and redactable (Source: deepgram.com, reactify-solutions.com, 2026).
- Speech-to-speech also currently has materially weaker language coverage — this matters directly for your Telugu roadmap, since neither OpenAI Realtime nor Gemini Live has anything close to Sarvam's Telugu depth.

**Recommendation:** cascaded architecture (STT → LLM with tool-calling → TTS), not speech-to-speech, for this entire project. This isn't a "settle for less exciting tech" call — it's the architecture every credible 2026 source converges on for exactly your requirements (structured extraction, auditability, non-English languages).

---

## 8. Cost — worked estimates, and why "cheaper than a human" isn't automatic in India

### Per-minute component cost (my synthesis of the sourced ranges above, self-built cascaded stack, English)

| Component | Range (₹/min) |
|---|---|
| Telephony (Plivo/Exotel local outbound) | ₹0.60–1.00 |
| STT (Deepgram/AssemblyAI) | ₹0.50–1.00 |
| LLM (Groq-hosted small/fast model) | ₹0.20–1.00 |
| TTS (Cartesia) | ₹1.00–2.00 |
| **Total (English, self-built)** | **~₹3–5/min** |

For Telugu, swap in Sarvam pricing (STT ₹1.5/min flat; TTS ~₹30 per 10k characters, which works out to roughly ₹2–3/min at typical conversational pace): expect **~₹4.50–7.50/min all-in** for Telugu, before infra/hosting overhead.

For context, if you instead *bought* a fully managed Indian voice-AI vendor (Gnani, Skit, Yellow.ai, etc.) rather than building, expect **₹4.50–9/min plus a platform fee of ₹1–6 lakh/month** at meaningful scale (Source: caller.digital, 2026) — that's the "buy" price, and it's the reason a build-your-own approach is worth the engineering investment for a project where voice quality is the whole point and long-term unit economics matter (e.g., if you later commercialize this for other colleges).

### Monthly cost at scale (assuming ~3 min average call, English, self-built stack, ~₹4/min all-in including infra amortization)

| Volume | Minutes/month | Approx. monthly cost |
|---|---|---|
| 100 calls | ~300 | ₹1,200–1,500 |
| 1,000 calls | ~3,000 | ₹12,000–15,000 |
| 10,000 calls | ~30,000 | ₹1.2–1.5 lakh |
| 100,000 calls | ~300,000 | ₹10–13 lakh (volume discounts typically kick in, bringing effective rate toward ₹3.5–4/min) |

These are component costs only — add DLT registration (~₹5,900 one-time + template fees), number rental (~₹250–1,000/month per number), hosting/infra for your orchestration layer, storage for recordings/transcripts (marginal), and engineering time.

### The human-calling comparison, done honestly for India
US-context comparisons (the kind that show up in most vendor blogs) compare AI at $0.05–0.25/min to a US call-center agent at $35–50k/year — a comparison that doesn't transfer to India. A campus/admin telecaller in India typically costs **₹15,000–25,000/month fully loaded**, and can plausibly handle 80–150 calls/day depending on call complexity — at ~2,500–3,500 calls/month and ~3 min average, that's roughly **₹2–3.5/min**, which is *at or below* the low end of your self-built AI cost, and meaningfully below a bought managed platform. 

**My take:** don't pitch this project on "AI is cheaper per minute than a human" in the Indian context — for your absent-student use case specifically, the real value is (a) every student gets called on the same day rather than admin staff working through a list over days, (b) structured, consistent data capture (reason, expected return date) instead of handwritten notes, (c) zero marginal cost to scale to every section/hostel simultaneously, and (d) it runs outside office hours. That's a genuinely strong pitch — it's just a different pitch than "cost savings."

---

## 9. Scalability

| Concurrency | What breaks first |
|---|---|
| 1 call | Nothing — this is where you validate conversation quality |
| 10 concurrent | Still trivial on any provider; useful for load-testing turn-detection tuning under real network jitter |
| 100 concurrent | Telephony provider's **channel/CPS (calls-per-second) limits** become the first bottleneck — Plivo's AI-agent tier, for example, is quoted at 50 concurrent calls / 3 CPS on its documented plan (Source: Plivo pricing page, 2026); you'll need to confirm and likely negotiate higher limits, or shard across multiple provider accounts/numbers |
| 1,000 concurrent | This is enterprise-scale telephony provisioning — direct carrier SIP trunking (the "20 lakh+ minutes/month" tier some sources describe going direct to Airtel/Jio) rather than a standard CPaaS plan (Source: caller.digital, 2026); at this point your LLM/STT/TTS provider rate limits and your own orchestration layer's horizontal scaling (stateless WebSocket workers behind a load balancer, session state in Redis/Postgres, a queue-throttled outbound dialer respecting CPS limits) become the binding constraints, not any single component |

**My take on architecture for this:** use a framework that already solves the concurrency/session-management problem rather than building it — LiveKit Agents and Pipecat both handle per-call session isolation, horizontal worker scaling, and WebRTC/SIP media at scale as first-class concerns (Source: multiple framework comparisons, 2026). Building your own WebSocket-per-call orchestrator from scratch is exactly the kind of "not your differentiator" engineering effort I'd avoid — your differentiator is conversation quality and domain flexibility, not real-time media infrastructure.

For a *campaign* use case specifically (call all absent students today), you also need a **rate-limited outbound dialer** — a queue that respects your telephony provider's CPS limit and retries on no-answer/busy according to a policy you define, independent of your real-time voice engine's own concurrency.

---

## 10. Indian telecom/legal — this needs actual legal review, not just engineering

I want to be direct about the limits of what I can tell you here: **this section should not be treated as legal advice, and several points below are genuinely unresolved gray areas that need a lawyer, not a search engine.**

**What's clear from current sources:**
- **DLT registration is mandatory** for any commercial/business outbound calling in India — register as a Principal Entity, register your number series and call templates, before making any calls (Source: TRAI TCCCPR framework, multiple 2026 compliance guides).
- **TRAI classifies AI-generated voices under existing robocall/TCPA-equivalent rules** — meaning your AI calling platform is legally treated the same as any automated dialing system, not as a novel unregulated category (Source: qcall.ai, 2026).
- **Following the 2026 IT Rules amendment, AI voice agents must self-identify as automated at the start of the call** and must not impersonate a specific real individual (Source: autointerviewai.com, 2026).
- **DPDP Act 2023 + DPDP Rules 2025** (notified Nov 13, 2025) govern what you can do with the *data* generated by the call — the recording, transcript, and any extracted fields are all "personal data." You need purpose-specific, informed consent (not just a TRAI dial-permission), a defined retention period, and — notably — **data localization**: Indian personal data should be processed/stored within India, and if you route audio through an international LLM/STT/TTS provider, you need to understand where that data actually flows (Source: caller.digital, gistly.ai, 2026). This is directly relevant to your provider choice — Sarvam explicitly markets India-only data processing/storage as a compliance feature; verify the equivalent for whichever English-stack providers you pick.
- **Indian law is generally one-party consent for recording** (if your institution is a participant in the call, you can record it) — but DPDP's *processing* consent requirement is separate and additional to this (Source: frejun.com, caller.digital, 2026).

**The genuine gray area for your specific use case:** TRAI's number-series framework is built around **promotional (140-series)** vs **transactional/service (1600-series, BFSI-oriented)** calls. A college calling an already-enrolled student's registered number to ask about an absence is neither classic marketing nor a BFSI transaction — it's institutional/administrative outreach to an existing relationship. None of the sources I found address this category directly. **Recommendation: get this specific classification confirmed with your DLT-registration provider or telecom counsel before your first real campaign** — misclassifying it risks calls being silently dropped (wrong series) or, worse, a DND/consent complaint if students haven't been asked to opt in to this kind of automated call. A pragmatic mitigation: collect explicit consent for "the college may call you or your guardian using an automated system regarding attendance" at admission/enrollment time, which sidesteps most of the ambiguity.

- **Recording retention**: sector guides cite RBI-style retention windows (6 months–3 years) for regulated (BFSI) sectors; there's no equivalent published standard for education specifically — set a defined, disclosed retention policy rather than keeping everything indefinitely, both for DPDP compliance and to bound your own storage costs.

---

## 11. English → Telugu: what actually changes

This is the section where I'd tell you most directly: **treat Phase 2 as a second STT/TTS integration project, not a configuration change.**

What changes:
1. **STT and TTS providers swap entirely.** Deepgram/AssemblyAI (STT) and Cartesia/ElevenLabs (TTS) — your likely English-phase choices — do not have credible production Telugu. **Sarvam AI (Saaras v3 for STT, Bulbul V3 for TTS)** is the standout India-specific option, explicitly built and benchmarked on Telugu, with sub-250ms/sub-150ms latency claims, native Telugu-English code-switching ("Tenglish"), and correct handling of Indian names/numbers (Source: sarvam.ai product pages, 2026 — these are provider claims; validate WER/latency against your own call audio before committing, exactly as the STT benchmarking sources above caution generally).
2. **Code-switching is not an edge case in Telugu, it's the norm.** Real conversational Telugu (as shown in Sarvam's own example transcripts) constantly mixes in English words mid-sentence ("naa account balance check cheyali"). An STT/TTS stack that treats this as noise will fail constantly; Sarvam's models are explicitly trained for this.
3. **The LLM layer can likely stay similar** (most frontier and mid-tier LLMs handle Telugu text reasonably for understanding intent, even if you wouldn't trust them for Telugu *voice*) — but you should validate that your chosen model doesn't silently default to Hindi or standard-register Telugu when the input transcript contains colloquial or regional phrasing.
4. **Turn-detection tuning likely needs to be redone**, not reused — Telugu sentence rhythm, pause patterns, and prosody differ from English, and the semantic/prosody turn-detection models discussed in §4 are typically trained/tuned on specific language data.
5. **Regional variation and dialect**: sourced comparisons note real accuracy variance by region even within a single Indian language (e.g., one WER benchmark noted "Delhi Hindi" claims collapsing on "Lucknow Awadhi-influenced Hindi" in practice — Source: caller.digital, 2026). The equivalent risk exists for Telugu across Telangana/Andhra/coastal-vs-Rayalaseema variation. **Don't accept a vendor's aggregate Telugu WER claim — test against audio from your actual target population** (your parents' boutique customer base or students' likely demographic, depending on which project this is for).

**Biggest current ecosystem gap:** there is no evidence of a mature, production-proven **speech-to-speech** option for Telugu (the OpenAI Realtime / Gemini Live category) — reinforcing the cascaded-architecture recommendation in §7, since it's the only path with credible Telugu coverage at all.

---

## 12. Competitive landscape

Two genuinely different categories are relevant to you, and I'd resist conflating them:

**Global/English-first voice-agent platforms** (Retell AI, Vapi, Bland AI, plus the open-source LiveKit Agents/Pipecat): differentiate mainly on latency consistency, developer control, and pricing transparency — not on anything India- or Telugu-specific. Independent 2026 head-to-head testing found Retell fastest/most consistent (~600–620ms median, ~$0.07/min), Vapi most flexible (component-level control, BYOK, effective cost $0.12–0.33/min once the full stack is added), Bland strongest for high-volume deterministic outbound flows (~700–900ms, bundled pricing) (Source: techsy.io independent build-on-all-three test, 2026). None of these have meaningful Telugu.

**India-specific voice AI vendors** (Gnani.ai, Skit.ai, Yellow.ai, Bolna, Sarvam, Caller Digital, Squadstack): this is the more relevant comparison set for your roadmap.
- **Gnani.ai** is the largest India-headquartered player by scale (30M+ daily conversations, 40+ languages/dialects including deep Telugu coverage, 14M hours of Indian telephony training data, government IndiaAI Mission selection) — but it's enterprise-only with custom pricing, not a self-serve API you'd build a prototype on (Source: caller.digital, gnani.ai, 2026).
- **Skit.ai** — outbound-native, strong in collections/insurance, "Hyper-Real" prosody claims (provider claim).
- **Bolna** — the most directly relevant to your build-it-yourself plan: an open-source agent framework that **ships Sarvam + Twilio-India as defaults**, i.e., someone has already assembled roughly the stack this report recommends. Worth evaluating as a starting point rather than building your orchestration layer fully from scratch (Source: thinnest.ai, bolna.ai, 2026).
- **Sarvam AI** — not a full voice-agent platform, but the STT/TTS layer underlying several of the above; you can use it directly.

**My take on what actually differentiates the strongest systems** (synthesizing across all the sourced comparisons rather than any single vendor's marketing): it is *not* raw model quality — WER and TTS MOS scores have converged across top providers. The differentiators that show up consistently across independent 2026 testing are: (1) turn-detection tuning specific to the target language/population, (2) pricing transparency vs. hidden per-component markups, and (3) for the India-specific vendors, actual dialect/regional coverage validated on real audio rather than a single benchmark language variant. Marketing claims about "hyper-real" or "indistinguishable from human" should be discounted heavily — none of the independent, third-party benchmarks I found support a categorical "indistinguishable" claim for any vendor.

---

## 13. Critical risks — direct challenges to the project

- **Robotic voice / high latency**: the median achievable latency in 2026 (600–900ms, per §3) is still roughly 3–4x slower than human-to-human turn-taking (~200ms). No amount of vendor selection closes this gap entirely — manage expectations that "as close to human as technically possible" still has a perceptible, if small, robotic edge in 2026. This isn't a solvable-with-more-budget problem; it's close to the current technical frontier.
- **Poor turn detection / false interruptions**: this is the failure mode most likely to make the *English* version feel bad even with a good voice — and it needs real-call tuning, not just picking a good-sounding vendor.
- **Telugu quality risk is the single biggest project risk in your roadmap**, not a secondary concern — you have exactly one credible specialist vendor (Sarvam) for the full stack; if its Telugu performance on your actual population doesn't hold up, there is no obvious second choice at comparable maturity today.
- **Hallucination / incorrect information extraction**: for the absent-student use case, an LLM inferring a plausible-but-wrong "reason for absence" or "expected return date" is a real risk with real consequences (a college acting on fabricated data). Mitigate with strict tool-calling/function-schema enforcement (part of why cascaded > speech-to-speech here), and a "low confidence → flag for human review" path rather than trusting every extraction.
- **Telecom/regulatory risk**: silently dropped calls due to DLT misclassification, or a DPDP complaint from a student/parent about an unconsented automated call, are both plausible operational failure modes, not hypothetical ones — build the consent-capture step into your admin/enrollment flow now, not as an afterthought before "moving to production" (your prototype-phase "no auth needed" plan is fine for internal testing, but the *consent and DLT compliance* pieces are not something you can defer the same way — they gate whether calls connect at all).
- **Concurrency/provider lock-in**: standard CPaaS concurrency tiers (tens of concurrent calls) will not support a "call every absent student across a large college simultaneously" campaign without either a higher-tier plan or a properly throttled dialer — plan the campaign dialer's pacing explicitly rather than assuming the telephony provider absorbs bursts for free.
- **Cost risk at scale**: the ₹4-9/min range for a bought platform, or ₹3-7/min for a well-built one, is a real ongoing cost once you're calling thousands of students per campaign across multiple colleges — model this against your actual expected campaign frequency before assuming "AI is basically free at scale."

---

## 14. Recommended technology strategy

*(Recommendations, explicitly — not facts. Multiple viable alternatives are noted for each.)*

1. **Telephony**: Start on **Plivo** (cheapest, LiveKit/Pipecat-native, fast DID provisioning). Move to **Exotel** if you want DLT/compliance handled for you at a modest premium, or once call volume justifies enterprise support. Avoid Twilio for India-domestic calling.
2. **Indian number approach**: DLT-registered virtual number via the chosen CPaaS provider — not SIM/eSIM. Start DLT Principal Entity registration in parallel with prototyping, since it's the longest lead-time item.
3. **STT**: Deepgram (Flux, for built-in turn detection) or AssemblyAI for English. **Sarvam Saaras v3** for Telugu — no credible alternative at comparable maturity.
4. **TTS**: **Cartesia Sonic** for English (latency-critical). **Sarvam Bulbul V3** for Telugu.
5. **LLM strategy**: cascaded (not speech-to-speech) architecture throughout, for tool-calling reliability and Telugu support. Default to a fast/cheap model (Groq-hosted Llama 3.3-class, or GPT-4o-mini-class) for standard turns; add deterministic escalation logic (not a bigger model on every turn) for ambiguous/sensitive responses.
6. **Real-time communication architecture**: build on **LiveKit Agents** or **Pipecat** rather than a from-scratch WebSocket orchestrator — both solve session isolation, concurrency scaling, and telephony integration as first-class problems, and both plug directly into Plivo/Exotel and every STT/TTS/LLM provider above. Consider evaluating **Bolna** directly as a starting scaffold, since it's already assembled close to this exact stack for the Indian market.
7. **Backend architecture**: FastAPI (or equivalent) admin/API layer + your chosen agent framework for the real-time voice layer; a queue-based outbound campaign dialer that respects provider CPS limits; async workers for post-call processing (summary generation, structured field extraction, export).
8. **Database**: Postgres for structured data (contacts, campaigns, calls, extracted fields, status) — this is a relational, reporting-heavy workload, not a vector/document-store problem at this stage. Object storage (S3-compatible, India-region for data-localization) for recordings.
9. **Deployment**: containerized, deployed in an India-region cloud (Mumbai) for DPDP data-localization alignment. Managed LiveKit Cloud or Pipecat Cloud is a reasonable Phase-1 choice to avoid owning real-time media infra before you've validated conversation quality; revisit self-hosting purely as a cost optimization once volume justifies it.
10. **Development roadmap**:
    - **Phase 0 (now)**: single-number English prototype, no auth, cascaded pipeline (Plivo/Exotel + Deepgram + fast LLM + Cartesia) on LiveKit Agents or Pipecat, validated against real (not scripted) test calls for turn-detection quality.
    - **Phase 1**: DLT registration + consent-capture flow + admin CSV upload/campaign/export UI; move from single-call testing to a rate-limited campaign dialer; nail down the absence-call domain logic (question flow, structured extraction schema, escalation rules).
    - **Phase 2**: Telugu — swap STT/TTS to Sarvam, re-tune turn detection on real Telugu call audio, validate on your actual target population's dialect before declaring it production-ready.
    - **Phase 3**: Tanglish code-switching, then generalize the domain layer (question flows, extraction schemas) so new use-cases beyond "absent students" are configuration, not new code.
    - **Phase 4+**: additional Indian languages, scale-out concurrency, and only then revisit authentication/production hardening.

---

## Sources
This report draws on ~25 web searches across current (2026) provider documentation, independent benchmarking sites, and industry comparison articles, conducted August 2026. Key sources cited inline include: Exotel, Plivo, and Twilio pricing/documentation pages; caller.digital, frejun.com, and awaaz.ai telephony comparison guides; TRAI-compliance guides (frejun.com, autointerviewai.com, ondial.ai, expressivr.com); DPDP Act guides (recordinglaw.com, caller.digital, gistly.ai); voice-platform comparisons (techsy.io, retellai.com, bland.ai, tested.media, alphacorp.ai); framework comparisons (thinnest.ai, forasoft.com, evalgent.com, techsy.io); STT/TTS benchmarks (assemblyai.com, futureagi.com, coval.ai, deepgram.com, gladia.io, codesota.com, burki.dev); Sarvam AI product pages; Groq/inference benchmarks (baytechconsulting.com, neuraplus-ai.github.io, apiscout.dev); cascaded-vs-speech-to-speech analysis (futureagi.com, deepgram.com, inworld.ai, reactify-solutions.com, softcery.com); cost models (inworld.ai, retellai.com, bitbytes.io, ravan.ai, caller.digital, famulor.io, klariqo.com); and Indian voice-AI competitor pages (gnani.ai, lumay.ai, vyora.ai, carmaone.ai).

**Given how fast this market is moving (several sources note major model/pricing changes within the last 1–2 months), re-verify pricing and latency figures directly against provider pages before committing to a contract — treat everything above as a well-sourced starting map, not a final quote.**
