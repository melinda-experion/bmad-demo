---
story: 1-2-favorite-an-idea-card
date: 2026-08-14
status: pending-approval
confidence: 82
confidence_label: High
confidence_rationale: All 8 acceptance criteria trace directly to approved epics.md Stories 2.1/2.2 and Architecture AD-3/AD-4; the only inference is the story-key mapping (confirmed with the user) and the exact favorite-toggle markup/icon, which is a UI-styling choice not pinned by any spec.
---

# Implementation Plan: Story 1.2 — Favorite an Idea Card

## Scope Summary

Add a client-side state object (`prompt`, `ideas`, `favoritedIndex`) to `public/app.js` and a single-select, non-color-only favorite toggle on each rendered idea card. Purely client-side; no server/adapter changes. Covers epics.md Stories 2.1 + 2.2 in one pass (per user confirmation).

## Impacted Modules & Files

- `public/app.js` — MODIFY: introduce `state` object, render idea cards from `state.ideas`, add favorite-toggle handling.
- `public/styles.css` — MODIFY: add a `.card.favorited` (or equivalent) rule for the non-color-only highlight.
- `test/` — ADD: new test file for the client-side state/render logic (exact filename TBD at test-writing time, e.g. `test/app.test.js`).
- No changes to `server.js`, `lib/ideaService.js`, or any other file.

## Detailed Design Approach

1. Refactor `public/app.js` around a single `state = { prompt: "", ideas: [], favoritedIndex: null }` object scoped at module level (page-lifetime only).
2. Prompt `<textarea>` `input` event updates `state.prompt` (in addition to existing behavior).
3. On `Generate ideas` click: synchronously set `state.ideas = []` and `state.favoritedIndex = null`, disable the button, *then* dispatch the fetch — preserving existing disable-on-in-flight behavior.
4. On success, set `state.ideas = payload.ideas` and call a `renderCards()` function that builds card markup from `state.ideas` and `state.favoritedIndex` (rather than rendering directly from `payload`).
5. Each card gets a favorite-toggle `<button>` with `aria-pressed` reflecting whether its index === `state.favoritedIndex`, and a label/icon that changes with state (e.g. `☆ Favorite` / `★ Favorited`) plus a `.favorited` class on the card.
6. Toggle click handler: if clicked index === current `favoritedIndex` → set to `null`; else → set to clicked index. Re-run `renderCards()` (or toggle classes directly) after every change.
7. `styles.css`: add `.card.favorited { border: 2px solid <accent>; }` plus ensure the label/icon change carries the non-color signal (so color removal/blindness still leaves an unambiguous cue).

## Data Model Usage

No server-side or persisted data model. Client-side `state` object only, held in a JS closure/module scope — never written to `localStorage`/`sessionStorage`/cookies, matching AD-3.

## API/Interface Changes

None. `/api/ideas` request/response contract is unchanged; this story only consumes the existing `{ ideas: [{title, description}] }` response shape.

## Error Handling & Edge Cases

- Rapid re-click of the same favorite toggle must cleanly toggle off (idempotent set/unset), not throw or double-highlight.
- Clicking a different card's toggle while one is already favorited must remove the old highlight before/at the same time as applying the new one — at most one favorited card at any instant.
- A new `Generate ideas` submission while a card is favorited must clear the highlight synchronously before the fetch is sent (AC8), independent of whether the fetch succeeds or fails.
- Existing error-path behavior (inline error, preserved prompt) is unaffected and must not regress — verified by existing tests, not re-implemented.

## Security Considerations

None new. No user input is newly rendered as HTML by this story (favorite icon/label is static, developer-authored text); existing `escapeHtml` usage for idea title/description is preserved unchanged.

## Performance Considerations

None material — DOM re-render of 3 cards on toggle is trivial; no debouncing or virtualization needed.

## Test Strategy

`node --test` only, per `.ai-context.md`.

- New test file exercising the state/render logic in isolation where feasible (e.g. by requiring `app.js`'s exported helpers, if refactored to export them, or via a minimal DOM shim consistent with any existing pattern in `test/`).
- Cases: initial state shape; prompt input updates `state.prompt`; `Generate ideas` clears `ideas`/`favoritedIndex` before fetch dispatch; favorite toggle set/unset/move across the 3 acceptance-criteria scenarios (AC5-7); new generation resets an existing favorite (AC8).
- Run full existing suite (`npm test`) to confirm no regression to Story 1.1's tests.

## Risks/Assumptions & Dependencies

- Assumption: `public/app.js` has no existing test file/export surface for its DOM logic — if no clean seam exists for unit-testing without a browser, may need a lightweight DOM stub (already implied usable per `.ai-context.md`'s testing convention, no new framework). Will inspect existing `test/story1.test.js` patterns before deciding exact test approach — no new test framework will be introduced regardless.
- Assumption: sprint-status.yaml's `1-2-favorite-an-idea-card` key covers both epics.md Stories 2.1 and 2.2 — explicitly confirmed with the user this session, not inferred silently.
- No new dependencies; no changes to `lib/ideaService.js` or `server.js`.

## Context Files Consulted

- `_bmad-output/planning-artifacts/epics.md` (Stories 2.1, 2.2)
- `_bmad-output/planning-artifacts/architecture/architecture-BMAD-2026-07-30/ARCHITECTURE-SPINE.md` (AD-3, AD-4, NFR4)
- `.ai-context.md`, `.ai-context-idea-generation.md`, `.ai-context-security.md`, `.ai-context-dependencies.md`
- `public/app.js`, `public/index.html`, `public/styles.css` (current state)
- `_bmad-output/implementation-artifacts/1-1-real-llm-backed-idea-generation.md` (sibling story precedent/format)

## Rationale Summary

The plan stays entirely within `public/` since both source stories (2.1, 2.2) are explicitly client-side-only per Architecture AD-3/AD-4, with no touch to the server/adapter layer completed in Story 1.1. Combining both stories into one implementation pass (per user's explicit choice) is safe because 2.2 (toggle UI) is additive on top of 2.1's state object with no conflicting design decisions between them.
