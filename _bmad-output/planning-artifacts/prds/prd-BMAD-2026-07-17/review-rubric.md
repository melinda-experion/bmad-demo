# PRD Quality Review — BMAD Idea Launcher (prd-BMAD-2026-07-17)

## Overall verdict

This PRD is well-calibrated to its stakes: a tiny, one-sitting build with no backend gets a lean capability spec rather than a bloated template-fill. The FRs are testable, the scope decisions (templated generation, no persistence beyond an optional localStorage favorite) are named and defended rather than smoothed over, and the Non-Goals/Assumptions/Open Questions machinery is used honestly rather than performatively. The main risks are mechanical, not structural: the Assumptions Index doesn't fully round-trip the inline `[ASSUMPTION]` tags, Glossary terms drift in capitalization/pluralization across sections, and the single UJ has no named protagonist. None of these threaten buildability; a developer could pick this up and start today.

## Decision-readiness — adequate

The PRD states real decisions rather than burying them: templated/local generation over a live LLM call is chosen and justified (§4.1), and the trade-off is explicit ("no backend, no API keys... buildable in a single front-end session" vs. giving up "real" idea quality, reinforced by counter-metric SM-C1). Open Questions (§8) are genuinely open — OQ2 (commit FR-7–9 now vs. stretch) and OQ3 (pull FR-5 into MVP) have no answer smuggled into the next sentence.

The gap is that the PRD never uses the `[NOTE FOR PM]` convention even though real tensions exist (e.g., the LLM-vs-template question is a product-direction call, not just a build-time one; the "Working title — confirm" note under the H1 is a live decision point with no owner or resolution path). These tensions are surfaced only as Open Questions or dangling prose, which works but is inconsistent with how the rest of the document tags uncertainty.

### Findings
- **low** Working title left unresolved outside the tracking machinery (title page, line 9) — "*Working title — confirm.*" is a real open decision but isn't in §8 Open Questions or §9 Assumptions Index, so it's easy to lose track of. *Fix:* add as OQ-4 or resolve before build.
- **low** No `[NOTE FOR PM]` callouts anywhere despite real tensions (LLM-vs-template direction, FR-5/7-9 optionality). Not a defect given Open Questions cover the same ground, but the PRD would be more internally consistent if it used one convention deliberately rather than leaving `[NOTE FOR PM]` completely unused.

## Substance over theater — strong

No persona theater — one persona is used and every JTBD line drives §4 scope (minimal generation, single-session state, no accounts). No differentiation/innovation section was forced in; the PRD doesn't claim novelty it doesn't have. The one NFR (§4.1 feature-specific NFR: "must complete fast enough to feel instant") is qualified with the actual reason (local/templated logic) and an explicit revisit condition if generation later becomes API-backed — this is the opposite of boilerplate NFR language. The Vision (§1) is specific to this artifact's pedagogical purpose and would not swap cleanly into another PRD.

## Strategic coherence — strong

The thesis is explicit: make the BMAD brief→PRD→UX→architecture→story→code arc tangible and finishable in 1-2 hours (§1). Feature selection follows from it — every in-scope FR (prompt input, 3-card generation, favoriting, one-screen layout) is load-bearing for UJ-1, and everything cut (persistence, auth, LLM backend, idea management) is cut because it would jeopardize the "finishable in one sitting" constraint, not because it was merely hard. SM-1 validates the brief's actual usability bar (30s to three cards); SM-2 validates the Vision itself (pedagogical completion) rather than a vanity activity metric. SM-C1 is a real counter-metric — it explicitly forbids optimizing idea quality at the expense of scope, which is the one place this PRD could have drifted into scope creep.

## Done-ness clarity — strong

Every FR (FR-1 through FR-6) carries testable consequences with concrete bounds: character sanity cap (500 chars, FR-1), exact card count and re-click behavior (FR-2), highlight-state independence per card (FR-4), concrete mobile/desktop widths (~375px / ~1280px+, FR-6). Vague adjectives are mostly avoided or immediately bounded — e.g. FR-3's "legible" is soft, but paired with concrete card-distinctness criteria, and is proportionate for a one-screen hobby app with no visual design spec expected.

### Findings
- **low** FR-3's "legible at both desktop and mobile widths" (line 90) has no bound (font size, contrast) the way FR-6 bounds its widths. Low severity given scope — but if a UX pass isn't run before build, this is the one place "done" is left to judgment. *Fix:* either accept as-is (reasonable for hobby scope) or add a one-line minimum (e.g., "readable without zooming at 375px").

## Scope honesty — strong

Non-Goals (§5) and Out-of-Scope subsections do real work — they name what's cut and why, not just gesture at it. `[ASSUMPTION]` tags are used at every point where the "basic/local generation" decision recurs (§4.1, FR-2, §5, §6.2, §8), and FR-5/FR-7–9 are explicitly marked optional with a note that they "should not block MVP completion" (line 144) — this is de-scoping done honestly rather than silently. Open-items density (3 Open Questions + 5 inline `[ASSUMPTION]` tags) is proportionate for a hobby-scope PRD that is not a green-light-to-build-without-review document — it reads as "still confirming a few things," not "riddled with unresolved gaps."

## Downstream usability — thin (matters less here, but still worth flagging)

This PRD explicitly feeds `bmad-ux`, `bmad-architecture`, and `bmad-create-story` (§0), so downstream usability isn't fully optional even at this scale. FR IDs are contiguous and unique (FR-1–FR-9), UJ-1 is the sole journey and clearly tagged, and most cross-references resolve ("see FR-6," "see FR-5"). But:

### Findings
- **medium** UJ-1 has no named protagonist — it opens "A BMAD learner opens the app..." (line 38) rather than a named individual carrying context inline, which the rubric flags as a downstream-usability risk even for single-UJ PRDs. Low-stakes here since there's only one UJ and one persona, but if `bmad-ux` expects a concrete user to design around, this is the one place it would have to invent one. *Fix:* name the learner (e.g., "Priya, a BMAD learner...") for UX/story continuity.
- **low** Glossary/body casing drift: Glossary (§3) defines "Idea Card" (capitalized, singular form used generically), but body text alternates between capitalized ("3 Idea Cards," FR-2) and lowercase ("three idea cards," §1 Vision and §7 SM-1) for the same term, and FR-3's own heading reads "Idea card display" (mixed case). Not confusing to a human reader but a downstream doc-extraction pass would see this as term drift.

## Shape fit — strong

This is correctly treated as a hobby/solo, single-operator capability spec: one persona, one UJ ("Lighter scope dial per template," line 36, explicitly acknowledged), no multi-stakeholder framing, no forced differentiation or competitive-landscape section. It is not over-formalized (no persona/UJ padding) and not under-formalized (the single UJ that exists is concrete and testable, not skipped entirely for a consumer-facing product). The addendum's placement of tech-stack detail (vanilla HTML/CSS/JS) outside the PRD body, deferred to architecture, is the right call and keeps the PRD from drifting into implementation theater.

## Mechanical notes

- **Assumptions Index roundtrip is incomplete.** Five inline `[ASSUMPTION]` tags exist (§4.1 FR-2 description; FR-2 Out-of-Scope line 73; §5 Non-Goals line 149; §6.2 line 169; §8 OQ1 line 182), but §9 Assumptions Index lists only two entries (mapped to §4.1 and §6.2). They're arguably the same underlying assumption restated five times, but a downstream reader scanning only §9 would miss that the assumption also gates FR-2's scope line and the Non-Goals section directly. *Fix:* either consolidate the inline tags to point at one canonical assumption entry, or add the missing locations to §9.
- **Glossary casing drift**: "Idea Card"/"idea card"/"idea cards" used inconsistently across §1, §4, §7 (see Downstream usability finding above).
- **ID continuity**: FR-1–FR-9 contiguous, no gaps or duplicates. UJ-1, SM-1/SM-2/SM-C1 all unique and referenced correctly (e.g., "Validates FR-2," "Realizes UJ-1"). No broken cross-refs found.
- **Working title unresolved** (line 9) — not itself a mechanical defect, but worth resolving before this PRD is treated as final, since the filename/title would otherwise propagate into UX and architecture docs.
