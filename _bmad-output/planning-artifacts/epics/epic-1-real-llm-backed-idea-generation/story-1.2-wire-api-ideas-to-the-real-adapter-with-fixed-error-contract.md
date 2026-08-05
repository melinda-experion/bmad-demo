# Story 1.2: Wire /api/ideas to the Real Adapter with Fixed Error Contract

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
