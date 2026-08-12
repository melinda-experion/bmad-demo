# Story 2.1: Client-Side State Object for Prompt, Ideas, and Favorite

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
