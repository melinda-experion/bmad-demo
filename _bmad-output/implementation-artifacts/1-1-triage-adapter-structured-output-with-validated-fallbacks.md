---
baseline_commit: d3156914b4d2b2e642b5f71e993d080f36558c4d
---

# Story 1.1: Triage Adapter — Structured Output With Validated Fallbacks

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Triaging Agent,
I want the system to turn my raw ticket text into a validated Category, Priority, Summary, and Draft Reply,
so that I never see a broken or out-of-scope value in a triage result.

## Acceptance Criteria

1. **Given** ticket text describing a billing issue, **When** `lib/triageService.js` processes it, **Then** it returns `category="billing"` (one of the 5-value enum), a `priority` from the 3-value enum, a one-sentence summary, and a non-empty draft reply (FR2)
2. **Given** ticket text that doesn't clearly match bug/billing/feature-request/question, **When** processed, **Then** `category` resolves to `"other"` without erroring (FR3)
3. **Given** a triage LLM response that isn't valid structured data (invalid JSON, or a missing/wrong-typed key), **When** processed, **Then** the adapter reports a `MALFORMED`-class failure rather than guessing a value (AD-4)
4. **Given** a triage LLM response with a `category` or `priority` value outside its enum (right type, wrong value), **When** processed, **Then** they resolve to `other`/`medium` respectively — never the raw out-of-enum value (AD-4)
5. **And** two calls with identical input each invoke the LLM — no caching or memoization (NFR1)

## Tasks / Subtasks

- [x] Task 1: Scaffold `lib/triageService.js` and the LLM client call (AC: #1)
  - [x] Subtask 1.1: Resolve the LLM-call mechanism (see Completion Notes — no new dependency added; raw `fetch` used instead of `@anthropic-ai/sdk`, superseding this subtask's original text after discovering project-context.md's "no npm dependencies beyond husky" rule and the prior app's own no-SDK precedent)
  - [x] Subtask 1.2: Implement `triageTicket(ticketText)` in `lib/triageService.js` — builds the prompt, calls Claude via raw `fetch` to the Messages API, returns the raw parsed response
  - [x] Subtask 1.3: Read the API key from `process.env.ANTHROPIC_API_KEY` — never hardcode, never log it or raw ticket text
- [x] Task 2: Implement the "parses as structured data" gate (AC: #3, AD-4)
  - [x] Subtask 2.1: Write failing tests: invalid JSON → `MALFORMED`; missing key → `MALFORMED`; wrong-typed key (e.g. `priority` as a number) → `MALFORMED`
  - [x] Subtask 2.2: Implement the schema check — valid JSON with `category`/`priority`/`summary`/`draftReply` all present as strings — before any enum check runs
  - [x] Subtask 2.3: On failure, return a `MALFORMED`-class result (no inline default; this is a failure, not a fallback) — shaped so Story 1.3's HTTP layer can map it straight to `MALFORMED:500` (AD-5) without re-deriving the class
- [x] Task 3: Implement enum validation with named fallbacks (AC: #4, AD-4)
  - [x] Subtask 3.1: Write failing tests: `category` outside `bug`/`billing`/`feature-request`/`question`/`other` → resolves to `"other"`; `priority` outside `low`/`medium`/`high` → resolves to `"medium"`
  - [x] Subtask 3.2: Implement the enum check — only runs after Task 2's structured-data gate passes; never touches Summary/Draft-Reply content (AD-4 scopes this to Category/Priority only)
- [x] Task 4: Implement the happy path (AC: #1, #2)
  - [x] Subtask 4.1: Write failing tests: a billing-shaped ticket → `category="billing"`, valid `priority`, one-sentence `summary`, non-empty `draftReply`; an ambiguous ticket → `category="other"` with no error thrown
  - [x] Subtask 4.2: Confirm the happy path returns cleanly through Tasks 2–3's validation without any inline default kicking in unnecessarily
- [x] Task 5: Verify no caching/memoization (AC: #5, NFR1)
  - [x] Subtask 5.1: Write a test asserting two calls with identical `ticketText` each trigger a distinct LLM call (assert call count on the mocked `fetch`, not just output equality)
  - [x] Subtask 5.2: Confirm the implementation has no memoization wrapper, cache map, or identical-input shortcut anywhere in the call path

### Review Findings

- [x] [Review][Patch] Missing `ANTHROPIC_API_KEY` throws a raw `Error` instead of the module's own `{ok:false, failureClass, message}` contract [lib/triageService.js:67] — fixed: added `CONFIG` failure class, returns `{ok:false, failureClass:"CONFIG", message}` instead of throwing.
- [x] [Review][Patch] No delimiter/fencing around customer-supplied `ticketText` in the LLM prompt [lib/triageService.js:19,64] — fixed: `buildPrompt` now wraps `ticketText` in `<<<TICKET_START>>>`/`<<<TICKET_END>>>` markers with an explicit instruction to treat the enclosed content as data, not instructions.
- [x] [Review][Patch] Unguarded `response.json()` can throw past the discriminated-union boundary [lib/triageService.js:102] — fixed: wrapped in try/catch, returns `{ok:false, failureClass:"NETWORK", message:"Triage LLM response body was not valid JSON"}` on parse failure.
- [x] [Review][Patch] Abort timer only covers the `fetch` call, not the subsequent `response.json()` body-read [lib/triageService.js:95-102] — fixed: `response.json()` now runs inside the same try block as `fetch`, sharing the same abort controller/timer, so a stalled body-read after headers still resolves to `TIMEOUT`.
- [x] [Review][Patch] `isNonEmptyStringField` only checks `typeof value === "string"`, not non-emptiness — fixed: renamed to `isStringField` to match its actual behavior.
- [x] [Review][Patch] `responseBody?.content?.[0]?.text` assumed the first content block is always text — fixed: `extractText` now finds the first block with `type === "text"` instead of indexing `[0]`.
- [x] [Review][Patch] `"MALFORMED"`/`"TIMEOUT"`/`"NETWORK"` were repeated string literals — fixed: added a `FAILURE_CLASSES` constant object (now including `CONFIG`), used consistently throughout.
- [x] [Review][Defer] Non-string/null/undefined `ticketText` is not validated before being interpolated into the prompt — deferred, pre-existing scope boundary (story's own Dev Notes: empty-string rejection is explicitly Story 1.3's client-side job; a non-string here safely stringifies via template literal rather than crashing).
- [x] [Review][Defer] `summary`/`draftReply` are passed through with no output sanitization (control characters/HTML) before being marked `ok:true` — deferred, this is a rendering-layer concern for whichever UI displays the text (Story 1.3's `public/app.js`), not this backend adapter.
- [x] [Review][Defer] No retry/backoff, no rate-limit/auth-error distinction from generic `NETWORK`, no fallback if the hardcoded model ID is retired — deferred, explicitly out of v1 scope per NFR1 ("no hard latency SLA in v1") and the architecture's Deferred section (hardening not designed here).

## Dev Notes

### LLM Provider Decision (resolves architecture's Deferred item)

The architecture spine (AD-4 rationale, Deferred section) deliberately left the triage LLM provider unchosen — "a story implementing FR2/FR3 must pick one and document the choice; it becomes a de facto decision, not a silent implementation detail." This story is that story. Decision, made explicitly here per user direction at story creation:

- **Provider/model:** Claude Haiku 4.5 (`claude-haiku-4-5`) via the official Anthropic SDK (`@anthropic-ai/sdk`) — a cost-sensitive classification/extraction task (category/priority/summary/draft-reply from short ticket text) doesn't need a larger model; Haiku 4.5 is Anthropic's current fast/cheap tier ($1/$5 per 1M input/output tokens) and supports structured JSON output.
- **Structured output mechanism:** `output_config: {format: {...}}` on `messages.create()` (or `client.messages.parse()` if a straightforward schema-validated call fits) — constrains the response to the `{category, priority, summary, draftReply}` shape at the API level. This narrows, but does not eliminate, the need for Task 2/3's own validation gate — AD-4 requires the adapter to independently verify "parses as structured data" and enum membership regardless of what the provider's structured-output feature already promises, since the architecture is explicitly provider-agnostic and must not trust one vendor's guarantee as a substitute for its own invariant.
- **Timeout:** not fixed by the architecture (Deferred — "its trigger value is undefined; a story implementing it must pick one and it becomes a de facto AD"). Pick a reasonable client-side call timeout (e.g. 15–20s, consistent with AD-3's PromptGateway bound) and map an exceeded timeout to the `TIMEOUT:504` class from AD-5's taxonomy. Document the chosen value in Completion Notes.
- **Not in this story's scope:** wiring the API key into `server.js`/deployment config (Story 1.3), and the PromptGateway call (Story 1.2). This story only needs `ANTHROPIC_API_KEY` present in the local dev environment to run/test against a live model if desired — tests themselves must mock the client (Testing Standards below), not hit the real API.

### Architecture Compliance (binding — from ARCHITECTURE-SPINE.md v1)

- **AD-1 (layered + adapter):** `lib/triageService.js` is the *sole* caller of the triage LLM. It must never call `lib/promptGatewayClient.js` or vice versa — no adapter calls another adapter. This story does not touch `server.js`, `lib/promptGatewayClient.js`, or `public/` — those don't exist yet and are out of scope (Stories 1.2/1.3 create them).
- **AD-4 (triage output validation) — this story's core contract:**
  - "Parses as structured data" = valid JSON with `category`, `priority`, `summary`, `draftReply` keys, **each a string**. Anything short of that (invalid JSON, missing key, wrong type) is *not* structured data.
  - Not structured data → adapter failure (`MALFORMED` class, no inline default — Task 2).
  - Is structured data, but `category`/`priority` value is outside its enum (right type, wrong value) → resolves inline to `other`/`medium` (Task 3). This is the *only* case that gets a soft fallback.
  - Raw model text must never reach the response as a `Category`/`Priority` field value.
  - AD-4 does **not** govern Summary-is-one-sentence or Draft-Reply-non-empty — those are prompt-design/test concerns per the spine's own scoping note, not structural invariants. Don't add validation logic for them beyond what AC #1's test checks for.
- **AD-5 (error/status taxonomy) — this story's output must compose cleanly into it, even though HTTP mapping itself is Story 1.3's job:** triage-adapter failures map to `TIMEOUT:504` / `NETWORK:502` / `MALFORMED:500` (`MALFORMED` includes AD-4's fully-not-structured-data case). Design the adapter's failure return/throw shape so Story 1.3 can map it directly to one of these three classes without re-parsing.
- **AD-6 (state & scope):** the triage LLM call must never be cached or memoized — every call is a fresh network call, always (Task 5, AC #5).

### Data Conventions (from project-context.md — must match exactly)

- `category` ∈ `bug` | `billing` | `feature-request` | `question` | `other` (lowercase, hyphenated where multi-word)
- `priority` ∈ `low` | `medium` | `high` (lowercase)
- These are the *only* legal values this module may ever return for `category`/`priority` — no other casing, no synonyms.

### Project Structure Notes

- This story creates exactly one new file: `lib/triageService.js` (plus its test file under `test/`). No `server.js`, `public/`, or `lib/promptGatewayClient.js` — per epics.md's Additional Requirements (corrected during implementation-readiness review), scaffolding is spread across all 3 stories as each needs it, not front-loaded into 1.1.
- No conflicts detected against project-context.md's Source Layout — `lib/triageService.js` as "sole caller of the triage LLM" matches exactly.

### Testing Standards Summary

- `node --test` (built-in runner) — no other test framework, per Stack table.
- Tests must **mock** the Anthropic SDK client / LLM call — never make real API calls in the test suite (cost, determinism, and CI reliability). Inject the client or stub the SDK call so Task 2/3/4/5's scenarios (malformed JSON, missing key, wrong type, out-of-enum value, happy path, call-count assertion) are all constructible without network access.
- Cover every AC explicitly: 5 ACs → at minimum 5 distinct test scenarios, plus the sub-cases under Task 2/3 (invalid JSON, missing key, wrong-typed key are 3 separate `MALFORMED` scenarios, not one).

### Previous Story Intelligence

Not applicable — this is the first story in Epic 1 (story_num = 1); no previous story file exists to carry learnings from.

### References

- [Source: _bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md#AD-4 — Triage output validation]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md#AD-1 — Layered + adapter structure]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md#AD-5 — Error/status taxonomy]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md#AD-6 — State & scope invariant]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md#Deferred — Triage LLM provider, SDK, and API-key convention]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1: Triage Adapter — Structured Output With Validated Fallbacks]
- [Source: _bmad-output/project-context.md#Global Do-Not-Do Rules (Always Enforced)]

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

- Implemented `lib/triageService.js` per the approved implementation plan, with one design change made and re-approved mid-plan: the original plan called for `@anthropic-ai/sdk` as a new dependency, but before writing code this was checked against `project-context.md`'s Technology Stack line ("No npm dependencies beyond husky") and the prior demo app's own `lib/ideaService.js` (git history, commit `8e9bc31`), which used raw `fetch` straight to the Anthropic Messages API with no SDK. Switched to that pattern — no new dependency added, `package.json` unchanged. User re-approved the revised plan before implementation began.
- LLM provider/model: `claude-haiku-4-5`, hardcoded constant (not env-configurable — an explicit story-level decision, matching the architecture's instruction to "pick one and document the choice"). API key via `process.env.ANTHROPIC_API_KEY`.
- Timeout: 18s (`AbortController`), chosen to sit under AD-3's 20s PromptGateway bound so Story 1.3 doesn't stack two near-20s waits. Maps to the `TIMEOUT` failure class.
- Failure return shape: `{ok: false, failureClass: 'TIMEOUT'|'NETWORK'|'MALFORMED', message}` on failure, `{ok: true, category, priority, summary, draftReply}` on success — a discriminated union rather than throwing, so Story 1.3 can map `failureClass` directly to AD-5's `TIMEOUT:504`/`NETWORK:502`/`MALFORMED:500` without parsing error messages.
- All 5 ACs covered by 11 test scenarios in `test/triageService.test.js` (3 distinct `MALFORMED` sub-cases for AC3, both enum-fallback directions for AC4, explicit call-count assertion for AC5, plus TIMEOUT/NETWORK/non-ok-status failure paths beyond the ACs' minimum). Full suite (`npm test`) passed 11/11 before code review.
- No linter is configured in this repo (`package.json` has no lint script) — none run.
- **Post-review (see Review Findings):** 7 patch findings applied — added `CONFIG` failure class for missing `ANTHROPIC_API_KEY` (was a raw throw), added `<<<TICKET_START>>>`/`<<<TICKET_END>>>` delimiter fencing around ticket text in the prompt, guarded `response.json()` against non-JSON bodies (`NETWORK`), extended the abort timeout to cover the body-read phase, renamed `isNonEmptyStringField` → `isStringField`, filtered response content blocks by `type === "text"` instead of indexing `[0]`, added a `FAILURE_CLASSES` constant. 4 new tests added (CONFIG path, malformed response body, delimiter fencing, non-first text block). Full suite now 15/15 passing. 2 items deliberately deferred to `deferred-work.md` (output sanitization belongs to Story 1.3's UI layer; retry/backoff/rate-limiting explicitly out of v1 scope per NFR1); 1 item dismissed as noise (`__setTimeoutMsForTest` export matches the prior app's own precedent).

### File List

- `lib/triageService.js` (new)
- `test/triageService.test.js` (new)

## Change Log

- 2026-08-14: Story implemented — `lib/triageService.js` + `test/triageService.test.js`, all 5 ACs covered, 11/11 tests passing. Status set to review.
- 2026-08-14: Addressed code review findings — 7 items resolved (2 decision-needed + 5 patch), 2 deferred, 1 dismissed. Suite now 15/15 passing.
