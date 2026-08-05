# Story 1.1: Real LLM Provider Call in the Idea Adapter

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
