# Story 1.3: Show Clear Feedback When Generation Fails

As a learner,
I want the app to explain generation failures clearly,
So that I can recover quickly and retry without losing context.

**Acceptance Criteria:**

**Given** the generation request fails or returns an error
**When** the user is returned to the page
**Then** the app displays a short user-friendly error message
**And** the prompt remains intact so the user can try again
**And** the app does not leave the interface in a broken or silent state
