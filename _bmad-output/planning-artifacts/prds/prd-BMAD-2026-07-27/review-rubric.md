---
title: PRD Quality Review — BMAD Idea Launcher
prd_version: 1
date: 2026-07-27
---

# PRD Quality Review — BMAD Idea Launcher

## Overall verdict

This PRD holds up well for its stated stakes: a single-session hobby build with an honest, narrow MVP, real trade-offs surfaced (SM-C1, §9.2), and clean FR-to-consequence traceability. The one substantive defect is a self-contradictory Glossary entry for "Favorite" that conflicts with the FR-4 assumption and cites the wrong FR — a small fix, but the kind of thing that would confuse a builder mid-implementation. Everything else is calibrated correctly for a 1-2 hour learning exercise: light on formal UJ protagonists, appropriately terse on NFRs, and honest about deferrals.

## Decision-readiness — adequate

Trade-offs are named rather than smoothed over. SM-C1 (§8) explicitly forbids caching/reusing responses to game the SM-1 latency metric, and states why ("the point is real responsiveness... not the appearance of speed") — a real counter-metric doing real work, not boilerplate. §9.2 is the strongest example: it surfaces that the brief's "no backend API integration" non-goal was deliberately overridden, and rather than papering over it, leaves genuinely open "whether that addition still fits inside the brief's 1-2 hour build target," with a `[NOTE FOR PM]` flagging it as worth checking before the build starts. That is an objection acknowledged, not dodged.

### Findings
- **low** Open Question phrased as answered-then-reopened (§9, item 2) — The first half of Q2 reads as resolved ("deliberately overridden... confirmed... not a silent scope creep") before the actual open question (time-budget fit) appears in the second sentence. Not rhetorical in the rubric's bad sense (there's a real unresolved question), but the framing buries the lede. *Fix:* lead with the open question, then explain the resolved part as context.

## Substance over theater — strong

No findings — no persona bloat (2 UJs, both tied directly to FR realization), the Vision statement is specific to this product's shape (three cards, one screen, "stops" on purpose) rather than swappable boilerplate, and the FR-2 NFR ("must not expose the LLM API key to client-side code") is a concrete, product-specific bar rather than a generic "must be secure."

## Strategic coherence — strong

The thesis — "shipping a complete, small thing on purpose is the differentiator" (§2) — is stated once and then actually drives scope: every in-scope item in §7.1 serves the single prompt-to-three-cards flow, and everything else (categories, workflow helper, export) is explicitly deferred in the same breath the Vision raises it. SM-1 (speed) and SM-2 (session completion + real use) both validate the thesis directly rather than measuring generic activity, and SM-C1 guards against a metric being gamed in a way that would undercut the thesis.

## Done-ness clarity — adequate

Each FR (FR-1 through FR-4) carries testable consequences with concrete thresholds (280-character minimum, 30-second render target, exactly three cards). Two adjective-only spots remain unbound:

### Findings
- **medium** "Clearly highlighted visual state" left unbound (§5.2, FR-4) — No color, contrast, or state-persistence spec; "clearly highlighted" is exactly the kind of adjective the rubric flags. Low-stakes for a 1-2 hour build, but an implementer still has to invent the bound themselves. *Fix:* either accept it's intentionally left to implementer discretion (say so) or give a one-line bound (e.g., "visually distinct border/background, not solely color-based").
- **low** "Lightweight inline cue" undefined (§5.1, FR-2 consequence) — Similar looseness for the empty-prompt case; acceptable given the `[ASSUMPTION]` tag already flags it as unspecified by the brief, but worth a one-line concretization (e.g., "field border color change + short text") if the builder wants zero ambiguity during the build.

## Scope honesty — strong

§6 Non-Goals and §7.2 Out of Scope do real work and don't just restate the obvious; four `[ASSUMPTION]` tags are all indexed in §11 with no orphans; two `[NOTE FOR PM]` callouts land at genuine tensions (§7.2 cost-control risk if usage grows beyond the builder's own testing; §9.2 time-budget risk). Open-items density (4 open questions + 4 assumptions + 2 notes) is high in absolute terms but appropriate for a hobby/solo, low-stakes build per the rubric's own guidance — not a blocker here.

## Downstream usability — strong

Glossary terms (Prompt, Idea Card, Favorite, Idea Generation Service) are used consistently and capitalized consistently across FRs and UJs, with one exception noted below. FR IDs (FR-1–FR-4), UJ IDs (UJ-1, UJ-2), and SM IDs (SM-1, SM-2, SM-C1) are contiguous and cross-referenced correctly ("Realizes UJ-1, UJ-2," "Validates FR-2"). §10 gives each downstream BMAD skill a concrete anchor back into this PRD rather than a generic "this feeds architecture" statement.

### Findings
- **high** Glossary "Favorite" entry contradicts and mis-cites FR-4 (§4) — The Glossary defines Favorite as "a per-card toggle marking one idea card as selected; **at most implied to be multi-select** unless stated otherwise (see FR-3)." This directly conflicts with §5.2 FR-4's own consequence and the §11 Assumptions Index entry, both of which state single-select is the inferred behavior ("only one card can be favorited at a time"). The Glossary entry also cites **FR-3** (view cards), when the favoriting mechanic is defined in **FR-4**. A builder reading only the Glossary would come away with the opposite behavior from what FR-4 specifies. *Fix:* rewrite the Glossary entry to match FR-4 exactly (single-select, one active Favorite at a time) and correct the cross-reference to FR-4.

## Shape fit — strong

Correctly calibrated for hobby/solo, single-session stakes: two role-based UJs (not over-built with a personas roster), NFRs kept to the one that actually matters (API key never reaching the client), and success metrics that include the builder's own completion of the build (SM-2) rather than forcing an inapplicable DAU/MAU-style framing onto a one-user tool. No over-formalization detected.

## Mechanical notes

- **Glossary drift**: §7.1's MVP Scope bullet uses lowercase "favorite toggle" where the Glossary term is capitalized "Favorite" — minor, but the same document is inconsistent about whether this is a defined term or a common noun in that one spot.
- **The Glossary/FR-4 contradiction above** (see Downstream usability finding) is also a broken-reference issue: §4 points to FR-3 for behavior that's actually specified in FR-4.
- **ID continuity**: FR-1 through FR-4, UJ-1/UJ-2, SM-1/SM-2/SM-C1 are all contiguous with no gaps or duplicates.
- **Assumptions Index roundtrip**: all four inline `[ASSUMPTION]` tags (Glossary/Idea Generation Service, FR-2 empty-prompt, FR-2 NFR/API key, FR-4/single-select) are indexed in §11, and no §11 entry lacks an inline counterpart. Roundtrip is clean.
- **UJ protagonist naming**: UJ-1 and UJ-2 use role labels ("a BMAD learner," "a developer") rather than named individuals. Given the single-user, single-session shape, this is acceptable, but it's worth flagging as a deliberate light-touch choice rather than an oversight.
- **Redundancy**: §6 Non-Goals and §7.2 Out of Scope for MVP overlap substantially (idea management, multi-user/auth both appear in each). Not incorrect, just duplicated — low-cost to leave as is for a short PRD.
