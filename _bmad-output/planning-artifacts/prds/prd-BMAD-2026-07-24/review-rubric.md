# PRD Quality Review — BMAD Idea Launcher (prd-BMAD-2026-07-24)

## Overall verdict

For a 1-2 hour hobby build, this PRD is unusually disciplined: it names its own biggest risk (the local-vs-LLM generation assumption) as both an Open Question and a Non-Goal caveat, ships testable consequences with real numeric bounds, and defers scope honestly rather than smuggling it into "aside from optional." The only real gaps are downstream-usability nits (single UJ with a role-not-name protagonist, FR-4 numbered but never implemented) that matter little for a standalone, non-chained PRD. Nothing here blocks a build.

## Decision-readiness — strong

The PRD does not smooth over its central risk. §5.1's `[ASSUMPTION: idea generation is a local, templated/keyword-driven transform... If the intent was actually an LLM-backed generator, this FR and the "buildable in one session" framing both need revisiting.]` is a real fork, restated as Open Question 1 ("the single biggest fork in how this gets built") rather than resolved rhetorically. §6 Non-Goals explicitly says "if that assumption is wrong, this PRD is the wrong shape for the actual intent" — an honest admission most PRDs would bury. SM-C1 names a real trade-off (idea sophistication given up for build-time safety) rather than declaring everything important.

### Findings
None — this dimension has no material gaps.

## Substance over theater — strong

Vision (§2) is specific to this product, not swappable: it names the exact interaction ("type a problem... click Generate ideas, get three idea cards"), and explicitly distinguishes itself from "idea-management" tools rather than reciting generic ambition. Only one UJ and no persona roster, so no persona theater. The one Feature-specific NFR ("distinguishable without color alone") is concrete and product-specific, not scalability/security boilerplate.

### Findings
None.

## Strategic coherence — strong

Thesis is stated plainly in §2: "the 'product' is the interaction loop, not the sophistication of the ideas themselves." Scope choices (§7) and the counter-metric SM-C1 both follow from that thesis rather than from ease of implementation. MVP scope kind is problem-solving/experience-hybrid and the scope logic (defer everything not load-bearing to the core loop) matches it consistently.

### Findings
None.

## Done-ness clarity — strong

FR-1 through FR-3 each carry testable, bounded consequences: "under 5 seconds" (FR-1), "1440px-class desktop... 375px-class mobile... without horizontal scrolling" (FR-2), "does not change the Favorite state of the other two" (FR-3). No stray "reasonable performance" or "user-friendly" language anywhere in the FR text.

### Findings
- **low** Empty-prompt behavior underspecified (§5.1, FR-1) — "a lightweight visual cue (e.g. input outline) rather than silently doing nothing" names the failure mode to avoid but leaves the exact cue as an example, not a requirement. *Fix:* fine to leave as an implementer's choice given the project's scale, but worth an explicit "MUST provide some non-silent cue" framing if this PRD is meant to be handed off rather than self-built.

## Scope honesty — strong

§6 Non-Goals and §7.2 Out of Scope are unusually explicit for the size of this project — the PRD even calls out that it's resolving an ambiguity Voss's brief review flagged ("nothing said which of the four would actually ship"). All four brief "optional enhancements" are individually named and reasoned about rather than lumped into a vague "future work." The Assumptions Index (§10) round-trips cleanly against the two inline `[ASSUMPTION]` tags (§5.1, §5.2/FR-3). Open-items density (2 Open Questions, 2 assumptions, 0 `[NOTE FOR PM]`) is appropriately light for a solo learning-project PRD, not a blocker-level pile-up.

### Findings
None.

## Downstream usability — adequate

This is a standalone PRD by its own framing (§1: "written for whoever picks this up next — most likely the builder themself"), so this dimension matters less per the rubric, but two small items would trip up a story-creation pass if one happened:

### Findings
- **low** FR-4 is numbered and cross-referenced (§5.2, §7.2, §10) but never implemented in MVP — it exists only as a deferred placeholder. This is intentional and reads fine standalone, but a downstream story-generation pass scanning "FR-1 through FR-N" could mistake FR-4 for an MVP requirement if it doesn't read §7.2 closely. *Fix:* a one-line "(v1.1, not MVP)" tag next to the FR-4 heading itself, not just in the surrounding prose, would make this unambiguous on a skim.
- **low** Only one UJ (UJ-1) and its protagonist is a role ("A BMAD learner"), not a named individual carrying context across the journey. Fine for a single-screen hobby app with one user type, but if this PRD ever feeds a UX pass with multiple named personas elsewhere, the naming convention would need to align.

## Shape fit — strong

The PRD correctly reads itself as hobby/solo (§2: "Everything about this PRD is sized to a 1-2 hour build") and calibrates accordingly: one UJ instead of a persona roster, capability-oriented FRs, no fabricated multi-stakeholder framing. It resists over-formalization (no NFR section padded with generic scalability/security language) while still holding a real substance bar (testable consequences, honest scope, a named risk). This is the right shape for what it is.

### Findings
None.

## Mechanical notes

- Glossary (§4) terms — Prompt, Idea Card, Favorite, Session — are used with consistent capitalization throughout §5-§10; no drift observed (e.g. "Favorite" is never lowercased as a common noun where it means the domain term, and "cards" only appears informally in prose, not in FR consequence text).
- FR IDs (FR-1, FR-2, FR-3, FR-4) are contiguous and each cross-reference resolves (FR-4 in §7.2 correctly points back from §5.2/FR-3's persistence caveat).
- UJ-1 is the only UJ and is referenced consistently ("Realizes UJ-1") across FR-1, FR-2, and FR-3's feature description — no floating or orphaned UJ references.
- Assumptions Index (§10) roundtrips cleanly: both inline `[ASSUMPTION]` tags (§5.1, §5.2) have matching index entries, and no index entry lacks an inline counterpart.
- Required sections for this stakes level (Vision, Target User, Glossary, Features/FRs, Non-Goals, MVP Scope, Success Metrics, Open Questions, Assumptions Index) are all present; no missing section for a hobby-scale, standalone PRD.
