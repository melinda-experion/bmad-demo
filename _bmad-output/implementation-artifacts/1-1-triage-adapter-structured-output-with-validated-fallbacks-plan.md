---
story: 1.1 — Triage Adapter — Structured Output With Validated Fallbacks
date: 2026-08-14
status: approved
confidence: 76
confidence_label: Medium
confidence_rationale: All 5 ACs, the AD-4 validation contract, and the AD-5 failure-class shape are directly confirmed by the approved architecture spine and story ACs, not inferred. Docked from High because two load-bearing details are this plan's own new assumptions rather than confirmed input — the triage LLM provider/model (Claude Haiku 4.5) and the call timeout value (18s) were both explicitly Deferred by the architecture and are being decided here, in this plan, for the first time.
---

# Implementation Plan: Story 1.1 — Triage Adapter

## Scope Summary

Build `lib/triageService.js`: a single adapter module that takes raw ticket text, calls the triage LLM (Claude Haiku 4.5 via `@anthropic-ai/sdk`), and returns a validated `{category, priority, summary, draftReply}` result — or a typed failure — per AD-4's two-gate validation contract. No HTTP layer, no PromptGateway integration, no UI — those are Stories 1.2/1.3. Scope is exactly: `lib/triageService.js`, its test file, and the new `@anthropic-ai/sdk` dependency.

## Impacted Modules & Files

- **New:** `lib/triageService.js` — the adapter, exports `triageTicket(ticketText)` (CommonJS, matching this repo's actual `package.json` — no `"type": "module"`).
- **New:** `test/triageService.test.js` — `node --test` suite, mocks `global.fetch`.
- **No new dependency.** Superseded from the original SDK-based design after checking `project-context.md`'s Technology Stack line ("No npm dependencies beyond husky") and the prior demo app's own `lib/ideaService.js` precedent (git history, commit `8e9bc31`) — raw `fetch` straight to the Anthropic Messages API, no SDK. `package.json`/`package-lock.json` are unchanged.

## Detailed Design Approach

`triageTicket(ticketText)` is an async function with three internal stages, matching AD-4's exact ordering:

1. **Call the LLM.** Raw `fetch` to `https://api.anthropic.com/v1/messages` (mirrors `lib/ideaService.js`'s prior-app pattern exactly — no SDK). Headers: `x-api-key` from `process.env.ANTHROPIC_API_KEY`, `anthropic-version`, `content-type`. Model is the hardcoded constant `claude-haiku-4-5` (this story's explicit decision, not a runtime knob). Prompt instructs the model to classify `ticketText` and respond with ONLY a JSON object containing `category`/`priority`/`summary`/`draftReply` string fields (same "ONLY JSON, no markdown/commentary" instruction style as `ideaService.js`'s `buildPrompt`). An `AbortController` enforces an 18s timeout; an aborted call maps to a `TIMEOUT` failure, any other fetch rejection or a non-`ok` response maps to `NETWORK`.
2. **Structured-data gate (AD-4, Task 2).** Attempt `JSON.parse` on the model's text output (defense in depth even though `output_config.format` should already constrain this — the architecture requires the adapter enforce its own invariant, not trust the provider's guarantee). Check all four keys are present and each is a `string`. Any failure here (parse error, missing key, wrong type) → return a `MALFORMED` failure. No inline default at this stage.
3. **Enum validation (AD-4, Task 3).** Only runs after stage 2 passes. `category` checked against `['bug','billing','feature-request','question','other']` — if not a member, replaced with `'other'`. `priority` checked against `['low','medium','high']` — if not a member, replaced with `'medium'`. `summary`/`draftReply` pass through unmodified (AD-4 explicitly scopes out their content). Return `{category, priority, summary, draftReply}`.

Failure return shape (stage 1 or 2): `{ ok: false, failureClass: 'TIMEOUT' | 'NETWORK' | 'MALFORMED', message: string }` — chosen so Story 1.3 can map `failureClass` directly to AD-5's `TIMEOUT:504` / `NETWORK:502` / `MALFORMED:500` without re-deriving it. Success return shape: `{ ok: true, category, priority, summary, draftReply }`. A discriminated-union-by-`ok` shape (rather than throwing) is chosen because Task 2/3's test scenarios need to assert on structured failure data, and because a throw would force Story 1.3 to parse error messages to recover `failureClass` — a plain return keeps that mapping lossless.

## Data Model Usage

No database, no persistence (AD-6). The only "data model" is the in-memory result shape above, held for the duration of one request/test — nothing outlives the function call.

## API/Interface Changes

New module-level export only — no HTTP endpoint in this story (Story 1.3 adds `POST /api/submit-triage` and will import `triageTicket` from this module).

```js
// lib/triageService.js
export async function triageTicket(ticketText) { ... }
```

## Error Handling & Edge Cases

- Invalid JSON in model response → `MALFORMED`.
- Valid JSON, missing one of the 4 keys → `MALFORMED`.
- Valid JSON, a key present but wrong type (e.g. `priority: 3`) → `MALFORMED`.
- Valid JSON, all keys present and string-typed, `category`/`priority` value outside its enum → inline fallback (`other`/`medium`), not a failure.
- SDK throws (network error, non-timeout) → `NETWORK`.
- Call exceeds 18s → `TIMEOUT`.
- Empty-string `ticketText` — out of this story's scope; FR-1 makes that a client-side rejection in Story 1.3 before any request reaches an adapter. This adapter does not special-case it.

## Security Considerations

- `ANTHROPIC_API_KEY` read from `process.env` only — never hardcoded, never included in logs, error messages, or test fixtures (tests use a mocked client, never a real key).
- Raw `ticketText` is never logged — PromptGateway screening (Story 1.2) exists specifically because this text may contain PII; this adapter must not create a second, unscreened place ticket content gets written to disk/console.

## Performance Considerations

No caching or memoization anywhere in the call path (AD-6/AC #5) — this is a correctness requirement, not just a performance non-goal; Task 5's test asserts call-count, not just output equality, to catch an accidental memoization wrapper.

## Test Strategy

`node --test`, all LLM calls mocked (no real network calls in the suite). Test file structure: inject the Anthropic client (constructor-parameter or module-level override function) so each test can stub `messages.create` to return a canned response.

Minimum scenarios (maps directly to Tasks 2–5):
1. Billing-shaped ticket → `category="billing"`, valid `priority`, one-sentence `summary`, non-empty `draftReply` (AC #1)
2. Ambiguous ticket → `category="other"`, no throw (AC #2)
3. Invalid JSON response → `MALFORMED` (AC #3)
4. Valid JSON, missing key → `MALFORMED` (AC #3)
5. Valid JSON, wrong-typed key → `MALFORMED` (AC #3)
6. Valid JSON, out-of-enum `category` → resolves to `"other"` (AC #4)
7. Valid JSON, out-of-enum `priority` → resolves to `"medium"` (AC #4)
8. Two calls, identical `ticketText` → mock call-count asserted as 2, not 1 (AC #5)
9. Simulated timeout → `TIMEOUT` failure class
10. Simulated SDK/network throw → `NETWORK` failure class

## Risks/Assumptions & Dependencies

- **Assumption (this plan's own decision, not prior input):** Claude Haiku 4.5 (`claude-haiku-4-5`) via `@anthropic-ai/sdk`, chosen for cost/latency fit on a short-text classification task. Documented in the story's Dev Notes per the architecture's instruction that the story implementing this "must pick one and document the choice."
- **Assumption:** 18s client-side timeout — no value was fixed by the architecture (Deferred); chosen to sit just under AD-3's 20s PromptGateway bound so a Story 1.3 request doesn't stack two near-20s waits unpredictably. Flagged as a de facto AD per the spine's own instruction, not a silent detail.
- **Dependency:** adds `@anthropic-ai/sdk` — the first npm runtime dependency in this repo. Project-context's Do-Not-Do list says "do NOT pick a triage LLM provider or add its SDK without flagging it first" — flagged here explicitly for approval as part of this plan, satisfying that rule rather than bypassing it.
- **Risk:** `output_config.format` exact API shape is taken from current Claude API skill reference material, not verified against a live call in this environment (no network access during planning). If the SDK call shape has drifted, this surfaces as a implementation-time fix, not a design-level one — the two-gate validation logic (stage 2/3 above) does not depend on which exact SDK call shape is used.

## Context Files Consulted

- `_bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md` (AD-1, AD-4, AD-5, AD-6, Deferred section)
- `_bmad-output/planning-artifacts/epics.md` (Story 1.1 ACs)
- `_bmad-output/project-context.md` (Data Conventions, Global Do-Not-Do Rules)
- `_bmad-output/implementation-artifacts/1-1-triage-adapter-structured-output-with-validated-fallbacks.md` (story file, Dev Notes)

## Rationale Summary

This plan implements exactly AD-4's contract (structured-data gate, then enum fallback, in that order, nothing more) and nothing from Stories 1.2/1.3's scope. The two genuinely new decisions in this plan — LLM provider and timeout value — are both decisions the architecture explicitly assigned to this story rather than gaps in analysis, and both are called out rather than silently assumed, per this project's own confidence-scoring discipline.
