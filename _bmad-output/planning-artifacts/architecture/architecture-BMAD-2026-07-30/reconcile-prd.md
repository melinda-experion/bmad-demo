---
title: Reconciliation — ARCHITECTURE-SPINE.md vs prd.md
input: _bmad-output/planning-artifacts/prds/prd-BMAD-2026-07-30/prd.md
checked: _bmad-output/planning-artifacts/architecture/architecture-BMAD-2026-07-30/ARCHITECTURE-SPINE.md
created: 2026-07-30
---

# Reconciliation Findings

## Gap 1 — AD-4 invents an unstated toggle-off/deselect behavior, unflagged

FR-2's consequences say only that favoriting a second card un-favorites the previous one ("at most one favorited card at any time"). The PRD never specifies what happens when the user clicks the *already-favorited* card. AD-4 resolves this silently: "Clicking the currently-favorited card toggles it back to `null` (deselect)." This is a reasonable interpretation of the word "toggle" in FR-2's opening sentence, but it is new behavior not present in the PRD's testable consequences, and the spine states it as `[ADOPTED]` fact rather than flagging it as an `[ASSUMPTION]` the way AD-2 correctly does for the env-var name. A builder or reviewer reading only the PRD would not expect deselect-on-reclick.

## Gap 2 — AD-5 silently resolves Open Question 4 instead of carrying it forward

PRD Open Question 4 explicitly asks whether the 30s SM-1 target still holds once a real (non-stub) LLM call is in the path, or whether a looser target is needed — and leaves it unresolved. AD-5 does not carry that uncertainty forward: it binds FR-1 to "30s target per PRD SM-1" and hard-codes a server-side `AbortController` at 25s "under the PRD's 30s end-to-end target," presenting the budget as settled. Nothing in the spine's Deferred section notes that this timeout split is provisional pending Open Question 4's resolution, so downstream builders would implement a fixed 25s timeout that the PRD itself flagged as possibly wrong.

## Gap 3 — Open Question 3's specific reconciliation detail is flattened

The PRD's Open Question 3 is more specific than "provider/model TBD": it flags that the existing story doc (`1-1-real-llm-backed-idea-generation.md`) already assumes Anthropic Claude and an `IDEA_LLM_API_KEY` env var, and that a specific model ID "could not be reliably confirmed" in that doc — a concrete reconciliation risk if the spine's provider-agnostic AD-2 diverges from what a builder actually implements. The spine's Deferred entry only generically restates "LLM provider/model choice and the exact env-var name... Open Questions 1 and 3," dropping the specific pointer to the story doc's existing (possibly stale) assumption. Not fatal since Deferred does gesture at Open Question 3, but the concrete collision risk the PRD called out is lost.

## Non-gaps checked (faithful)

- AD-5/AD-6 error handling (exactly-3, no pad/truncate/fabricate, no caching, error+retry preserving typed prompt) matches FR-1's consequences precisely.
- AD-3/AD-4 favoriting core spec (single-select, resets on new generation, session-only, no localStorage) matches FR-2.
- Provider-agnostic decision, Open Question 1 reconciliation risk, and PromptGateway exclusion are all carried forward (spine's top `[NOTE]`, AD-2's `[ASSUMPTION]`, and the Deferred section).
- SM-1, SM-2, SM-C1 are all represented in AD-5/AD-6 and the accessibility convention row.
