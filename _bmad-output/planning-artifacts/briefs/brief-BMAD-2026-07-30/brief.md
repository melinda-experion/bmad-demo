---
title: BMAD Idea Launcher — Implementation Status Brief
approval_status: approved
created: 2026-07-30
updated: 2026-07-30
confidence: 90
confidence_label: High
confidence_rationale: Nearly every claim is traced directly to code inspection (server.js, public/app.js, public/index.html) rather than inference. Voss's adversarial review (review-report.md) surfaced 4 moderate findings, all resolved in this revision by adding audit criteria, a working-tree caveat, and an absence-is-not-proof caveat to the Assumptions Index, plus softening two recommendation-leaning spots into diagnostic questions.
version: 1
---

# Product Brief: BMAD Idea Launcher — Implementation Status

## Purpose

This is a status/gap brief, not a forward vision document. It exists because a v2 scoping conversation was starting to assume prior work — favoriting, the LLM backend, the deferred/vision items — without anyone having checked what of v1's promise actually shipped; scoping v2 on unverified assumptions about v1 risks re-planning work that's already done, or missing work that was never finished. It answers one question against the approved v1 brief and PRD (`brief-BMAD-2026-07-27`, `prd-BMAD-2026-07-27`): **of what v1 promised, what has been built?** It commits to no new scope — it is the factual base a future v2 scoping decision would start from.

**Audit criteria:** "Implemented" means direct positive evidence was found in the audited files (specific markup, handler, or call). "Not implemented" means the expected pattern was absent from those files — evidence of absence, not proof of absence (see Assumptions Index). This document is considered complete for its stated purpose once every v1 FR, deferred item, and vision item has one of these two verdicts with cited evidence; it does not require resolving the Open Questions below, which are follow-on decisions for whoever scopes v2.

## Summary

Of the four core FRs, two are fully implemented (FR-1, FR-3), one is partially implemented with the LLM call stubbed (FR-2, with an in-progress story tracking the fix), and one is entirely missing (FR-4, favoriting). One of four deferred items shipped (`Clear` button); the other three did not. None of the three v2 vision items exist yet, and one (export) is structurally blocked until favoriting is built. The PromptGateway service exists on this branch but isn't connected to the idea-generation path.

## What v1 Promised

Per the approved brief/PRD (`brief-BMAD-2026-07-27`, `prd-BMAD-2026-07-27`): a single-screen app with prompt input, three generated idea cards, single-select favoriting, a short "if time allows" deferred list, and a longer-term vision explicitly not committed for v1. Status of each is below.

## Current Implementation Status

Audited directly against the working-tree contents of `server.js`, `public/index.html`, `public/app.js`, `public/styles.css` on `feature/prompt-gateway` as of 2026-07-30. `[ASSUMPTION: not cross-checked against the last commit — if these files have uncommitted local changes, this status reflects the working tree, not necessarily what's checked in.]`

### Core FRs (v1 §5)

| Item | Status | Evidence |
|---|---|---|
| FR-1: Prompt input with placeholder | **Implemented** | `public/index.html` — textarea with the specified placeholder text |
| FR-2: `Generate ideas` → Idea Generation Service → 3 ideas, empty-prompt validation, error handling | **Partial** | Button, fetch call, empty-prompt validation, and a generic error message all wired (`public/app.js`). But the server side is a **hardcoded stub** (`server.js`) — three template-string ideas built from the prompt text, not an LLM call. `[ASSUMPTION: the in-progress story doc at _bmad-output/implementation-artifacts/1-1-real-llm-backed-idea-generation.md, with all tasks unchecked and a target file lib/ideaService.js that doesn't exist yet, is the tracked plan to close this gap — treating it as authoritative rather than stale.]` No retry-with-backoff exists (out of scope per v1, so this is expected, not a gap). |
| FR-3: Exactly 3 idea cards (title + description) | **Implemented** | `public/app.js` renders cards from the response; styled in `public/styles.css` |
| FR-4: Favorite toggle, single-select, highlighted state | **Not implemented** | No favorite markup, click handler, or highlighted-state CSS anywhere in the app code |

### Deferred items (v1 §7.2, "if time allows")

| Item | Status | Evidence |
|---|---|---|
| Save favorite in `localStorage` | **Not implemented** | No `localStorage` usage in app code (also blocked by FR-4 not existing) |
| `Clear` button | **Implemented** | Present in `index.html`, resets prompt/results/status/error in `app.js` |
| "How it works" note | **Not implemented** | No such element in `index.html` |
| "Next step" hint → `bmad-ux` | **Not implemented** | No such element in `index.html` or `app.js` |

### Vision items (v1 §2, explicitly not committed for v1)

| Item | Status | Evidence |
|---|---|---|
| Guided idea categories aligned to BMAD phases | **Not implemented** | No category concept anywhere in server response or UI |
| Tiny workflow helper surfacing next BMAD step | **Not implemented** | Same gap as the "Next step" hint above |
| Export favorited idea into a brief/story | **Not implemented** | No export code; also structurally blocked until FR-4 (favoriting) exists |

## Branch Context: PromptGateway

The current branch (`feature/prompt-gateway`, commit `be00e36`) added a standalone PromptGateway service (`PromptGateway/app.py`, `policy.yaml`) plus Claude Code dev tooling (`.claude/skills/prompt-gateway-guard/`, `.claude/hooks/prompt_gateway_check.py`). This is **not wired into the running app** — grep of `server.js`/`public/app.js` for "gateway" returns no matches. The Idea Generation Service (stub today, planned `lib/ideaService.js`) does not route prompts through PromptGateway for a policy check. Both pieces exist on this branch but aren't connected to each other.

## Open Questions

1. Is `1-1-real-llm-backed-idea-generation.md`'s in-progress status still accurate, or has it stalled/been superseded?
2. Does export's dependency on FR-4 (favoriting) change how a v2 scoping pass would sequence these two items? (Diagnostic fact: export cannot exist before favoriting does — this doesn't resolve which order or whether either gets built.)
3. Is there a reason the real LLM-backed Idea Generation Service and PromptGateway aren't connected — deliberate sequencing, or simply not yet done?

## Assumptions Index

- Treated the in-progress story doc for real LLM-backed generation as the authoritative, still-current plan for closing the FR-2 gap, rather than assuming it's stale.
- Audited the working-tree state of the app files, not explicitly verified against the last commit — see the caveat in "Current Implementation Status."
- Every "Not implemented" verdict rests on the absence of an expected pattern (grep for terms like "favorite", "localStorage", "gateway") in the audited files — this is evidence of absence, not proof; a differently-named implementation, a build step not inspected, or unreferenced dead code wouldn't be caught. "Implemented" verdicts rest on direct positive evidence and don't carry this caveat.
