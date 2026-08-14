# Story 1.3: Submit–Screen–Triage Endpoint and Result UI

As a Triaging Agent,
I want a single screen where I paste a ticket and see its triage result (or a screening warning/refusal),
So that I can act on a ticket without leaving the app or guessing what happened.

**Acceptance Criteria:**

**Given** the single-screen UI
**When** I paste ticket text under 2000 characters and submit
**Then** the request is screened first, triaged only if not `BLOCK`ed, and the result (category/priority/summary/draft reply) displays (FR1, FR4, AD-1)

**Given** I submit empty ticket text
**When** I click submit
**Then** it's rejected client-side with no network call (FR1)

**Given** I submit ticket text over 2000 characters
**When** it reaches the server
**Then** it's rejected with HTTP `400` (AD-5)

**Given** screening returns `FLAG` or `UNREACHABLE`
**When** the result displays
**Then** a visible warning appears alongside the triage result (FR5)

**Given** screening returns `BLOCK`
**When** I submit
**Then** no triage call happens, I see a plain refusal message asking me to remove sensitive content, the response is HTTP `403`, and the raw flagged content is never echoed back (FR6, AD-5)

**Given** a triage-adapter failure (timeout, network, malformed response)
**When** it occurs
**Then** the response uses the AD-5 taxonomy (`TIMEOUT:504`/`NETWORK:502`/`MALFORMED:500`) with the `{"error": "<message>"}` envelope

**And** nothing persists past a page reload, no accounts (NFR4)
