# Adversarial Review — ARCHITECTURE-SPINE.md (architecture-BMAD-2026-07-30)

**Method:** for each finding, two units (Dev A / Dev B) each implement strictly to the letter of every AD, yet produce incompatible or divergently-behaving systems. Ranked by severity.

---

## Critical

### C-1. Duplicate/unassigned ownership of the "exactly 3, never pad/truncate/fabricate" invariant
AD-5 states the success response "must have exactly 3 entries"; AD-6 *separately* states the adapter resolves to exactly 3 entries and "must throw on this — never pad, truncate, or fabricate entries to force conformance." The anti-fabrication rule's **Binds** line is AD-6 (adapter only) — it never binds the handler.
- **Dev A**: trusts the adapter completely; handler passes the resolved array straight into `{ ideas }`.
- **Dev B**: defensively re-validates in `server.js` (paranoid about a buggy/future adapter) and silently `slice(0,3)`s or pads a 4th malformed entry to "fail safe" instead of 500ing.
Both are AD-6-compliant (Dev B never touches the adapter), yet Dev B's system silently violates the very invariant AD-6 exists to protect, in a place the spine forgot to also bind. **No AD assigns the handler responsibility to relay/enforce this rather than re-decide it.**
→ Close with: an explicit AD binding the handler to pass the adapter's array through unmodified (or reject via its own throw path) — never re-validate/normalize.

### C-2. Handler-level timeout race defeats AD-5's own "no double-dispatch" claim
AD-5 lists "double-dispatched LLM calls from independent client+server timeouts" under **Prevents**, and AD-6 gives the adapter sole ownership of the `AbortController`. But nothing in AD-6 *forbids* the handler from adding its own defense-in-depth timer around the adapter call (e.g. `Promise.race([adapterCall, timeoutPromise])`), since that binds "the handler," not "the adapter."
- **Dev A**: handler simply `await`s `generateIdeas()` and lets the adapter's internal 25s abort be the only timeout.
- **Dev B**: handler *also* wraps the call in its own 24s race "to be safe," per a literal reading of AD-5's stated intent.
If Dev B's race fires, the handler responds `504` to the client while the adapter's in-flight fetch to the LLM provider is **not aborted** (it doesn't share the handler's timer/signal) — the exact double-dispatch scenario AD-5 claims is prevented, produced by a fully AD-6-compliant adapter plus a fully AD-5-motivated handler.
→ Close with: an AD stating the handler must not implement any timeout/abort logic of its own; the adapter's throw is the only timeout signal, full stop.

---

## High

### H-1. "Well-formed `{title, description}`" is never defined
AD-6 requires the adapter to throw `MALFORMED` when output "didn't parse into exactly 3 well-formed `{title, description}` entries," but "well-formed" is undefined: are empty strings acceptable? Is trimming required? Are extra keys tolerated? Max length?
- **Dev A** treats any string (including `""`) as well-formed, so a degenerate LLM response (`{title:"", description:"..."}`) passes through as `200`.
- **Dev B** requires non-empty, trimmed strings, so the identical LLM output throws `MALFORMED` → `500`.
Identical provider output, identical AD compliance, divergent client-visible behavior — a shared e2e test suite cannot be written against "the spine" because the spine under-specifies the contract both builders are honoring.
→ Close with: an explicit validation predicate (non-empty after trim, max length, no extra/missing keys) as part of AD-5 or AD-6.

### H-2. Env-var read timing is unconstrained, splitting behavior under key rotation and tests
AD-2 only requires the key be "read from a server-side environment variable inside that adapter" — it doesn't say *when* (module load vs. per-call).
- **Dev A** reads `process.env.IDEA_LLM_API_KEY` once at module top-level (cached in a const at `require` time).
- **Dev B** reads it inside the exported function body on every call.
Both are "inside the adapter." But under `node --test` (spec-mandated runner), test files that set `process.env` before invoking `generateIdeas` will pass against Dev B and silently use a stale/undefined key against Dev A depending on require-cache order — a flaky, build-dependent test outcome the spine doesn't rule out. In production, Dev A also never picks up a rotated key without a process restart; Dev B does.
→ Close with: mandate per-call (not module-scope-cached) env read inside the exported function.

---

## Medium

### M-1. No standardized `error` string content — only the envelope shape is fixed
AD-5 fixes `{ error: string }` and the status code per failure class, but never constrains the *content* of `error`. Two fully compliant backends can return `{error:"Request timed out"}` and `{error:"TIMEOUT"}` for the same `504` — both satisfy the letter of AD-5. Any downstream story/test that asserts on `error` text (very plausible given AD-6 names literal `.code` tokens `'TIMEOUT'|'NETWORK'|'MALFORMED'`) will pass against one build and fail against the other, and the client's "always preserve typed prompt on error" behavior is untested against message content divergence.
→ Close with: pin the `error` string vocabulary (e.g., require it equal the `.code` token, or a fixed message table keyed by code).

### M-2. No request-body size bound — AD-1 + AD-5 leave an availability gap open to two divergent implementations
AD-5's `400` triggers only after the body is parsed as JSON and `prompt.length` is checked; AD-1 mandates raw Node `http` with no framework (so body parsing is hand-rolled). Nothing bounds total body size before parsing.
- **Dev A** buffers the full incoming body unconditionally before `JSON.parse`, so an oversized payload (e.g., 200MB of irrelevant JSON plus a valid short `prompt`) is fully read into memory before any check fires.
- **Dev B** adds an early byte-count guard and rejects oversized bodies before parsing.
Both comply with every AD; only one is resilient to a large-payload DoS. This is a case where an AD's own **Prevents** framing ("the response shape drifting," "double-dispatched calls") never claims to cover resource exhaustion, so the gap survives full compliance.
→ Close with: an explicit max request body size (e.g., matching or slightly above the 2000-char prompt bound) enforced before JSON parsing.

### M-3. Undefined handler behavior for a thrown error missing/outside the `.code` enum
AD-6 says thrown errors "carry a `.code` property — one of `'TIMEOUT' | 'NETWORK' | 'MALFORMED'`" but doesn't require *all* adapter throw sites to set it, nor define the handler's behavior if `.code` is absent or unrecognized (e.g., a raw `TypeError` bubbling from a bug, or a future adapter provider library throwing its own error shape).
- **Dev A**'s handler defaults unknown/missing `.code` to `502`.
- **Dev B**'s handler defaults to `500`.
Both read AD-6 literally (it only specifies the mapping for the three named codes) and diverge on the unspecified fallback — silently producing different status codes for the same underlying bug class.
→ Close with: an explicit default/fallback status (and require the mapping table itself, not just the code enum, to live in the spine rather than be inferred from prose order).

---

## Verdict
The spine is coherent on the "happy path" and on paper looks fully deterministic, but **6 findings** show that its Rules bind specific artifacts (the adapter, the handler) narrowly enough that two fully-compliant builders diverge on: invariant ownership (C-1), timeout/abort authority (C-2), validation semantics (H-1), env-read timing (H-2), error-message content (M-1), and unbounded-input handling (M-2), plus an unspecified error-code fallback (M-3). None of these are addressed by restating existing AD text — each needs a new Rule or a tightened one.
