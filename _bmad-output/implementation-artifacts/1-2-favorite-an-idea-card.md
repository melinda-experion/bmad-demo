---
baseline_commit: 8e9bc31fb54df14a7b0e563d95f48b9616458ece
---

# Story 1.2: Favorite an Idea Card

Status: ready-for-dev

<!-- Combines epics.md Story 2.1 (client-side state object) + Story 2.2 (favorite toggle UI) per sprint-status.yaml key "1-2-favorite-an-idea-card" (Epic 2 covers both under one sprint slot). -->

## Story

As a user interacting with the idea generator,
I want the app's prompt, ideas, and favorite selection tracked consistently in one place, with a favorite toggle I can perceive without relying on color,
So that the UI never shows stale or conflicting state, and I can clearly track which idea I've chosen to focus on.

## Acceptance Criteria

1. Given the page is loaded, when `app.js` initializes, then a single client-side state object exists holding `prompt`, `ideas`, and `favoritedIndex`, scoped to the lifetime of the page, and no server-side or persisted storage (e.g. `localStorage`) is involved (AD-3).
2. Given the user types or changes the prompt input, when the input/change event fires, then `state.prompt` is updated to match the current input value (AD-3).
3. Given the user clicks `Generate ideas`, when the request is dispatched, then `state.ideas` is synchronously cleared and `state.favoritedIndex` is reset to `null` before the fetch is sent (AD-3).
4. Given a `Generate ideas` request is in flight, when the user attempts to click `Generate ideas` again, then the button is disabled for the duration of the in-flight request, so no overlapping fetches or stale-response races are possible (AD-3).
5. Given three idea cards are rendered, when the user clicks the favorite toggle on a card, then `state.favoritedIndex` is set to that card's index and the card is visibly highlighted using more than color alone — e.g. a distinct border plus an icon/label change (FR2, NFR4, AD-4).
6. Given a card is already favorited, when the user clicks the favorite toggle on a different card, then the previous card's highlight is removed and the newly clicked card becomes the sole favorited card — at most one favorited card at any time (FR2, AD-4).
7. Given a card is already favorited, when the user clicks the favorite toggle on that same card again, then the card is un-favorited and `state.favoritedIndex` returns to `null` (AD-4).
8. Given a favorite is set, when the user clicks `Generate ideas` to request a new set of ideas, then the favorite highlight is cleared and `state.favoritedIndex` resets to `null`, consistent with AC3 (FR2, AD-3).

## Tasks / Subtasks

- [ ] Task 1: Introduce client-side state object in `public/app.js` (AC: 1, 2, 3, 4)
  - [ ] Add a single `state = { prompt: "", ideas: [], favoritedIndex: null }` object scoped to the module (page lifetime only, no `localStorage`/`sessionStorage`)
  - [ ] Wire the prompt `<textarea>` input event to update `state.prompt`
  - [ ] On `Generate ideas` click, synchronously set `state.ideas = []` and `state.favoritedIndex = null` before `fetch` is dispatched
  - [ ] Keep the existing in-flight button-disable behavior (already present), now driven off/consistent with state
- [ ] Task 2: Render idea cards from `state.ideas` with a favorite toggle per card (AC: 5, 6, 7)
  - [ ] On successful response, set `state.ideas = payload.ideas` and re-render cards from state (not directly from `payload`)
  - [ ] Add a favorite-toggle control to each rendered card (e.g. a button with a star icon/label), wired to click → toggle that card's index in `state.favoritedIndex` (set/unset/move per AC 5-7)
  - [ ] Re-render (or update classes) after every favorite toggle so exactly one card reflects `state.favoritedIndex`
- [ ] Task 3: Accessible, non-color-only highlight (AC: 5)
  - [ ] Add a CSS class (e.g. `.card.favorited`) in `public/styles.css` giving a distinct border AND an icon/label change (not color alone) — toggle this class based on `state.favoritedIndex`
  - [ ] Ensure the favorite toggle button has an accessible name/state (e.g. `aria-pressed`) reflecting favorited status
- [ ] Task 4: Reset favorite on new generation (AC: 8)
  - [ ] Confirm the Task 1 synchronous reset (`state.favoritedIndex = null` before fetch) also visibly clears the highlight from any previously-rendered card
- [ ] Task 5: Tests (`node --test`)
  - [ ] DOM-level test(s) (using `node:test` + a minimal DOM shim already used by existing tests, or by exercising the exported render/state functions) covering: state object initialized correctly; prompt input updates `state.prompt`; `Generate ideas` clears `ideas`/`favoritedIndex` before fetch; favorite toggle sets/moves/unsets `favoritedIndex`; new generation resets favorite highlight
  - [ ] Confirm no regression in existing story 1 tests (`npm test`)

## Dev Notes

- Architecture constraints in force: AD-3 (client-side, session-only state — no persistence), AD-4 (`favoritedIndex: number | null`, single-select, click-to-deselect). AD-1/AD-2/AD-5/AD-6 (server/adapter contract) are unaffected — this story only touches `public/app.js` and `public/styles.css`.
- This is a brownfield change to `public/app.js`, which currently manipulates the DOM directly (`promptInput`, `results.innerHTML`, etc.) with no central state object — introducing `state` is the AD-3 decision, not a refactor of unrelated code.
- The favorite highlight must not be color-only (NFR4) — pair the CSS border/background change with an icon or text label change (e.g. `☆`/`★` or "Favorite"/"Favorited") and `aria-pressed`.
- Testing standard: `node --test` only, per `.ai-context.md`. `public/app.js` currently has no dedicated test file; check `test/` for any existing DOM-testing pattern before inventing a new one.

### Files Being Modified — Current State & Required Changes

**`public/app.js` (UPDATE, not new)** — current state: DOM-driven, no state object; renders `payload.ideas` directly into `results.innerHTML` with no favorite affordance.
- What this story changes: introduce `state`, render from `state.ideas`, add favorite-toggle buttons and their click handling.
- What must be preserved: existing prompt validation, in-flight button disabling, error/status text handling, `escapeHtml` usage for all rendered idea text.

**`public/styles.css` (UPDATE, not new)** — current state: `.card` has a plain border, no favorited variant.
- What this story changes: add a `.card.favorited` (or similar) rule providing a non-color-only distinction.

**`server.js` / `lib/ideaService.js` (no change expected)** — this story is entirely client-side; the `/api/ideas` contract from Story 1.1 is unchanged.

### References

- [Source: epics.md#Story 2.1] — client-side state object acceptance criteria
- [Source: epics.md#Story 2.2] — favorite toggle acceptance criteria
- [Source: ARCHITECTURE-SPINE.md#AD-3] — client-side session-only state
- [Source: ARCHITECTURE-SPINE.md#AD-4] — `favoritedIndex` state machine
- [Source: prd.md#FR2] — favorite toggle requirement
- [Source: .ai-context-idea-generation.md] — module boundaries, state machine, do-not-do rules

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-08-14: Story file created (mirrors epics.md Stories 2.1 + 2.2 under sprint-status.yaml key `1-2-favorite-an-idea-card`).
