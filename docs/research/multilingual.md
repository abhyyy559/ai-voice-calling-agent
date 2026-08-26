# Phase-2 Multilingual Research: Fluent Telugu, Tenglish Code-Switching & Natural Cloned Voices

*Generated: 2026-08-26 · Author: multilingual-researcher agent · Status: DECISION DOCUMENT (planning artifact only — per project guardrails, no Telugu implementation work starts until Phase-2 kickoff)*
*Method: live web research across ~20 queries (vendor docs, independent benchmarks, pricing trackers, GitHub, arXiv). Sources dated inline. Confidence labels:*
- **[VENDOR]** = vendor-published claim, unaudited
- **[INDEP]** = independent/third-party measurement or benchmark
- **[EST]** = our arithmetic from stated assumptions — verify before contracting

---

## 0. TL;DR Decision Table

| Component | Recommendation | ₹/connect-min [EST] | Why |
|---|---|---|---|
| STT | **Sarvam Saaras v3 streaming** (A/B vs incumbent Deepgram Nova-3 `te`, which added Telugu May 2026) | ₹0.50 API (self-host path ₹0.10–0.25 later) | Only streaming ASR with published IndicVoices/code-mix numbers + 8 kHz telephony focus |
| LLM | **Sarvam-M / Sarvam-30B (non-think)** primary, rule-based escalation to Groq GPT-OSS-120B | ₹0.05–0.30 | Best public Telugu/Tenglish evidence (Indic Vibe Check 8.12/9 [VENDOR]); token cost negligible either way |
| TTS | **Sarvam Bulbul v3 catalog voices** at launch; enterprise consent-cloning for custom voices | ₹0.5–2.4 (dominant cost) | Top Indic naturalness (blind-study claim), sub-250 ms TTFB, native 8 kHz output |
| Cloning | **Phase 2a: Sarvam consent-based enterprise cloning. Phase 2b (scale): self-host commercial-safe stack — but no proven open Telugu cloner exists today (gap, see §3.4)** | ₹0 (enterprise deal) / ₹0.1–0.3 amortized | F5-TTS & XTTS-v2 are license-barred for commercial use AND lack Telugu |
| **ALL-IN** | | **≈ ₹1.1–2.0/min** | Comfortably under ₹3.5 competitor line with ~₹0.8 telephony (§5) |

---

## 1. STT — Telugu + Code-Switched Speech on Real 8 kHz Phone Audio

### 1.1 Comparison

| Model | Telugu WER (best available) | Code-switching | Streaming / latency | 8 kHz telephony fit | Price | License / hosting |
|---|---|---|---|---|---|---|
| **Sarvam Saaras v3** (Feb 2026) | ~19.3% avg IndicVoices 10-lang; code-mixed <12%, Hindi <8%, Indic-English <6% [VENDOR, third-party roundup concurs] | Native (trained-in; dedicated `codemix` output mode) | Yes — WebSocket, <150 ms first-token "Fast" mode [VENDOR] | Explicitly positioned for 8 kHz telephony; LiveKit/Pipecat integrations exist | **₹30/hr = ₹0.50/min** official API pricing page ⚠️ marketing pages show ₹1.5/min — reconcile before contract | Closed API, India-hosted, DPDP/SOC2 claims |
| **Deepgram Nova-3** (incumbent vendor) | Telugu (`te`) GA; accuracy improvements announced May 2026; no public Telugu WER [VENDOR] | Multilingual code-switching endpoint + keyterm prompting [VENDOR] | Yes, <300 ms claim [VENDOR]; Flux adds turn detection (English/multi — **no Telugu**) | Telephony-grade heritage | ~$0.0043–0.0074/min ≈ ₹0.37–0.65/min [INDEP tracker] | Closed API; US-hosted by default (data-residency question — see compliance-agent) |
| **AI4Bharat IndicWhisper** (fine-tuned Whisper, MIT) | **28.8% avg Telugu** across Vistaar benchmarks (Kathbath 25.0, KB-hard 27.8, FLEURS 25.4, IndicTTS 33.8, MUCS 32.1) [INDEP, AI4Bharat paper] | Weak — trained on monolingual Indic corpora | No native streaming (Whisper seq2seq, chunked hacks only) | Poor — AI4Bharat itself lists "handle 8 kHz telephony data" as *future work* | Free weights; GPU-hour only | MIT, self-host, weights on HF/E2E object store |
| **AI4Bharat IndicConformer 600M** (multi) + mono Telugu large | Vaani Hindi 13.2%; no published Telugu headline in card; Vistaar-family lineage suggests mid-20s% [INDEP partial] | Monolingual-leaning; multi model covers 22 langs but not mixed-utterance optimized | RNNT decoder is streaming-*capable* but not packaged as a low-latency server | Same caveat as above | Free weights; ~600M params runs many streams/GPU | MIT, NeMo ecosystem |
| **Whisper-large-v3 (+ fine-tunes)** | Zero-shot Indic far behind Indic-tuned models [INDEP roundups]; community Hindi LoRA cut FLEURS 35.6→22.3% — directionally instructive, no equivalent public Telugu fine-tune found | Poor zero-shot; synthetic-data CS fine-tuning is research-grade | No native streaming | Poor (studio-domain training) | Free weights | Apache/MIT ecosystem; turbo variant fastest |
| **Gnani Prisma v2.5** | "<4% WER Indian English", "#1 on Kathbath-Noisy 8 kHz in 8/9 languages", 96% code-switch accuracy — **all [VENDOR]**, methodology unpublished | Native, BFSI-domain vocabulary (PAN/UPI/EMI…) | Yes, sub-200 ms [VENDOR] | Purpose-built on 14M hrs telephonic audio [VENDOR] | ~₹27/hr via API reseller [INDEP tracker]; direct = enterprise quote | Closed; on-prem option |

### 1.2 Economics: API vs self-host [EST]

Self-host math form requested: **₹/hr ÷ concurrent streams**. Reference GPU rates (E2E Networks, INR, 2026): L4 ₹49/hr · A100-80GB ₹189/hr (spot ₹66) · H100 ₹362/hr (spot ₹70–180). IndiaAI-subsidised compute ~₹67–92/GPU-hr if approved.

| Scenario | Math | ₹/min |
|---|---|---|
| Saaras v3 API | ₹30/hr ÷ 60 | **0.50** |
| Deepgram Nova-3 API | $0.005 ± /min × ₹87/$ | **0.44** |
| faster-whisper-lg-v3 / Conformer on L4, 12 concurrent streams (optimistic) | ₹49 ÷ 60 ÷ 12 | 0.07 |
| Same, 5 concurrent (conservative, streaming chunks) | ₹49 ÷ 60 ÷ 5 | 0.16 |
| On A100-80GB spot, 25 streams | ₹66 ÷ 60 ÷ 25 | 0.04 |
| Add ops overhead ×2 (monitoring, failover, idle GPU in bursty campaign traffic) | — | **0.10–0.35 realistic** |

Break-even vs Saaras API ≈ 1.6 continuously-active streams (raw GPU), realistically ~6–10 average with utilization waste. Worth it only at steady campaign volume (>~50k min/month) — and **accuracy risk remains**: open models are demonstrably weaker on noisy/telephony audio, which is exactly our domain.

> **RECOMMENDATION (STT): Ship Phase-2 on Sarvam Saaras v3 streaming (₹0.50/min), keeping Deepgram Nova-3 `te` as the cheap-to-integrate A/B arm since it's already wired into `/voice-agent`; revisit self-hosting (Conformer-RNNT on spot A100) only after qa-eval proves ≥25k min/month sustained and open models close the 8 kHz noise gap.**

---

## 2. LLM — Native Spoken Telugu + Tenglish, Tool-Calling, Rock-Bottom Tokens

### 2.1 Evidence table

| Model | Telugu / Tenglish evidence | Tool-calling | Latency profile | Price (in/out per 1M tok) |
|---|---|---|---|---|
| **Sarvam-M → Sarvam 30B/105B family** (24B Mistral-Small-derived → newer MoE) | **Best available**: Indic Vibe Check **8.12/9 avg across 11 langs** vs Llama-4-Scout 7.58 & Llama-3.3-70B 6.93; MMLU-IN 0.79; romanized-Telugu-class GSM8K +86% vs base; Telugu = 8% of SFT mix; trained on formal + code-mixed + romanized forms [VENDOR — Sarvam's own evals; treat as favorable-but-interested]. Independent Artificial Analysis ranks its *general* intelligence low (#121/137) → fine for constrained call flows, not open-ended reasoning | Documented think/non-think modes; **function-calling must be verified in our harness — no independent benchmark row** [GAP] | India-hosted; ~100 tok/s (high-concurrency config) to ~300 tok/s (low-concurrency) [VENDOR] | Sarvam 105B: **₹29.28 / ₹73.20** official page; Sarvam-M ≈ ₹35/₹35 via resellers |
| **Groq-hosted open models** (current stack's host) | No Telugu-specific public benchmarks for any of them — **evidence gap**. General multilingual signals only | Yes (OpenAI-compatible tools) | TTFT ~0.2–0.7 s measured [INDEP, Artificial Analysis] | GPT-OSS-120B **$0.15/$0.60**; GPT-OSS-20B $0.075/$0.30; Qwen3-32B $0.29/$0.59; Gemma-2-9B $0.20/$0.20 (⚠️ Llama-3.3-70B & 3.1-8B **deprecated Aug 16 2026** — migration forced anyway) |
| **DeepSeek-V3/R1** | Strong MMMLU/multilingual aggregates but training is English+Chinese-dominant [INDEP tech report]; no Telugu conversational evidence found | Yes | Cheap but heavier TTFT; R1 thinking incompatible with voice budgets | $0.27/$1.10 (V3) [INDEP tracker] |
| **Gemma 2/3 27B** | Gemma 3: 140+ languages in pretraining [VENDOR]; won multilingual category vs Qwen-3.5-27B 83.1% vs 71.4% in one third-party suite [INDEP, single source] | Yes | Good on vLLM/Groq | $0.10/$0.20 Deepinfra (cheapest capable tier) [INDEP]; Sarvam also hosts a Gemma-4-class model at ₹36.60/₹91.50 |
| **Qwen 2.5 / 3** | CJK-optimized multilingual; strong general benchmarks [INDEP]; Telugu anecdotal only | Yes | Excellent on Groq LPU | See Groq rows above |
| **Llama-3.x** | Weakest Indic showing among candidates (Indic Vibe Check 6.93 for 70B [VENDOR]) | Yes | — | Deprecation pressure on Groq |

**Honest read:** there is **no rigorous, independent, spoken-register Telugu benchmark** for any global-open model. The only Telugu-relevant head-to-head that exists is Sarvam's own Indic Vibe Check — favorable to Sarvam, unsurprisingly. Everything else is proxy evidence (multilingual aggregates ≠ conversational Tenglish fluency).

### 2.2 Translation-in-the-middle: measure, don't guess

Option: STT (Telugu) → IndicTrans2 → English LLM → IndicTrans2 → Telugu TTS.

- IndicTrans2-distilled (~250M) via CTranslate2-int8: ~**40 ms/clause** on GPU per one open pipeline build; full ASR+NMT+TTS pipeline demonstrated "<300 ms" target [INDEP, single hobby-grade repo — weak evidence]
- AI4Bharat's hosted demo translates a sentence in 2–3 s; naive HF inference took 17 s in a user report [INDEP issue tracker] — i.e., **latency is entirely an engineering variable**, 100 ms possible, seconds likely if done casually
- Structural costs regardless of speed: **error propagation** through two NMT hops, nuance loss on pivot, and doubled failure surface — flagged by AI4Bharat themselves as reasons they built direct M2M models

**Verdict vs our ≤900 ms median turn target:** a tight clause-level pivot adds ~100–300 ms on top of an already-tight cascade (Saaras 150 ms + LLM 250–500 ms + Bulbul 250 ms ⇒ ~650–900 ms). Translation-in-the-middle **does not fit inside the budget with headroom** and degrades extraction reliability (FR-12 escalation logic depends on trustworthy transcripts). It is acceptable **only** as an emergency fallback for pure-Telugu turns if the primary LLM fumbles — never as the standing path.

> **RECOMMENDATION (LLM): Primary = Sarvam-M/Sarvam-30B in non-think mode, prompt-locked to our domain-config flow with tool schemas; validate function-calling + extraction accuracy in the qa-eval harness BEFORE commitment (the one unverified load-bearing claim). Escalation tier = Groq GPT-OSS-120B for hard turns (rule-based escalation per locked architecture — note Groq's Aug-2026 model deprecations force a Phase-1 migration anyway). Skip translation-in-the-middle; keep distilled IndicTrans2 warm only as fallback. Token cost is a rounding error (<₹0.05–0.30/min) — decide on quality, not price.**

---

## 3. TTS — Most-Human Telugu + Voice Cloning

### 3.1 Comparison

| Engine | Telugu naturalness | TTFB / streaming | Cloning | Price → ₹/agent-min [EST] | License / risk |
|---|---|---|---|---|---|
| **Sarvam Bulbul v3** (Feb 2026) | 11 langs incl Telugu; 30–35 persona voices; **won Josh Talks blind study (20k+ votes)** [VENDOR]; docs candidly admit per-language voice-quality variance | **<250 ms** WebSocket [VENDOR]; 8 kHz mulaw supported (native telephony) | **Consent-based enterprise cloning** — blog demos Telugu generation from reference clip; ⚠️ **no self-serve cloning product as of Aug 2026** (two sources concur) | Official ₹30/10k chars (beta); v2 legacy ₹15/10k. Agent speaks ~350–600 Telugu-script chars/connect-min ⇒ **₹1.05–1.80/min** (v3) or **₹0.53–0.90** (v2) [EST] | Closed API, India-resident, SOC2/DPDP claims |
| **Cartesia Sonic** (incumbent vendor) | Dedicated Telugu page; "native prosody" [VENDOR]; no independent Telugu MOS found | **<90 ms** claim [VENDOR] — best-in-class | Instant cloning self-serve | ~$0.065/1k chars [INDEP tracker] ⇒ ~₹5/1k ⇒ **₹1.8–3.0/min** [EST] | Closed, US-hosted |
| **ElevenLabs (Multilingual v2/v3)** | 70+ langs claimed; Telugu present in v3-era coverage [VENDOR]; quality on Dravidian langs consistently rated below Hindi in community tests [INDEP anecdotes] | ~500 ms; Flash cheaper/faster [INDEP] | IVC (1-min sample) + PVC (30-min, 95% likeness, identity verification) | Business-tier self-publishes "**as low as $0.05/min**"; retail effective $0.18–0.30/1k chars [INDEP] ⇒ **₹4–6/min** realistic | Closed, expensive, strongest cloning-consent tooling |
| **Gnani Timbre v2.5** (beta) | MOS 4.23 claim, <250 ms p95 [VENDOR]; cloning for 12 Indian languages announced [INDEP press] | Beta | Yes (announced) | Unpublished (enterprise) | Closed; early-stage risk |
| **AI4Bharat Indic-TTS** (FastPitch+HiFi-GAN, ICASSP'23) | Solid intelligibility, dated prosody; Telugu included in 13-lang release [INDEP] | Non-streaming batch design | None | Free weights; GPU-only ⇒ **₹0.05–0.15/min** amortized [EST] | Open (Bhashini); verify fork license |
| **AI4Bharat Indic Parler-TTS Mini** | 21 langs incl Telugu; speaker-similarity ~88–89 (Telugu row) on their evals [VENDOR/INDEP]; description-controlled style | Chunk-streamable, slower than Bulbul-class | **No true cloning** (description-driven voice creation) | Apache-2.0 family [INDEP registry] | Best open *catalog* option; needs own serving layer |
| **F5-TTS** | Top-tier English/Chinese prosody; **no Telugu** [INDEP] | ~2.8 s to first audio (non-causal design) [INDEP] | Zero-shot, excellent (EN/ZH) | Free weights | ❌ **CC-BY-NC-4.0 — non-commercial. Cannot ship.** |
| **XTTS-v2 (Coqui)** | 17 langs, **no Telugu**; MOS ~4.0 [INDEP] | ~3.5 s TTFA | Zero-shot, mature ecosystem | Free weights | ❌ **CPML non-commercial; company defunct — no one to license from.** |
| **Chatterbox / Fish Speech / Kokoro** | Commercial-safe licenses (MIT/Apache) [INDEP]; Chatterbox reportedly beats ElevenLabs in ~65% blind tests [VENDOR-of-claim, single source]; **Telugu support: none documented** [GAP] | Varies; Kokoro fast but no cloning | Chatterbox/Fish yes (EN-centric) | Free weights | ✅ licenses, ❌ Telugu |

### 3.2 The cloning reality check (read this twice)

The two most famous open-source cloners — **F5-TTS (CC-BY-NC) and XTTS-v2 (CPML) — are both legally barred from commercial products AND neither speaks Telugu.** The commercial-safe open cloners (Chatterbox, Fish Speech, OpenVoice-v2) have **no documented Telugu capability** as of this research date. Practitioner guidance converges on the same conclusion: stay on managed APIs below ~10M chars/year; self-host only permissive models at scale [INDEP, Forasoft 2026 guide + Spheron deployment guide].

Self-host TTS economics when it eventually makes sense [EST]: XTTS-class throughput ~600 chars/sec/GPU [INDEP, Spheron benchmark] ⇒ one L4 (₹49/hr) could theoretically carry dozens of streams; realistic streaming Parler/Bulbud-class serving ⇒ **₹0.05–0.25/min** amortized. The savings vs Bulbul API are real but second-order until volume is large — and they buy you *worse* Telugu naturalness today.

### 3.3 Latency budget check

Cascade sum (median): Saaras fast-mode first-token <150 ms [VENDOR] + LLM TTFT 250–500 ms [INDEP] + Bulbul first-byte <250 ms [VENDOR] ≈ **650–900 ms + network** — inside our ≤900 ms target, with zero slack. Cartesia's <90 ms TTFB is the escape hatch if we blow the budget, at ~2× TTS cost and offshore hosting.

> **RECOMMENDATION (TTS): Launch on Bulbul v3 catalog voices (per-language recommended-speaker mapping from Sarvam's own docs) with Bulbul v2 pricing negotiated if volume justifies; contract Sarvam's consent-based enterprise cloning as the custom-voice path (it is the only demonstrated Telugu-capable cloner reachable today). Keep Cartesia Sonic wired as latency/quality fallback behind our existing provider-abstraction. Do NOT burn sprints on open-source Telugu TTS in Phase 2 — revisit Indic Parler-TTS self-hosting at >1M chars/month.**

---

## 4. Voice-Selection UX — What Platforms Do, What We Copy

Precedent observed (Aug 2026):

| Platform | Pattern |
|---|---|
| **Vapi** | `assistant.voice = {provider, voiceId}` per assistant; pluggable providers (ElevenLabs, Smallest-Lightning built-in…); **voice-fallback chain** config; providers expose "pick a voice **or clone your own from a few seconds of audio**" inside assistant settings |
| **Retell AI** | Per-agent voice picker over categorized voice library; multilingual voices tagged per language; agent-level config object |
| **ElevenLabs** | Searchable Voice Library (use-case tags, instant previews); two cloning tiers — Instant (1-min sample, seconds) vs Professional (30-min+, 4–6 h train, **identity verification + consent capture** before activation) |
| **Smallest AI (via Vapi)** | 217-voice catalog, ~100 ms streaming, clone-from-seconds flow embedded in partner dashboards |
| **Sarvam** | Publishes **per-language recommended voices** (docs admit quality varies by language) — rare honesty worth copying outright |

**Copy-list for our admin dashboard (frontend-agent + conversation-ai-agent handoff):**
1. `voice_id` lives on the **agent config / domain-config**, never hardcoded (consistent with PRD §4.3 config-over-code rule)
2. Curated **Telugu-first voice gallery** with per-language recommended mapping + inline `<audio>` preview before commit
3. Clone flow = upload ≥30 s clean sample → recorded verbal-consent statement + checkbox (DPDP; compliance-agent owns wording) → async clone job → **QC preview gate** → activate per agent
4. Voice **fallback chain** (primary → secondary provider) so a TTS outage never dead-airs a call
5. Never surface raw provider IDs/slugs to customers; friendly names + samples only

---

## 5. Final Recommended Phase-2 Stack

Assumptions: $1 ≈ ₹87 [EST]; connect-minute = billed phone minute; agent speaks ~45% of airtime (~350–600 Telugu-script chars); LLM ≈ 2.5–4k tokens/connect-min combined.

| # | Component | Choice | ₹/connect-min | Quality verdict | Risk |
|---|---|---|---|---|---|
| 1 | Telephony | Plivo (locked) | ~0.80 | Proven | Low (existing) |
| 2 | STT | **Saaras v3 streaming** (A/B: Deepgram Nova-3 `te`) | **0.50** (DG ≈ 0.44) | Best public Indic/code-mix numbers; 8 kHz-focused | Sarvam pricing-page inconsistency (₹30/hr vs ₹1.5/min marketing) — resolve pre-contract; single-vendor concentration |
| 3 | LLM | **Sarvam-M/30B non-think** + Groq GPT-OSS-120B escalation | **0.05–0.30** | Only model with published Tenglish/Telugu conversational evidence; general reasoning mediocre but sufficient for config-driven flows | **Function-calling unverified independently** — hard-gate on qa-eval results |
| 4 | TTS | **Bulbul v3 catalog** (negotiate v2 pricing) | **0.55–1.80** | Best Indic naturalness claim + blind-study win; 8 kHz native | No self-serve cloning; per-language voice variance is real |
| 5 | Cloning | **Sarvam consent-based enterprise cloning**; Phase-2b option: self-host permissive stack when (a) volume >1M chars/mo AND (b) a Telugu-capable commercial-safe cloner ships | ~0 (bundled) | Only demonstrated Telugu cloner | Enterprise-deal dependency; open-source Telugu cloning **does not exist yet** — biggest strategic gap on this page |
| 6 | Orchestration | LiveKit Agents (locked) — swap STT/TTS providers via existing abstraction | — | — | Low |
| **Σ** | | | **≈ 1.90–3.40 sticker → 1.1–2.0 expected** | | **vs ₹3.5/min competitor + ₹0.8 telephony: PASS with 35–65% headroom** |

**Sensitivity:** worst case (all stickers, max chars, v3 pricing) ≈ ₹3.40 — still under the line but thin; mitigations in order: negotiate v2-rate TTS (−₹0.5–0.9), shift default voices to shorter phrasings in domain-config, move TTS in-house at scale (−₹1+).

**Compliance notes carried forward:** consent capture precedes any cloning (DPDP); recording-retention and disclosure scripts unchanged from Phase-1 compliance-agent work; Sarvam's India-residency claim supports localization posture, Deepgram's does not — factor into the STT A/B weighting.

---

## 6. Sources (accessed 2026-08-26)

1. Sarvam — Saaras v3 launch blog (2026-02-10), STT product page (upd. 2026-05-06), official API pricing page, Bulbul docs & product pages, Bulbul v3 blog (2026-02-05) — sarvam.ai / docs.sarvam.ai
2. Third-party STT roundup: Saaras v3 vs Whisper vs Google Chirp (anuragwagh.com, 2026-07-23) — independent IndicVoices/Odia numbers
3. AI4Bharat — Vistaar paper + repo (arXiv 2305.15386, INTERSPEECH 2023), IndicConformer HF card (upd. 2026-03-02), Indic-TTS repo (ICASSP 2023), Indic Parler-TTS HF card, AI4Bharat ASR roadmap page ("8 kHz telephony" as future work)
4. Gnani.ai — Prisma v2.5 / Timbre v2.5 product & FAQ pages, homepage claims; CallMissed model listings (Gnani ₹27/hr, Saaras ₹30/hr, Sarvam-M ₹35/M) [reseller pass-through]
5. Deepgram — Nova-3 APAC expansion (2026-05-14), Telugu product page, Models & Languages docs
6. Sarvam-M/Sarvam-30B — CallMissed model dossier (training-mix & Indic Vibe Check figures), Artificial Analysis Sarvam-M pages (intelligence rank, deprecation notice)
7. Groq — CloudZero pricing table (2026-05-04), MarkAICode Groq benchmark/deprecation report (2026-07-12), Tickerr/aipricing.guru tables (Aug 2026)
8. llm-stats.com DeepSeek-V3 vs Gemma-3-27B (pricing/benchmarks); Data-Dynamics OSS LLM comparison (2026-04-16)
9. IndicTrans2 — AI4Bharat blog (M2M/distilled latency), GitHub issue #31 (hosted-demo vs local latency)
10. Spheron — self-host voice-cloning guide (XTTS-2/F5/OpenVoice, GPU economics, 2026-05-31); India GPU-cloud pricing survey (ecorpit.com, 2026); E2E Networks GPU pricing pages; Spheron India-provider guide (2026-05-23)
11. Forasoft voice-cloning build-vs-license guide (2026-08-02) — license traps, MOS landscape; Codesota OSS TTS registry (2026-03-28); gigagpu TTS rankings (2026-04)
12. InVideo Bulbul v3 explainer (2026-08-07) — pricing, no-self-serve-cloning confirmation; Economic Times Bulbul v3 launch (2026-02)
13. Cartesia — Telugu TTS page, all-languages page; PkgPulse TTS API comparison (2026-03-09)
14. ElevenLabs — pricing page (Business "$0.05/min" line), aiofm cloning guide (2026-05-05)
15. Vapi docs (voice pipeline, voice-fallback-plan), Smallest×Vapi integration page, Retell docs/homepage
16. sunlo-core repo — IndicTrans2-CT2 ~40 ms/clause pipeline datapoint (single-source, hobby grade)

## 7. Known gaps / follow-ups for qa-eval-agent

1. **No independent Telugu WER on real 8 kHz recordings exists for Saaras v3 vs Nova-3-te vs Prisma v2.5** — build a 60-min annotated test set (mixed Telugu/Tenglish, mobile+landline) and score all three; this single experiment decides STT.
2. **Sarvam-M function-calling + field-extraction accuracy unmeasured** — run the domain-config harness (absent-student flow translated) before signing anything.
3. **Bulbul v3 Telugu MOS on OUR scripts** — blind-test 5 candidate voices with college-office staff; Sarvam's own docs warn voices vary by language.
4. **Confirm Sarvam STT list price** (₹30/hr vs ₹1.5/min discrepancy) and enterprise cloning terms/pricing in writing.
