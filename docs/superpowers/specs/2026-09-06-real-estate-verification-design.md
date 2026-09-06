# Real-Estate Verification + Quotation-Callback Agent — Design

**Date:** 2026-09-06 (IST)
**Status:** Approved (design approval given during brainstorming; build starts after implementation-plan approval)
**Scope:** Config-only agent (Approach A). No code changes unless the verification gate exposes a platform gap. No pricing engine, no quote documents, no triggers (Beta V2).

---

## 1. Context

P1 proved agents are config, not code, and shipped a `real-estate-lead-qualification` starter preset. Live testing showed two gaps this design closes: (a) extraction that does not stick (values heard but never recorded, including a pseudo-`<tool_call>` loss since fixed in the text path), and (b) prompts that do not verify before recording. This agent makes verification + quotation-callback commitment its full pipeline, with a confirm-loop discipline that fixes (a) and (b) by construction.

Out of scope: live price quotes on the call, quotation documents/links, website/form triggers, Telugu.

## 2. Decisions (approved during brainstorming)

| # | Decision | Rationale |
|---|---|---|
| D1 | Quotation = collect + callback | No pricing engine, no document integration; agent gathers requirements and commits to a specialist callback |
| D2 | Full pipeline: enquiry authenticity + requirement details + callback commitment | Verifies the lead is genuine before spending a callback on them |
| D3 | Confirm loop, not lowered thresholds | Repeat-back + explicit confirmation makes values stick; thresholds stay 0.8 required / 0.7 optional |
| D4 | Config-only (Approach A) | Preset + agent version; approaches B (callback tool) and C (RE persona scripts) are fast follows on evidence only |

## 3. Agent definition

**Role.** Verification + qualification agent for `[Company Name]`, a real-estate brokerage. Calls people who recently enquired about a property (website form, listing, referral). Confirms the enquiry is genuine, collects the requirement, and commits to a concrete quotation-callback slot. Never quotes prices, offers, or possession dates — the human specialist delivers the quotation on callback.

**Question flow (one per turn, each confirmed before moving on).**

1. Opener/consent + enquiry confirmation: "Did you recently enquire about a property with `[Company Name]`?" If no → apologise, end politely, `invalid_lead`.
2. Interest check: "Are you still looking to buy?"
3. Requirement, one item per turn: property type → budget band → preferred locality.
4. Possession timeline: "By when are you hoping to take possession?"
5. Quotation callback: propose a slot ("Our specialist can call you back with a detailed quotation — would tomorrow at 11 AM work?"), negotiate if needed, confirm the EXACT day/time, read it back once more.
6. Wrap-up: thank them, restate the commitment ("We will call you back on {slot} with your quotation"), end. If the caller asks for a site visit instead, note `visit_date_preference` and wrap up the same way.

**System prompt.** The preset's `system_prompt` carries: role/objective/persona as above; the confirm-loop rules from §4 verbatim; objection handling (never enquired → apologise + end + `invalid_lead`; busy → ask better time, note it, end; "how did you get my number" → "you shared it in the enquiry"); answering rules (basic property facts only from `company_context`, never quote unverified numbers, specialist confirms the rest); hard stops (not interested → thank + end; abuse/opt-out → end + flag).

## 4. Confirm-loop discipline (the extraction fix)

1. Ask ONE thing per turn.
2. When the caller answers a requirement question, repeat the value back ("Just to confirm, your budget is around 80 lakhs, correct?") and call `record_extracted_field` ONLY after explicit confirmation (`yes/correct/right`).
3. On correction: update the value (upsert), repeat back again, re-confirm.
4. Spellings of names/localities: ask to spell out, never guess.
5. Unconfirmed values are NEVER recorded — ask again or mark unfilled (FR-12).
6. Callback slot: propose → negotiate → confirm exact day/time → read back once more → record `quotation_callback_slot` + `call_outcome=qualified_callback`.
7. When all required fields are confirmed (or the caller stops/refuses), `end_call` with a factual summary including unfilled required fields.

## 5. Extraction schema

| Field | Type | Required | Threshold | Notes |
|---|---|---|---|---|
| `enquiry_confirmed` | boolean | yes | 0.8 | Caller confirms they made the enquiry |
| `still_interested` | boolean | yes | 0.8 | Interest still current |
| `property_type` | string | yes | 0.7 | e.g. 2BHK apartment, plot, villa — caller's words |
| `budget_band` | string | yes | 0.8 | Exact band as stated, confirmed |
| `locality_preference` | string | yes | 0.8 | Confirmed, spelled out if needed |
| `possession_timeline` | string | no | 0.7 | When they hope to take possession |
| `quotation_callback_slot` | string | when callback | 0.8 | EXACT agreed day/time for the quotation callback |
| `visit_date_preference` | string | no | 0.7 | Only if caller asks for a site visit |
| `call_outcome` | string | yes | 0.8 | `qualified_callback`, `qualified_visit`, `not_interested`, `invalid_lead` |
| `escalation_needed` | boolean | no | 0.9 | Abuse, legal question, contradiction |

**Callback handoff.** `quotation_callback_slot` + `call_outcome` + all requirement fields surface on Call Detail, per-call export, campaign export, and the human-review flag when escalated. The team sees who to call back, when, and with what budget. No automation beyond that.

## 6. Verification gate (must pass before web-call testing)

Text dry-run on 3–5 sample real-estate leads across all five personas:
- Cooperative/terse: every required field captured, each confirmed in-transcript before recording.
- Refuses/clueless: clean wind-down, `not_interested`/`invalid_lead`, zero fabricated values.
- Zero verbatim `[...]` tokens in any transcript; zero raw `<tool_call>` markup persisted.
- Known limit (accepted): persona scripts answer with absentee-flavored lines, so the gate validates loop mechanics + extraction discipline, not domain content realism. Content realism via user roleplay; Approach C (RE persona scripts) only if this limit blocks sign-off.

## 7. Acceptance criteria

1. New preset version builds a working agent version from the builder with zero code changes.
2. Dry-run gate §6 passes on sample RE leads.
3. The user's live roleplay (text mode): enquiry → requirements → slot commitment all confirmed + recorded, callback slot read back verbatim.
4. P2 exit gates remain untouched; no P2 work starts.

## 8. Non-goals / later

- Live price computation or quotation figures on the call (would need a rate-card tool + data).
- Quotation documents, links, WhatsApp/email sending.
- Website/form-submit triggers, Telugu (Beta V2).
- Approach B (dedicated callback tool) and C (RE persona scripts): only on evidence.
