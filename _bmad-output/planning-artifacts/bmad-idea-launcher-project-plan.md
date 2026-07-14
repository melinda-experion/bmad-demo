# BMAD Idea Launcher Project Plan

## Objective

Deliver the full MVP for BMAD Idea Launcher by implementing all three epics and proving the behavior through automated and manual validation. The work should stay lightweight, keep the experience on a single screen, and preserve the learning-artifact scope defined in the PRD.

## Scope Summary

### Epic 1 — Capture and Generate Starter Ideas

- Prompt entry and submission flow
- Generation request handling
- Exactly three idea cards rendered per submission
- Clear error feedback when generation fails

### Epic 2 — Save and Review Promising Ideas

- Favorite toggle interaction
- Visual favorite state
- Persistence of favorites in browser storage

### Epic 3 — Deliver a Lightweight Single-Screen Experience

- Single-screen flow for prompt, generation, and results
- Responsive layout for mobile and desktop
- Clear, readable presentation without extra navigation

## Delivery Approach

### Phase 1 — Foundation and Epic 1

Focus on the core flow first so the product can generate and display ideas end to end.

Tasks:

- Implement or stabilize the server endpoint for idea generation
- Validate prompt input and reject empty or whitespace-only submissions
- Normalize generation responses so the UI always receives exactly three cards
- Render cards with title and description
- Surface clear user-friendly error states
- Add automated tests for API behavior and UI rendering

Definition of done:

- A valid prompt returns exactly three ideas
- An empty prompt is rejected with a clear error
- The UI renders three cards after submission
- The user can retry after a failure without losing the prompt

### Phase 2 — Epic 2: Favorites and Persistence

Add lightweight interaction and persistence without introducing backend complexity.

Tasks:

- Add favorite toggle behavior to each idea card
- Show a clear visual favorite state
- Save favorite selections to browser storage
- Restore favorite state when the page reloads
- Add tests for persistence and toggle behavior

Definition of done:

- Multiple ideas can be favorited simultaneously
- Favorited cards stay marked after a refresh
- Favorite state is restored without a backend

### Phase 3 — Epic 3: Single-Screen Responsive Polish

Polish the experience so it feels lightweight, responsive, and easy to use.

Tasks:

- Keep the full flow on a single screen
- Refine layout for mobile and desktop
- Ensure controls remain visible and tappable at common widths
- Review accessibility and clarity for first-time users
- Perform responsive verification checks

Definition of done:

- Prompt, action, and results remain on one screen
- The interface is usable at mobile and desktop widths
- No core flow requires navigation or hidden steps

## Workstream Breakdown

### Backend

- Build and stabilize the POST /api/ideas endpoint
- Keep response and error handling simple and predictable
- Ensure the API contract returns exactly three ideas for successful requests

### Frontend

- Wire the prompt form to the backend
- Render idea cards from generation results
- Provide loading and error states
- Implement favorite interactions and storage hydration
- Keep the UI lightweight and single-screen

### Testing

- Add or extend automated tests for API success and failure paths
- Validate UI rendering behavior for generated cards
- Cover favorite toggle and persistence scenarios
- Add responsive/manual verification for mobile and desktop layouts

## Testing Strategy

### Automated Tests

- API contract tests for valid and invalid prompts
- UI behavior tests for generation and card rendering
- Storage-based tests for favorite persistence
- Regression tests for empty-state and error-state handling

### Manual Verification

- Verify the end-to-end flow from prompt entry to idea review
- Confirm the app remains usable at 375px, 768px, and 1920px widths
- Check that the prompt and error messages remain visible after failed requests

### Definition of Done for the Project

- All three epics are implemented
- All acceptance criteria from the epic breakdown are satisfied
- Automated tests pass
- The experience is usable on mobile and desktop without broken layout

## Milestones

### Milestone 1 — Core generation flow complete

- Epic 1 implemented and tested
- Basic server and UI integration verified

### Milestone 2 — Favorites complete

- Epic 2 implemented and tested
- Browser persistence verified

### Milestone 3 — Responsive MVP shipped

- Epic 3 implemented and validated
- End-to-end experience verified for common devices

## Risks and Mitigations

### Risk: LLM or generation response variability

Mitigation: Normalize responses so the UI always renders exactly three cards and handles short or long outputs safely.

### Risk: Scope creep beyond the MVP

Mitigation: Keep the implementation focused on prompt capture, idea generation, favorites, and responsive single-screen behavior only.

### Risk: Inconsistent behavior across devices

Mitigation: Test at multiple widths and ensure layout remains simple and readable.

## Verification Commands

Run the following from the project root:

- node --test
- node server.js

## Recommended Execution Order

1. Implement and test Epic 1
2. Implement and test Epic 2
3. Implement and test Epic 3
4. Run the full regression suite and review the end-to-end experience
