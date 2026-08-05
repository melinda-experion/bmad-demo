---
story: '1-1-real-llm-backed-idea-generation'
date: '2026-07-29'
status: pending-approval
---

# Implementation Plan — Story 1.1: Real LLM-Backed Idea Generation

## Scope Summary

Replace the hardcoded fake-idea stub in `server.js`'s `POST /api/ideas` handler with a real LLM-backed generation flow via a new `lib/ideaService.js` adapter. No client-side (`public/`) changes are in scope.

## Impacted Modules & Files

- **NEW** `lib/ideaService.js` — the `generateIdeas(prompt)` adapter
- **UPDATE** `server.js` — only the success-path body of the existing `/api/ideas` handler, plus one new validation check
- **NEW** test files under `test/` — adapter unit tests, endpoint integration tests
- **NO CHANGE**: `public/index.html`, `public/app.js`, `public/styles.css`, all static-serving routes, `module.exports`/`server.listen`

## Detailed Design Approach

`lib/ideaService.js` exports `generateIdeas(prompt)`, signature `(prompt: string) => Promise<Array<{title, description}>>` (Architecture AD-6). It owns and constructs its own `AbortController`, calls the LLM provider via native `fetch` (Node ≥18 built-in, no new dependency per AD-1/dependency governance), and aborts the call at 25s. `server.js`'s handler awaits this call inside its existing `try/catch`, replacing the current hardcoded array, and maps thrown `.code` values to HTTP status per AD-5. The existing invalid-JSON and empty-prompt `400` checks are preserved unchanged; a new max-length (`>2000` trimmed chars) check is added alongside them.

## Data Model Usage

None. No database exists or is introduced. The only data shape crossing any boundary is the idea object `{title, description}`, whose shape is unchanged from what `server.js` already returns today (Architecture AD-5).

## API / Interface Changes

No new endpoints. `POST /api/ideas`'s contract (Architecture AD-5) is being *fulfilled for real* rather than changed: request `{prompt: string}`; success `200 {ideas: [...]}` (exactly 3); errors `400`/`502`/`504`/`500` per the `.code` taxonomy in `.ai-context-errors.md`.

## Error Handling & Edge Cases

- Adapter throws only (never resolves an error envelope); `.code` ∈ `{'TIMEOUT', 'NETWORK', 'MALFORMED'}`, mapped by the handler to `504`/`502`/`500`; any uncoded/unknown throw → `500`.
- Provider response that doesn't parse into exactly 3 well-formed `{title, description}` entries → adapter throws `MALFORMED` — never padded, truncated, or fabricated.
- Request validation (before the adapter is ever called): invalid JSON, non-string `prompt`, empty/whitespace-only `prompt`, or `>2000` trimmed chars → `400`.

## Security Considerations

The LLM API key is read exclusively via `process.env.IDEA_LLM_API_KEY` inside `lib/ideaService.js` (Architecture AD-2) — never logged, never returned in any response, never referenced elsewhere. No new auth surface is introduced (PRD: no accounts).

## Performance Considerations

Adapter-owned 25s timeout leaves headroom under the PRD's 30s end-to-end target (SM-1). No caching or memoization of provider responses — deliberate, per PRD counter-metric SM-C1, not an oversight to "optimize" later.

## Test Strategy

`node --test` only (existing convention, no new framework). Unit tests for `lib/ideaService.js` with a mocked `fetch` covering: success (3 valid ideas), timeout (`.code='TIMEOUT'`), network failure (`.code='NETWORK'`), malformed output (`.code='MALFORMED'`, including a 2- or 4-idea response). Integration tests for `POST /api/ideas` covering all five response codes (`200`/`400`/`502`/`504`/`500`). A dedicated test proving two identical-prompt requests each independently reach the mocked provider (no caching). A rendering test confirming exactly 3 cards with title+description on a successful response.

## Risks, Assumptions & Dependencies

- **Assumption (flagged, needs your input):** LLM provider is Anthropic's Messages API via native `fetch`; the exact model ID could not be reliably confirmed via web research this session (a search result surfaced a name not recognized as a real current model) — the adapter reads it from `ANTHROPIC_MODEL` at runtime and fails loudly if unset, rather than guessing.
- **Dependency:** `IDEA_LLM_API_KEY` and `ANTHROPIC_MODEL` must be set in the environment for real end-to-end runs; unit tests use a mocked `fetch` and don't require real credentials.
- **Non-blocking note:** PRD Open Question 2 (whether a server-side LLM proxy still fits the 1-2hr build budget) is a time-management concern for the builder, not a technical gap in this plan.

## Context Files Consulted

`.ai-context.md`, `.ai-context-security.md`, `.ai-context-dependencies.md`, `.ai-context-api.md`, `.ai-context-errors.md`, `.ai-context-idea-generation.md`, `ARCHITECTURE-SPINE.md` (AD-1, AD-2, AD-5, AD-6), `prd.md` (FR-2, SM-1, SM-C1), `epics.md` / the story file itself (Acceptance Criteria 1–7).

## Rationale Summary

- Architecture AD-6 already fixes the handler/adapter interface and error-code taxonomy exactly — this plan implements that contract literally rather than inventing a new one.
- The existing `server.js` already has working JSON-parse and empty-prompt `400` handling that must be preserved, not rewritten — re-verified by reading the current file rather than assuming.
- PRD SM-C1 explicitly forbids response caching as a counter-metric, ruling out an "optimization" a developer might otherwise reach for.

## Confidence: High

All technical decisions are fully pinned by the approved Architecture Spine and PRD except the specific LLM model ID, which is explicitly called out above as needing your confirmation rather than silently assumed.
