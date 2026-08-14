---
title: PRD Quality Review — Support Ticket Triage
prd_version: 1
date: 2026-08-14
---

# PRD Quality Review — Support Ticket Triage

## Overall verdict

This PRD is unusually self-aware for a Fast-path document — it names its own trade-offs (fail-open screening, no differentiation, thin persona) instead of laundering them into neutral language, and its Success Metrics correctly measure the governance chain rather than product-fiction vanity numbers. The main risk is downstream, not strategic: one Assumptions Index cross-reference points at the wrong item, roughly a third of the indexed assumptions have no inline `[ASSUMPTION]` tag at their source, and FR-3's stated "testable" consequence doesn't actually test FR-3's claim. None of these threaten the PRD's coherence, but they're exactly the kind of thing that trips up an architecture/stories pass that source-extracts mechanically.

## Decision-readiness — strong

The PRD states decisions as decisions rather than burying them as considerations. §1 resolves the brief's two-"Primary"-persona ambiguity explicitly ("This PRD does not treat that audience as a second product persona"). The FR-6 NFR names the fail-open trade-off plainly — "This is a v1 convenience trade-off, not a hardened security posture" — and SM-C2 pre-empts the obvious pushback: "Do not let PromptGateway's fail-open behavior (§5.2) go unmentioned in the demo narrative to make SM-1 look cleaner than it is." Open Questions are genuinely open, not rhetorical-with-answer — e.g. §9 Q5 explicitly declines to resolve the brief's generic Problem framing and states the fork ("does that framing need real specificity... or does 'illustrative by design' cover it") without smuggling in an answer. No findings.

## Substance over theater — strong

No persona theater: the single Triaging Agent persona is intentionally thin (Assumptions Index item 8) but every JTBD bullet in §3.1 maps to an FR. No innovation theater: the Vision (§2) states plainly "the product itself has no real differentiation." No NFR boilerplate: the NFRs under FR-3 and FR-6 are specific and sourced (2000-char cap, fail-open behavior tied to a named existing hook) rather than generic "must be scalable/secure" language. SM-5/SM-6 are lightweight (10-ticket sample, binary judgment) but the PRD is explicit about that limitation and guards it with counter-metrics (SM-C1) rather than dressing it up as rigor. No findings.

## Strategic coherence — strong

The thesis is stated directly: the product has no differentiation, so the PRD's value is that it "does one real thing" — PromptGateway screening with real failure modes (§2). Features 5.1 and 5.2 both serve that thesis (core loop, then the screening layer that makes the loop non-trivial). Success Metrics follow the thesis correctly: SM-1–SM-4 (Primary) measure the governance chain itself, not activity metrics, and SM-5/SM-6 (Secondary) are explicitly subordinated — §8's directive to story authors states this priority in so many words. Counter-metrics are present for both SM groups. No findings.

## Done-ness clarity — adequate

Most FRs carry consequences an engineer could turn directly into a test: FR-1's "exactly one triage LLM call," FR-4's "no Ticket Text reaches the triage LLM call without a prior PromptGateway screening attempt," FR-6's "zero triage LLM calls" are all unambiguous. Two gaps:

### Findings
- **medium** FR-3's testable consequence doesn't test FR-3's claim (§5.1, FR-3) — FR-3 states ambiguous Ticket Text "is categorized `other` rather than forced into the nearest fixed category," but the listed consequence is "No submission ever fails or errors solely because it doesn't fit the first four categories." An implementation that force-fits every ambiguous ticket into `bug` would still satisfy that consequence, since it wouldn't error. SM-5's 10-ticket sample partially covers this at the metrics level, but the FR itself has no consequence that would catch a broken fallback in isolation. *Fix:* add a consequence such as "Ticket Text that doesn't match any of bug/billing/feature-request/question deterministically returns `other`, verifiable against a held-out sample" — or explicitly point FR-3's Consequences at SM-5 the way SM-5 already points back at FR-3.
- **low** "Comparably short timeout" is an adjective, not a bound (`addendum.md`, "Fail-open implementation note") — the addendum exists specifically to hand architecture concrete technical direction, and does cite the hook's own 8–15s timeout as a reference point, but never commits Support Ticket Triage's own screening call to a number. *Fix:* either state the timeout value directly (e.g., "≤8s, matching the hook's own `--timeout 8`") or explicitly flag it as an open decision for architecture rather than implying it's already specified.

## Scope honesty — strong

§6 Non-Goals does real work — items like "Hardened PromptGateway failure handling (retries, fail-closed mode, circuit breaking) — v1 fails open only" and the latency-SLA non-goal are specific, not filler. The favorite/save-triage cut is de-scoped honestly rather than silently dropped: "Deferred, not rejected `[NOTE FOR PM]`... natural candidate for a second epic." `[ASSUMPTION]` tags are used at genuine inference points (category fallback, fail-open behavior, the 2000-char cap, SM-5/6 tightening) rather than scattered defensively. Given the PRD's own stated stakes (Internal, Fast-path, demo vehicle), the volume of Open Questions (7) and Assumptions (8) is appropriate, not a red flag — this matches the rubric's own guidance not to penalize a low-stakes PRD for surfacing what it doesn't know. No findings beyond the roundtrip mechanics noted below.

## Downstream usability — adequate

This is a chain-top PRD (§1: "for whoever builds the architecture, epics, and stories that follow it"), so cross-reference correctness matters more than it would for a standalone document. FR/UJ/SM numbering is contiguous with no gaps or duplicates, and most cross-references resolve correctly (UJ-1 → "Realizes FR-1 through FR-6" is accurate; SM-5/SM-6 → "Validates FR-2, FR-3" is accurate).

### Findings
- **medium** Broken Assumptions Index cross-reference (§1, Document Purpose) — the text reads "This PRD does not treat that audience as a second product persona — see Assumptions Index, item 2," but that claim matches **item 1** ("§1 — The demo audience is not treated as a second product persona..."). Item 2 is a different assumption entirely (§3.1's JTBD trust inference). A reader following this pointer lands on the wrong entry. *Fix:* change "item 2" to "item 1."
- **low** Glossary terms defined but not reused verbatim (§4 vs. body) — `Screening Decision` is defined ("PromptGateway's verdict... `ALLOW`, `FLAG`, or `BLOCK`") but FR-4/5/6 refer to it only as a generic lowercase "decision," never the capitalized glossary term. Similarly, `Triaging Agent` is the formal glossary term and appears in FR-1's text ("A Triaging Agent can submit..."), but §3.1's JTBD bullets and UJ-1's narrative consistently say "a support agent" instead. Neither drift is confusing in context, but it means the two sections most likely to be lifted independently (FR block vs. UJ/JTBD block) use different vocabulary for the same entities. *Fix:* pick one term per concept and use it in both the formal FR language and the narrative UJ/JTBD language.

## Shape fit — strong

The PRD correctly identifies its own shape: "Single-operator-role internal tool — lightweight shape per PRD scope dial" (§3.3), and follows through — exactly one UJ, no UJ-density padding, and Success Metrics that are explicitly operational (governance-chain checks) rather than forced into user-facing engagement language. The brownfield-style precedent references check out against the actual repo: `.claude/hooks/prompt_gateway_check.py`'s real BLOCK/FLAG/ALLOW branching and its `--timeout 8` / `timeout=15` subprocess guard match the addendum's description exactly, and `server.js`'s `MAX_PROMPT_LENGTH = 2000` (committed at `8e9bc31`) matches the 2000-character cap cited in FR-6 and the addendum. No findings.

## Mechanical notes

- **Assumptions Index roundtrip is partial.** Of the 8 indexed items, only items 3–7 (FR-3 category fallback, FR-3's no-SLA NFR, FR-6's fail-open NFR, FR-6's 2000-char cap, and SM-5/SM-6's tightening) have a corresponding inline `` `[ASSUMPTION]` `` tag at their source location in the body. Items 1, 2, and 8 — the persona-scoping decision (§1), the JTBD trust inference (§3.1), and the intentionally-thin persona (§3.1) — are real, defensible assumptions but appear in the body as plain prose with no inline tag. A reader scanning the document body for `` `[ASSUMPTION]` `` markers (rather than reading the index top-to-bottom) would miss three of the eight.
- **Broken cross-reference:** §1 → "Assumptions Index, item 2" should read "item 1" (see Downstream usability finding above).
- **Glossary drift:** `Screening Decision` and `Triaging Agent` defined in §4 but not consistently reused verbatim in FR vs. UJ/JTBD text (see Downstream usability finding above).
- **UJ protagonist naming:** fine as-is — UJ-1's "a support agent, mid queue" is consistent with the intentionally thin, unnamed persona (Assumptions Index item 8) and doesn't read as a floating UJ.
- **Required sections for stakes:** all present and appropriately scaled for an Internal/Fast-path PRD — Vision, Target User (JTBD + Non-Users + UJ), Glossary, Features/FRs with per-FR Consequences, Non-Goals, MVP Scope, Success Metrics with counter-metrics, Open Questions, Assumptions Index.
