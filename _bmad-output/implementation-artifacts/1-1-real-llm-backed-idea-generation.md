---
baseline_commit: aa9f3290a67274a330bda3dd53b070629cad2cb4
---

# Story 1.1: Real LLM-Backed Idea Generation

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a BMAD learner,
I want the Generate ideas button to call a real LLM-backed service instead of a hardcoded stub,
so that I get genuinely varied, AI-generated starter ideas for my prompt.

## Acceptance Criteria

1. Given the server has `IDEA_LLM_API_KEY` configured, when I submit a non-empty prompt via `POST /api/ideas`, then `lib/ideaService.js`'s `generateIdeas(prompt)` is called and its resolved array of exactly 3 `{title, description}` ideas is returned as `200 { ideas: [...] }`.
2. Given the provider call exceeds the 25s server-enforced timeout, when `Generate ideas` is clicked, then the response is `504 { error }` and the adapter's `AbortController` actually aborts the outbound provider request.
3. Given the provider call fails before responding (network/provider error), when `Generate ideas` is clicked, then the response is `502 { error }`.
4. Given the provider responds but the output doesn't parse into exactly 3 well-formed `{title, description}` entries, when `Generate ideas` is clicked, then the adapter throws (never pads/truncates/fabricates) and the response is `500 { error }`.
5. Given the same prompt is submitted twice in separate clicks, when each `Generate ideas` click completes, then each triggers a genuinely fresh call to the LLM provider — no cached/memoized response is ever returned.
6. Given the LLM API key, when any part of the request/response cycle executes, then the key is read only from `process.env.IDEA_LLM_API_KEY` inside `lib/ideaService.js` and never appears in any client-served response or asset.
7. Given a successful `/api/ideas` response, when the client renders it, then exactly three cards appear, each showing its title and description text.

## Tasks / Subtasks

- [x] Task 1: Create `lib/ideaService.js` adapter (AC: 1, 2, 3, 4, 5, 6)
  - [x] Export `generateIdeas(prompt)`: `(prompt: string) => Promise<Array<{title, description}>>`, resolving to exactly 3 entries — this exact export name/signature is fixed by Architecture AD-6, do not rename or restructure it
  - [x] Read the LLM API key only via `process.env.IDEA_LLM_API_KEY` inside this file — never elsewhere, never hardcoded
  - [x] Call the LLM provider via native `fetch` (Node ≥18 built-in) — do not add a new npm dependency for this; see "Provider & Model — Needs Your Confirmation" below before writing the actual call
  - [x] Own and construct the `AbortController` inside this adapter (not in `server.js`); abort the outbound `fetch` at 25s; on abort, throw `new Error(...)` with `.code = 'TIMEOUT'`
  - [x] On any network/connection failure before the provider responds, throw with `.code = 'NETWORK'`
  - [x] Parse the provider's response; if it does not yield exactly 3 well-formed `{title, description}` entries, throw with `.code = 'MALFORMED'` — never pad, truncate, or fabricate entries to force conformance
  - [x] Do not memoize, cache, or short-circuit on a repeated identical prompt — every call must reach the provider (no module-level cache keyed by prompt text)
  - [x] All failures signal by throwing only — never by resolving an `{ error }` envelope (the caller's single `try/catch` is the only error path)

- [x] Task 2: Wire the adapter into `server.js`'s `/api/ideas` handler (AC: 1, 2, 3, 4, 6)
  - [x] Replace the current hardcoded fake-ideas block (the `const ideas = [...]` literal array) with `const ideas = await generateIdeas(prompt)`
  - [x] Wrap the call in `try/catch`; map the thrown error's `.code` to a status: `TIMEOUT`→`504`, `NETWORK`→`502`, `MALFORMED`→`500`, any uncoded/unrecognized throw→`500`
  - [x] **Preserve** the existing invalid-JSON `400` handling and the existing empty-prompt `400` check — both already work correctly, do not rewrite them
  - [x] **Add** the max-length validation that does not currently exist: trimmed `prompt` over 2000 characters → `400 { error }` (Architecture AD-5 requires this; the current handler only checks for empty, not over-length)
  - [x] **Preserve** all static-file-serving routes (`/`, `/styles.css`, `/app.js`), the 404 fallback, and the `module.exports`/`server.listen` behavior exactly as they are today — this story does not touch them

- [x] Task 3: Confirm client rendering still satisfies FR3 (AC: 7)
  - [x] `public/app.js`'s existing card-rendering code (the `results.innerHTML = payload.ideas.map(...)` block) needs **no code change** — the response shape (`{ ideas: [{title, description}] }`) is unchanged by this story
  - [x] Add a test (see Task 4) that exercises this rendering path end-to-end rather than assuming it still works

- [x] Task 4: Tests (`node --test`)
  - [x] Unit tests for `lib/ideaService.js` with a mocked `fetch`: success path (3 valid ideas), timeout path (`.code = 'TIMEOUT'`), network-failure path (`.code = 'NETWORK'`), malformed-output path (`.code = 'MALFORMED'`, including a provider response with 2 or 4 ideas)
  - [x] Integration test(s) for `POST /api/ideas` exercising each status code: `200`, `400` (invalid JSON, empty prompt, >2000 chars), `502`, `504`, `500`
  - [x] Test that two separate `POST /api/ideas` calls with the identical prompt each independently reach the (mocked) provider — proves no caching (AC 5)
  - [x] Test that a successful response renders exactly 3 cards with visible title + description (AC 7)

### Review Findings

- [x] [Review][Decision] All non-2xx provider responses collapse into `NETWORK`/502 with no distinction for 429/401/403 vs. a true pre-response network failure — resolved: leave as-is, current collapsed behavior is spec-compliant with AD-5's fixed status set. [lib/ideaService.js]
- [x] [Review][Decision] The prompt asks the model for "3 distinct starter ideas," but nothing validates distinctness — resolved: leave as-is for MVP, not a stated Acceptance Criterion and duplicates are rare in practice. [lib/ideaService.js]
- [ ] [Review][Patch] Timeout does not cover response-body reading — `clearTimeout(timer)` fires in the `finally` right after `fetch()`'s promise settles (headers received), before `await response.json()`. A provider that sends headers promptly but stalls the body can hang past the intended 25s bound, defeating AC2's timeout guarantee. [lib/ideaService.js:~90-114]
- [ ] [Review][Patch] `parseIdeas` reads `responseBody?.content?.[0]?.text` without checking `type` — assumes the first content block is always the text block. Fragile if the Anthropic response ever includes a non-text block first; a valid response could be wrongly classified as `MALFORMED`. [lib/ideaService.js:34]
- [ ] [Review][Patch] `response.json()` is unguarded — a 2xx response with a non-JSON body throws a raw, uncoded `SyntaxError` instead of going through the explicit `.code = 'MALFORMED'` path. Currently falls through to 500 by the `|| 500` default anyway, but is inconsistent with AD-6's explicit-coding requirement. [lib/ideaService.js:113]
- [ ] [Review][Patch] No server-side logging when a provider call fails — every failure (timeout/network/malformed/misconfig) is silently swallowed in `server.js`'s catch block with no `console.error`, leaving production debugging blind. [server.js:76-82]
- [ ] [Review][Patch] `isWellFormedIdea` accepts whitespace-only `title`/`description` (checks `.length > 0` without `.trim()` first) — a model returning blank-looking fields passes validation and renders as an empty idea card. [lib/ideaService.js:22-31]
- [ ] [Review][Patch] `buildPrompt` splices the raw user prompt into the instruction text with no delimiter or escaping — a prompt-injection surface. Downstream JSON-schema validation limits the blast radius, but a clear separator/tag around user content is still warranted as defense-in-depth. [lib/ideaService.js:12-20]
- [ ] [Review][Patch] No upper bound on LLM-returned `title`/`description` length, asymmetric with the 2000-char cap enforced on user input — add a reasonable max-length check in `isWellFormedIdea`. [lib/ideaService.js:22-31]
- [ ] [Review][Patch] Global mutable `timeoutMs` plus the test-only `__setTimeoutMsForTest` exported unguarded from the production module is a test-pollution/footgun hazard — inject the timeout via an options parameter instead of shared module state. [lib/ideaService.js:10,117-119]
- [ ] [Review][Patch] No test covers the exact-2000-character boundary (only over-2000 is tested) — add one boundary test to lock in the inclusive `≤2000` contract. [test/story1.test.js]

## Dev Notes

- Architecture patterns/constraints in force for this story: AD-1 (no framework — stay on Node core `http`), AD-2 (server-side-only key via `IDEA_LLM_API_KEY`), AD-5 (fixed `/api/ideas` wire contract and status codes), AD-6 (fixed handler/adapter interface, error-code taxonomy, no caching). AD-3 and AD-4 (client state, favorite) are **not** touched by this story — that's Stories 1.2/1.3.
- This is a **brownfield** change to an existing working scaffold, not new project setup — `server.js` and `public/` already exist and already handle the happy path with a fake stub. Read them before editing (see below).
- Testing standard: `node --test` only (already wired via `npm test` in `package.json`) — do not introduce Jest, Mocha, or any other test framework.

### Files Being Modified — Current State & Required Changes

**`server.js` (UPDATE, not new)** — current state: a working `http.createServer` with a `POST /api/ideas` handler that already parses the JSON body in a `try/catch` (→ `400` on parse failure) and already checks for an empty/whitespace prompt (→ `400`). It currently responds with a **hardcoded array of 3 fake ideas** built by string-templating the prompt — no real provider call exists yet. Static file serving (`/`, `/styles.css`, `/app.js`) and the 404 fallback are unrelated to this story and must not change.
- What this story changes: only the body of the success path inside the `/api/ideas` handler — swap the hardcoded array for `await generateIdeas(prompt)`, add the `.code`→status mapping, add the missing 2000-char validation.
- What must be preserved: the existing JSON-parse `400`, the existing empty-prompt `400`, all static routes, the 404 fallback, `module.exports`/`server.listen`.

**`lib/ideaService.js` (NEW file)** — does not exist yet. This is the only new source file this story creates.

**`public/app.js` (no change expected)** — current state: already sends `POST /api/ideas` with `{prompt}`, already disables the Generate button during the in-flight request, already renders `payload.ideas` into cards via `escapeHtml`-wrapped title/description, already surfaces `payload.error` on a non-`ok` response while preserving the typed prompt. None of this needs to change for this story since the response shape is unchanged — verify with a test rather than editing it.

### Provider & Model — Needs Your Confirmation Before Implementation

The PRD (Open Question 1) and Architecture Spine both explicitly leave the LLM provider/model choice to the builder, tagged `[ASSUMPTION: Anthropic Claude]`. Web research today confirmed the general Anthropic Messages API shape (native `fetch` to `https://api.anthropic.com/v1/messages`, `x-api-key` + `anthropic-version` headers — this convention is stable and long-standing), **but a specific model ID could not be confirmed reliably** — a search result surfaced a model name that doesn't match any model this session actually knows to exist, so it is not trustworthy enough to hardcode.

**Do not hardcode a guessed model ID.** Instead:
- Read the model name from an environment variable (e.g. `ANTHROPIC_MODEL`), with no silent fallback to a guessed value — fail loudly (throw at startup, or on first call) if it's unset, rather than defaulting to a possibly-wrong model.
- Confirm the exact model ID and current Anthropic API version header value with the user/builder before or during implementation, rather than the dev agent picking one unverified.

Also flagged, not blocking: PRD Open Question 2 asks whether adding a server-side LLM proxy still fits the project's 1-2 hour build budget — a time-management concern for the builder, not a technical gap in this story.

### Project Structure Notes

- Alignment: matches the Architecture Spine's Structural Seed exactly — `server.js`, new `lib/ideaService.js`, `public/`, `test/`. No new top-level directories needed.
- Detected variance (not a conflict, an intentional gap this story closes): `server.js` currently has no 2000-character max-length check on `prompt` — Architecture AD-5 requires one; Task 2 adds it.

### References

- [Source: ARCHITECTURE-SPINE.md#AD-2] — server-side-only key
- [Source: ARCHITECTURE-SPINE.md#AD-5] — fixed wire contract, status codes, timeout
- [Source: ARCHITECTURE-SPINE.md#AD-6] — handler/adapter interface, error taxonomy, no caching
- [Source: prd.md#FR-2] — generate-ideas behavior, 30s target, error+retry
- [Source: prd.md#SM-C1] — no caching/reuse counter-metric
- [Source: epics.md#Story 1.1] — acceptance criteria origin
- [Source: .ai-context-api.md], [Source: .ai-context-errors.md], [Source: .ai-context-idea-generation.md] — always-relevant context for this story per project customization

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

None — implementation proceeded without needing a debug log; all red/green cycles passed on first or second iteration.

### Completion Notes List

- Confirmed provider/model choice with the user before implementation (per the story's blocking note): Anthropic Messages API (`https://api.anthropic.com/v1/messages`, `anthropic-version: 2023-06-01`), model ID `claude-sonnet-5` read from `process.env.ANTHROPIC_MODEL` with no silent fallback (throws if unset).
- `lib/ideaService.js` created: owns its own `AbortController`/25s timeout, throws `.code`-tagged errors (`TIMEOUT`/`NETWORK`/`MALFORMED`) or an uncoded error (missing config), never memoizes, never pads/truncates/fabricates malformed provider output.
- `server.js`'s `/api/ideas` handler now calls `generateIdeas(prompt)`, maps thrown `.code` to status (`TIMEOUT`→504, `NETWORK`→502, `MALFORMED`→500, uncoded→500), and adds the previously-missing >2000-char validation (400). Existing invalid-JSON 400, empty-prompt 400, static routes, 404 fallback, and `module.exports`/`server.listen` are unchanged.
- `public/app.js` required no changes; added a test verifying the existing rendering path still renders exactly 3 cards against the new response shape.
- Tests: added `test/ideaService.test.js` (9 unit tests covering success, timeout, network failure, all malformed-output variants, no-memoization, missing-model-config) and extended `test/story1.test.js` with integration tests for 400 (invalid JSON, >2000 chars), 502, 504, 500, and no-caching at the HTTP level. Full suite: 21/21 passing (`npm test`).

### File List

- `lib/ideaService.js` (new)
- `server.js` (modified)
- `test/ideaService.test.js` (new)
- `test/story1.test.js` (modified)

## Change Log

- 2026-08-04: Implemented Story 1.1 — real LLM-backed idea generation via `lib/ideaService.js`, wired into `server.js`'s `/api/ideas` handler with full error-code-to-status mapping and 2000-char validation; added unit and integration test coverage for all acceptance criteria.
