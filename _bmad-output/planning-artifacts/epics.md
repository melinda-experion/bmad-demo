---
stepsCompleted: [step-01, step-02, step-03, step-04]
inputDocuments: ['_bmad-output/planning-artifacts/prds/prd-BMAD-2026-07-30/prd.md', '_bmad-output/planning-artifacts/architecture/architecture-BMAD-2026-07-30/ARCHITECTURE-SPINE.md']
confidence: 62
confidence_label: Medium
confidence_rationale: Both FRs and all NFRs/ADs are fully covered by 4 stories across 2 independent, correctly file-scoped epics with no forward dependencies — the breakdown itself is a clean, complete derivation. Confidence is capped at Medium because it inherits carried-forward uncertainty from its Medium-confidence source documents: the LLM env-var name is still unresolved, AD-4's click-to-deselect behavior is an architectural invention rather than a stated PRD requirement, the 25s/30s timeout is a working baseline pending an open PRD question, and the duplication with a separate pre-existing approved architecture spine covering identical scope remains unreconciled.
---

# BMAD - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for BMAD Idea Launcher v2, decomposing the requirements from the PRD (`prd-BMAD-2026-07-30`) and Architecture (`architecture-BMAD-2026-07-30`) into implementable stories. No UX design contract exists for this scope. Per team preference, each approved story is also mirrored to its own file under `_bmad-output/planning-artifacts/epics/epic-{n}-{epic-slug}/story-{epic}.{story}-{slug}.md` — this document (`epics.md`) remains the single canonical source that downstream steps (readiness-check, sprint-planning, etc.) read.

## Requirements Inventory

### Functional Requirements

FR1: Given a non-empty prompt, the backend calls a configured LLM provider and returns exactly 3 well-formed ideas, replacing the current hardcoded stub.
FR2: User can toggle a favorite state on any one idea card, with a clearly highlighted visual state when active (single-select — favoriting a new card clears the previous one).

### NonFunctional Requirements

NFR1: The LLM API key is read only from a server-side environment variable; never exposed to client code or responses.
NFR2: A failed/timed-out provider call surfaces an inline error and preserves the typed prompt for retry.
NFR3: No caching/memoization of LLM responses — every prompt gets a genuinely fresh call (counter-metric SM-C1).
NFR4: The favorite highlight must be conveyed by more than color alone (accessibility).
NFR5: Idea cards render within 30 seconds under normal network conditions (SM-1, working baseline pending PRD Open Question 4).

### Additional Requirements

- No web framework — Node core `http` only; brownfield change, no starter template (existing `server.js`/`public/` already in place) (AD-1)
- New file `lib/ideaService.js` exporting `generateIdeas(prompt)`, a server-side-only adapter (AD-2, AD-6)
- Fixed `/api/ideas` contract: `200/400/502/504/500` status codes, `{error: string}` error shape, 10KB raw-body size cap enforced before JSON parsing (AD-5)
- The handler must not re-validate, truncate, or otherwise alter the adapter's resolved output; the adapter is the sole owner of the `AbortController`/timeout (AD-5, AD-6)
- "Well-formed" idea means non-empty trimmed `title` and `description` strings; the adapter's environment variable(s) are read once at module load, never per-call (AD-6)
- Client-side session-only state object in `app.js` holding prompt/ideas/favorite — a new decision, since the current codebase is DOM-driven rather than state-object-driven (AD-3)
- `favoritedIndex: number | null` held client-side, single-select, click-to-deselect the currently favorited card (AD-4)
- `node --test` specs must mock the outbound provider call — no real LLM calls in any test run (AD-6)
- Stack: Node.js `>=24`, CommonJS module system, `node --test` as the test runner

### UX Design Requirements

None — no UX design contract exists for this scope; explicitly skipped per user confirmation.

### FR Coverage Map

FR1: Epic 1 - Real LLM-backed idea generation replaces the hardcoded stub
FR2: Epic 2 - Single-select favorite toggle on idea cards

## Epic List

### Epic 1: Real LLM-Backed Idea Generation
Users get genuinely AI-generated ideas from the `Generate ideas` action instead of hardcoded stub text — the existing prompt input, `Generate ideas` button, and three-card rendering UI are unchanged; only the backend response source changes. Standalone: ships and is valuable even if Epic 2 never happens, since favoriting is independent of where the ideas come from.
**FRs covered:** FR1
**NFRs covered:** NFR1, NFR2, NFR3, NFR5
**Additional Requirements covered:** AD-1, AD-2, AD-5, AD-6

### Epic 2: Favorite an Idea Card
Users can mark exactly one of the three rendered idea cards as their favorite, with a clearly (non-color-only) highlighted state that resets whenever a new `Generate ideas` request is made. Standalone: works against either the stub or the real LLM backend, so it does not require Epic 1 to function — it only needs idea cards to exist, which they already do in the shipped v1 UI.
**FRs covered:** FR2
**NFRs covered:** NFR4
**Additional Requirements covered:** AD-3, AD-4

## Epic 1: Real LLM-Backed Idea Generation

Users get genuinely AI-generated ideas from the `Generate ideas` action instead of hardcoded stub text — the existing prompt input, `Generate ideas` button, and three-card rendering UI are unchanged; only the backend response source changes.

### Story 1.1: Real LLM Provider Call in the Idea Adapter

As a user submitting a prompt,
I want the backend to call a real LLM provider to generate ideas,
So that the ideas I see are genuinely produced for my prompt rather than fixed stub text.

**Acceptance Criteria:**

**Given** a non-empty prompt is passed to `generateIdeas(prompt)` in `lib/ideaService.js`
**When** the LLM provider responds successfully
**Then** the adapter resolves with exactly 3 entries shaped `{title, description}`, each with non-empty trimmed `title` and `description` strings
**And** the adapter never pads, truncates, or fabricates entries to force "exactly 3" — a malformed response is signaled by throwing, never silently repaired (FR1, AD-6)

**Given** the adapter module is loaded
**When** the process starts
**Then** the LLM API key is read from its server-side environment variable exactly once, at module load — never re-read per call
**And** the key value never appears in the adapter's resolved output or in any thrown error (NFR1, AD-2, AD-6)

**Given** two separate calls are made with the identical prompt text
**When** each call reaches the adapter
**Then** each call independently invokes the LLM provider — no caching or memoization of responses by prompt text (NFR3, AD-6)

**Given** the provider call exceeds the adapter's internal timeout
**When** its `AbortController` fires
**Then** the adapter throws an error with `.code === 'TIMEOUT'`
**And** the adapter owns and creates this `AbortController` itself — it is the only timeout mechanism inside the adapter (AD-5, AD-6)

**Given** the provider call fails at the network/transport level before responding
**When** the failure occurs
**Then** the adapter throws an error with `.code === 'NETWORK'` (AD-6)

**Given** the provider responds but the output does not parse into exactly 3 well-formed `{title, description}` entries
**When** the adapter validates the response
**Then** the adapter throws an error with `.code === 'MALFORMED'` (AD-6)

**Given** a `node --test` spec exercises the adapter
**When** the spec runs
**Then** the outbound provider call (e.g. `fetch`) is mocked — no real LLM call is made during any test run (AD-6)

### Story 1.2: Wire /api/ideas to the Real Adapter with Fixed Error Contract

As a user submitting a prompt through the app,
I want the `/api/ideas` endpoint to return real generated ideas or a clear, correctly-coded error,
So that I always get either useful ideas or an understandable failure I can retry.

**Acceptance Criteria:**

**Given** a `POST /api/ideas` request with a valid non-empty, under-2000-char `prompt` string
**When** the handler calls the adapter's `generateIdeas(prompt)` and it resolves
**Then** the handler returns `200 { ideas: [...] }` with the adapter's resolved array unchanged
**And** the handler does not itself re-validate, truncate, pad, or otherwise alter that array (FR1, AD-5, AD-6)

**Given** a request body that is not valid JSON, exceeds the 10KB raw-body size cap, has a non-string `prompt`, or has an empty/whitespace-only or over-2000-char trimmed `prompt`
**When** the handler processes the request
**Then** the handler returns `400 { error: string }`
**And** the 10KB size cap is enforced before JSON parsing is attempted (AD-5)

**Given** the adapter throws an error with `.code === 'TIMEOUT'`
**When** the handler catches it
**Then** the handler returns `504 { error: string }` (AD-5, AD-6)

**Given** the adapter throws an error with `.code === 'NETWORK'`
**When** the handler catches it
**Then** the handler returns `502 { error: string }` (AD-5, AD-6)

**Given** the adapter throws an error with `.code === 'MALFORMED'`, no `.code` at all, or an unrecognized `.code`
**When** the handler catches it
**Then** the handler returns `500 { error: string }` (AD-5, AD-6)

**Given** the handler is running
**When** any timeout condition arises
**Then** the handler starts no timer or abort mechanism of its own — the adapter's `AbortController` remains the sole timeout path for the request (AD-5)

**Given** a failed or timed-out response reaches the client
**When** the client displays the error
**Then** the client surfaces an inline error and preserves the user's typed prompt for retry (NFR2)

**Given** a `node --test` spec exercises the `/api/ideas` handler
**When** the spec runs
**Then** the outbound provider call is mocked — no real LLM call is made during any test run (AD-6)

## Epic 2: Favorite an Idea Card

Users can mark exactly one of the three rendered idea cards as their favorite, with a clearly (non-color-only) highlighted state that resets whenever a new `Generate ideas` request is made.

### Story 2.1: Client-Side State Object for Prompt, Ideas, and Favorite

As a user interacting with the idea generator,
I want the app's prompt, ideas, and favorite selection tracked consistently in one place,
So that the UI never shows stale or conflicting state across a new generation request.

**Acceptance Criteria:**

**Given** the page is loaded
**When** `app.js` initializes
**Then** a single client-side state object exists holding `prompt`, `ideas`, and `favoritedIndex`, scoped to the lifetime of the page
**And** no server-side or persisted storage (e.g. `localStorage`) is involved (AD-3)

**Given** the user types or changes the prompt input
**When** the input/change event fires
**Then** `state.prompt` is updated to match the current input value (AD-3)

**Given** the user clicks `Generate ideas`
**When** the request is dispatched
**Then** `state.ideas` is synchronously cleared and `state.favoritedIndex` is reset to `null` before the fetch is sent (AD-3)

**Given** a `Generate ideas` request is in flight
**When** the user attempts to click `Generate ideas` again
**Then** the button is disabled for the duration of the in-flight request, so no overlapping fetches or stale-response races are possible (AD-3)

### Story 2.2: Favorite Toggle with Accessible Highlight

As a user reviewing generated ideas,
I want to mark exactly one idea card as my favorite with a highlight I can perceive without relying on color,
So that I can clearly track which idea I've chosen to focus on.

**Acceptance Criteria:**

**Given** three idea cards are rendered
**When** the user clicks the favorite toggle on a card
**Then** `state.favoritedIndex` is set to that card's index and the card is visibly highlighted using more than color alone — e.g. a distinct border plus an icon/label change (FR2, NFR4, AD-4)

**Given** a card is already favorited
**When** the user clicks the favorite toggle on a different card
**Then** the previous card's highlight is removed and the newly clicked card becomes the sole favorited card — at most one favorited card at any time (FR2, AD-4)

**Given** a card is already favorited
**When** the user clicks the favorite toggle on that same card again
**Then** the card is un-favorited and `state.favoritedIndex` returns to `null` (AD-4)

**Given** a favorite is set
**When** the user clicks `Generate ideas` to request a new set of ideas
**Then** the favorite highlight is cleared and `state.favoritedIndex` resets to `null`, consistent with Story 2.1's reset behavior (FR2, AD-3)
