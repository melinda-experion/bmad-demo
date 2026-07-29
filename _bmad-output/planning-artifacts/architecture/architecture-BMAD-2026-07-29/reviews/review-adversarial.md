---
name: 'Adversarial Review — ARCHITECTURE-SPINE (BMAD Idea Launcher)'
type: review
target: '_bmad-output/planning-artifacts/architecture/architecture-BMAD-2026-07-29/ARCHITECTURE-SPINE.md'
created: '2026-07-29'
---

# Adversarial Review — ARCHITECTURE-SPINE

## Verdict

The spine correctly fixes *ownership* (who holds state, where the key lives, one endpoint) but leaves the *interior contracts* — the handler↔adapter function interface, the exact `/api/ideas` error taxonomy, timeout semantics, and the client-side state lifecycle across regenerate/error/favorite events — loose enough that two AD-1-through-AD-5-compliant builds will not interoperate or will diverge in observable behavior.

## Findings

### 1. [Critical] Handler↔Adapter function interface is never fixed

AD-2 only fixes *where* the adapter is called from (server-side, one function, key from `process.env`). It never fixes the adapter's exported name, signature, return shape, or error-signaling convention. The handler (`server.js`) and the adapter are, in effect, two independently-buildable units that must agree on an in-process contract the spine doesn't specify.

**Concrete incompatible pair:**
- Build A (`server.js` author): `const { generateIdeas } = require('./ideaService'); const ideas = await generateIdeas(prompt); // expects Array<{title,description}>, catches thrown Error -> 5xx`
- Build B (adapter author): `module.exports = async function getIdeas({ prompt, timeoutMs }) { return { ideas: [...], error: null }; }` — different export name, object-param signature, and returns an envelope with an `error` field instead of throwing.

Both obey AD-2 to the letter (server-side only, adapter reads key from env, no key leakage). The app does not run: `generateIdeas` is undefined, or if named identically the shapes still mismatch (array vs `{ideas, error}` envelope) and error handling silently breaks (a resolved envelope with `error` set never hits the handler's `catch`).

**Fix:** Add an AD (e.g. AD-6 — Handler/Adapter Interface) that pins: exported function name and file, parameter shape (`(prompt: string) => Promise<{title,description}[]>`), and the rule that adapter failures are always signaled by throwing (never by a resolved error envelope), so the handler's single `try/catch` is the only error path.

### 2. [High] AD-5's "5xx-class" leaves the exact status code unpinned

AD-5 says "a `5xx`-class response for provider failure or timeout" — not a specific code. Two servers can both satisfy the letter of AD-5 while returning different codes for the same failure class.

**Concrete incompatible pair:**
- Build A returns `502` for any provider-adapter throw (treating the LLM as an upstream dependency).
- Build B returns `500` for provider throws and `504` specifically for timeouts.

Any test suite or client branch logic written against one build's codes (e.g. `if (status === 504) showTimeoutMessage()`) silently fails against the other, even though both are spine-compliant.

**Fix:** Tighten AD-5 to pin exact codes: `400` invalid prompt, `504` provider timeout, `502` provider/network failure, `500` unexpected/malformed provider response. Client behavior may still be generic (per AD-5's "client always preserves prompt on any error"), but the server contract stops being ambiguous.

### 3. [High] No timeout value or enforcement point is specified

AD-5 references FR-2's "30s target" but that is a UX performance target, not a hard timeout contract. Nothing says whether the *server* aborts the provider call, whether the *client* aborts the fetch, or what duration either uses.

**Concrete incompatible pair:**
- Build A: server-side `AbortController` cancels the LLM call at 20s and returns `504`; client fetch has no timeout of its own.
- Build B: server never times out the provider call (awaits indefinitely); client's `fetch` uses a 30s `AbortController` and shows a generic error while the server keeps running the LLM request in the background.

Under Build B, a user's retry after the client-side abort can result in two concurrent LLM calls for the same prompt (cost/latency doubling), and the server never emits the `5xx` AD-5 promises for that request — it just never responds to the aborted socket. Under Build A the client never needs its own timeout at all. These are materially different systems both "obeying" AD-5.

**Fix:** Pin in AD-5 (or a new sub-rule): the *server* owns timeout enforcement via `AbortController` on the provider call at a fixed value (e.g. 25s), always resolving with a `504` before the client's own fetch would time out; the client does not need a redundant abort.

### 4. [High] Undefined behavior when the provider doesn't return exactly 3 ideas

AD-5 fixes the wire contract as "exactly 3 entries" but never says what the adapter/handler does when the LLM returns 2, 4, or a malformed payload.

**Concrete incompatible pair:**
- Build A: adapter validates the parsed LLM output; if `ideas.length !== 3`, throws, producing a `5xx` — strict, matches AD-5's wire shape by rejecting anything that doesn't already conform.
- Build B: adapter pads with a placeholder idea (`{title: "Idea", description: ""}`) or truncates extra entries to force `length === 3` — technically satisfies AD-5's wire shape on every response, but silently fabricates or discards LLM content.

Both builds produce spine-legal `200 { ideas: [...] }` (or `5xx`) responses, but one degrades silently with fake data while the other surfaces a retry-able error — a real product-behavior fork invisible to the AD as written.

**Fix:** Add a rule: any provider response that does not parse into exactly 3 well-formed `{title, description}` entries is treated as a provider failure (`5xx`) — the adapter must never pad, truncate, or fabricate entries to force conformance.

### 5. [Medium] Malformed JSON / bad Content-Type request bodies are unhandled by AD-5

AD-5's `400` case is scoped to "empty/invalid prompt" — it says nothing about a request body that isn't valid JSON at all, or lacks a `prompt` key, or sends `prompt` as a non-string. Since AD-1 bars any framework (no body-parser middleware), each handler implementation must hand-roll body parsing.

**Concrete incompatible pair:**
- Build A wraps `JSON.parse(body)` in try/catch and returns `400 { error: "invalid request body" }` on failure.
- Build B does not guard the parse; a malformed body throws inside the request handler, which (with no framework-level error boundary, per AD-1) either crashes the process or falls through Node's default unhandled-exception behavior — producing a hung connection or a bare `500` with no `{error}` body, breaking AD-5's own error envelope guarantee.

**Fix:** Extend AD-5 (or the Consistency Conventions error-shape row) to explicitly cover non-JSON / non-string-`prompt` bodies as another `400 { error }` case, and require the handler to wrap body parsing in a try/catch as a hard rule (not left to individual diligence given AD-1 forbids framework-level safety nets).

### 6. [Medium] `favoritedIndex` lifecycle across regenerate is unspecified

AD-3/AD-4 fix *ownership* and *shape* (`favoritedIndex: number | null`, client-only) but never state what happens to it when a new prompt is submitted and new ideas replace the old three.

**Concrete incompatible pair:**
- Build A resets `favoritedIndex` to `null` the moment a new `POST /api/ideas` is dispatched (before the response even returns).
- Build B leaves the previous `favoritedIndex` untouched until new ideas render, so between "Generate" click and response arrival (and if a stale response ever races an older request), a card index from the *previous* idea set stays visually marked as favorite against the *new* set.

Both comply with AD-3/AD-4 ("one index, client-owned") but produce different, user-visible state machines — one of which has a real dangling-reference/race bug class the other doesn't.

**Fix:** Add an explicit state-transition rule: submitting a new prompt synchronously clears `ideas` and resets `favoritedIndex` to `null` before the fetch is dispatched; a response for a superseded request (if any request-sequencing exists) must not resurrect a stale `favoritedIndex`.

### 7. [Medium] Ambiguous source of truth for prompt text between DOM and state object

AD-3 says prompt text "lives only in a single client-side state object in `app.js`," and AD-5 requires "the client always preserves the typed prompt on any error response" — but neither says whether the `<input>` element is a controlled view of `state.prompt` (two-way bound on every keystroke) or whether `state.prompt` is only populated at submit time and the DOM input is the real source of truth in between.

**Concrete incompatible pair:**
- Build A: `<input>` is controlled — every `oninput` writes `state.prompt`, and on error the render function re-populates the input from `state.prompt`.
- Build B: `state.prompt` is only set inside the submit handler right before the fetch call; on error, nothing re-writes the (already-still-full) DOM input — "preservation" happens because the browser never cleared it, not because `app.js` state drives it.

Functionally both "preserve the typed prompt" for a human clicking through the UI once. But Build B's `state.prompt` is stale/empty at all other times, so anything that inspects `state` directly (an automated UI test, a future feature reading `state.prompt` to prefill a share link, a code reviewer following AD-3 literally) sees a broken invariant in Build B while Build A's tests pass — two spine-compliant builds with incompatible internal data flow.

**Fix:** Tighten AD-3 to state the input is a controlled element bound to `state.prompt` on every change event, making `state.prompt` the always-current, single source of truth (not just at submit).

### 8. [Low] "Invalid prompt" is undefined beyond "empty"

AD-5 says `400` for "empty/invalid prompt" but never defines invalid: whitespace-only? Over some max length? Non-string JSON value (number/array/null)? Two servers can diverge at these edges (e.g., a whitespace-only prompt: Build A trims and 400s, Build B does not trim and forwards `"   "` to the LLM as a 200).

**Fix:** Add a precise validation rule to AD-5 or the Consistency Conventions: `prompt` must be a string, trimmed length > 0, and ≤ a fixed max (e.g. 2000 chars); anything else is `400`.

### 9. [Low] Favorite toggle behavior is unspecified

AD-4 fixes single-select ownership but not whether clicking an already-favorited card deselects it (`favoritedIndex -> null`) or is a no-op. Two `app.js` builds can differ here with no spine text to arbitrate either way.

**Fix:** Add one sentence to AD-4: "clicking the currently-favorited card toggles `favoritedIndex` back to `null`" (or explicitly the opposite), removing the free choice.
