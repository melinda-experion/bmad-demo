# Reconciliation: PRD vs Brief

**Input brief:** `_bmad-output/planning-artifacts/briefs/brief-BMAD-2026-07-30/brief.md`
**Document checked:** `_bmad-output/planning-artifacts/prds/prd-BMAD-2026-07-30/prd.md`

## Scope check

FR-1 (LLM backend) and FR-2 (favoriting) both faithfully reflect the brief's underlying findings: the stub/no-retry-with-backoff facts for FR-2→FR-1, and the single-select/highlighted-state description plus "not implemented" verdict for FR-4→FR-2. No content mismatch found there. Out-of-scope items (PromptGateway, localStorage, other deferred/vision items) are correctly excluded and flagged as open questions rather than silently dropped.

## Gaps found

1. **Working-tree-vs-committed caveat dropped.** The brief explicitly hedges its entire audit — including the FR-2 "hardcoded stub" finding that FR-1 is built on — with `[ASSUMPTION: not cross-checked against the last commit — if these files have uncommitted local changes, this status reflects the working tree, not necessarily what's checked in.]`. The PRD's §3.1 FR-1 states "replacing today's hardcoded stub" as settled fact and the PRD's own Assumptions Index (§6) never mentions this caveat. Since FR-1's premise rests directly on that audit, silently dropping the hedge means an implementer could start work against a stub that may no longer exist in the committed code without ever being told to check.

2. **Absence-is-not-proof caveat dropped for favoriting.** The brief's Assumptions Index explicitly caveats every "Not implemented" verdict (including FR-4/favoriting) as evidence-of-absence rather than proof. The PRD's §1 states favoriting as "favoriting (never built)" and §2.1 as "never built" with no hedge, and §6 Assumptions Index doesn't carry the caveat forward for FR-2. This is partially mitigated by Open Question 3 (possible overlap with pre-existing architecture/epics/Stories 1.1–1.3), but that question is framed around document reconciliation, not re-stated as "the not-implemented verdict itself carries residual uncertainty."

3. **Brief's Open Question 1 loses its original framing.** The brief asks directly: "Is `1-1-real-llm-backed-idea-generation.md`'s in-progress status still accurate, or has it stalled/been superseded?" The PRD's Open Question 1 reuses the same story doc but only surfaces the provider/model-ID sub-detail from it; the higher-level question of whether the story's in-progress status is stale or superseded is not restated anywhere in the PRD (it's adjacent to, but not the same as, Open Question 3's reconciliation concern).

No structural/tone loss found beyond the above — SM-C1 counter-metric, the retry-with-backoff exclusion, and the session-only/no-localStorage decision are all carried forward faithfully with correct attribution.
