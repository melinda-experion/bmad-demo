# Adversarial Re-Validation — ARCHITECTURE-SPINE.md (2026-07-29)

## Verdict

PASS WITH NOTES — the seven previously-found gaps are genuinely closed, but two new interoperability gaps survive at the handler/adapter boundary and the client request-lifecycle boundary that would still let two AD-compliant implementations diverge incompatibly.

## Findings

### [MEDIUM] No pinned error taxonomy linking adapter throws to AD-5's status codes

AD-6 pins that the adapter signals failure "only by throwing" and that "the handler's single try/catch is the sole error path." AD-5 pins that the codes returned must be one of `504` (timeout), `502` (provider/network failure), or `500` (malformed output), with the adapter required to "throw on this" for malformed output. Nothing in AD-5 or AD-6 pins **what property or type the thrown error carries** that lets a single `catch` block distinguish these three cases.

Construct two units that each obey AD-6 to the letter:
- **Adapter A** uses the native `fetch`+`AbortController`; on abort it re-throws the native `AbortError` (`err.name === 'AbortError'`), on network failure lets the native `TypeError` propagate, and on malformed output throws `new Error('bad shape')`.
- **Adapter B** uses `axios` (or `https` directly); on abort/timeout it throws an `AxiosError` with `err.code === 'ECONNABORTED'`, on network failure `err.code === 'ECONNREFUSED'`/`ENOTFOUND`, and on malformed output throws a custom `class ValidationError extends Error`.

A handler written against Adapter A's discriminator (`err.name === 'AbortError'` → 504, `err instanceof TypeError` → 502, else 500) is silently wrong when paired with Adapter B (misclassifies every failure as 500), and vice versa. Both adapters are fully AD-6 compliant (correct export name, signature, resolve shape, throw-only failure signaling); both handlers are fully AD-5 compliant in the codes they *intend* to emit — yet the pairing produces wrong status codes for two of the three error classes. This is precisely the "unpinned status codes" gap the prior review raised, reopened one layer down: the codes are pinned, but the routing logic that selects among them is not.

**Suggested close:** pin either (a) a required error shape, e.g. the adapter must throw `Error` instances tagged with a fixed `err.code` drawn from an enumerated set (`'TIMEOUT' | 'PROVIDER_ERROR' | 'MALFORMED_OUTPUT'`), or (b) that the adapter itself is responsible for mapping to the numeric status and the handler trusts a status pinned on the error object.

### [MEDIUM] Concurrent/in-flight request handling is not pinned, reopening the "stale response" risk AD-3 claims to close

AD-3's prevents-clause explicitly lists "a stale prior request's state rendering against a newer one," but the rule text only pins one moment: state is cleared **synchronously before the fetch is dispatched** on submit. It says nothing about what happens if a second submit occurs while a first request is still in flight (rapid double-click on Generate, or edit-and-resubmit before the first response lands).

Construct two `app.js` units that each obey AD-3 and AD-4 to the letter:
- **Unit A** disables the Generate button (or ignores subsequent submits) while a request is pending, so only one fetch is ever in flight.
- **Unit B** leaves the button live; each submit clears state and dispatches a fresh fetch per AD-3's letter, with no request-identity check on resolution.

Under Unit B, if a user submits prompt P1 then quickly edits to P2 and resubmits, and the P1 response arrives after the P2 response (plausible — LLM latency is variable), Unit B will render P1's ideas over P2's already-rendered ideas — the exact stale-over-fresh scenario AD-3 says it prevents. Nothing in the current AD text requires disabling the input during a pending request or tagging requests with an id/generation counter so late responses can be discarded. Both units are AD-3/AD-4 compliant to the letter; only one actually delivers the guarantee AD-3's own prose promises.

**Suggested close:** add a rule requiring either (a) the submit control be disabled/no-op while a request is pending, or (b) each dispatched request carry a generation token compared against `state` on resolution, discarding stale responses.

### [LOW] Timeout ownership (adapter vs. handler) is inferable but not stated

AD-5 pins the timeout mechanism as "`AbortController` on the provider call fixed at 25s," and AD-6 fixes the adapter's signature to `(prompt: string) => Promise<...>` with no `signal` parameter — which by elimination means the `AbortController` must live inside `lib/ideaService.js`, not `server.js`. That inference is sound but never stated as a rule. A builder who reads AD-5 in isolation could instead implement the 25s timeout in the handler via `Promise.race`, satisfying "server-side... fixed at 25s... always resolving 504 before any client-side timeout" in prose, while never constructing an `AbortController` on the actual outbound provider request — leaving that request running in the background after the handler has already responded 504. This doesn't break the wire contract (client still gets a pinned 504), so severity is low, but it's a real residual ambiguity about where AD-6's fixed signature forces the timeout to live, and it's worth stating explicitly rather than leaving it to inference.

**Suggested close:** one added sentence — "The `AbortController` is constructed and owned inside `generateIdeas`; the handler has no signal to pass and only awaits/catches."
