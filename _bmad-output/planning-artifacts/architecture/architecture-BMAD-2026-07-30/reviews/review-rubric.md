# Rubric Review — ARCHITECTURE-SPINE.md (architecture-BMAD-2026-07-30)

**Verdict:** PASS WITH FINDINGS (spine is usable as-is; two items should be resolved or explicitly deferred with rationale before build starts)

**Scope note:** Per instructions, the deliberate duplication of the approved `architecture-BMAD-2026-07-29` spine is a known, accepted tradeoff and is not treated as a finding.

## Method

Read the spine, the driving PRD (`prd-BMAD-2026-07-30/prd.md`), and — despite the task's caveat about not having direct code access — this environment does have file access, so `server.js`, `public/app.js`, `public/index.html`, `test/story1.test.js`, and `package.json` were read directly to check the brownfield-ratification claim rather than judging it on plausibility alone.

## Findings

### 1. [Major] No test-strategy convention for the real LLM adapter — a real, undecided divergence point

AD-6 replaces the hardcoded stub with a genuine provider call. The existing `test/story1.test.js` drives this through the live HTTP handler end-to-end (`POST /api/ideas` against a real listening server). Once `lib/ideaService.js` makes a real outbound call, `node --test` will either hit the live provider on every run (cost, latency, flakiness, requires a live key in dev/CI) or needs some injection/mocking seam — and the spine specifies none. Two builders extending this could diverge: one stubs `fetch`/the provider module, one adds an env-gated fake-adapter path, one just lets tests hit the real API. AD-6 is exactly the seam (fixed adapter signature/export) that should have settled this, but it's silent on testability. This should be decided (e.g., "tests inject a fake adapter via X" ) or explicitly listed under Deferred with rationale.

### 2. [Moderate] The deferred provider/env-var-name choice is flagged as needing reconciliation, not safely deferrable

Per the checklist's "nothing under Deferred could let two units diverge": the spine's own Deferred section notes that an existing story doc (`1-1-real-llm-backed-idea-generation.md`) already assumes Anthropic Claude and `IDEA_LLM_API_KEY`. That's a stronger signal than an open design choice — it means a builder following AD-2 fresh could legitimately pick a different provider/env-var name than what other already-written artifacts assume, producing incompatible wiring (docs, `.env.example`, that story's tasks) rather than two harmlessly-different-but-compatible implementations. The spine correctly surfaces the tension in prose but still lists it under Deferred rather than either fixing the name or promoting it to a must-resolve-before-build item. This mirrors the PRD's own unresolved Open Question 3, so it isn't a spine-only gap, but the spine had the opportunity to close it and didn't.

### 3. [Minor] AD-3's "single client-side state object" is new structure, not ratified from existing code

Verified `public/app.js`: it currently has no consolidated state object — it reads/writes DOM elements directly (`promptInput.value`, `results.innerHTML`, etc.) with no `state.prompt`/`state.ideas`/`state.favoritedIndex`. AD-3's rule is a reasonable new design decision to support FR-2's favorite tracking, but the spine's ratification framing ("`[ADOPTED]` — ratified from the existing... code, matching the prior spine's paradigm exactly") applies to the Design Paradigm section's layering, not to AD-3's specific state-object shape. Worth being explicit that AD-3 introduces a refactor of `app.js`'s current imperative style rather than implying it already exists.

## Checklist pass/fail summary

- Fixes real divergence points for the level below: **mostly** — AD-1/2/4/5/6 are solid; AD-3's state-object requirement and the missing test-mocking convention (Finding 1) are the two gaps.
- Every AD's Rule is enforceable and prevents its divergence: **yes** for AD-1 through AD-6 as written.
- Nothing under Deferred could let two units diverge: **no** — see Finding 2.
- Named tech verified-current (Node.js ≥22, CommonJS, `node --test`): **consistent** with `package.json` (no `"type"` field → CommonJS default; `test` script is `node --test`); no `engines` pin exists to enforce ≥22, but that's a repo-hygiene gap, not a spine defect.
- Ratifies rather than contradicts the brownfield codebase: **yes for AD-1** (confirmed core `http`, no framework) and the overall layering; **partially** for AD-3 (see Finding 3 — not a contradiction, but not pre-existing either).
- Covers FR-1 and FR-2: **yes** — both bound explicitly, each with 2+ ADs addressing them.
- Every dimension the altitude owns is decided/deferred/open: **yes**, including the operational/environmental envelope, which is explicitly and correctly deferred (local-only, no ops/CI in scope) — no silent dimension found.

## Finding counts

- Major: 1
- Moderate: 1
- Minor: 1
