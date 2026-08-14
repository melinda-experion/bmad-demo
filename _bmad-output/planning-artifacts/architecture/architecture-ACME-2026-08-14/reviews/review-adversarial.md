# Adversarial Review — Architecture Spine (Support Ticket Triage)

**Target:** `_bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md`
**Method:** for each hole below, two independent stories are constructed, each
implementing the spine and obeying every AD's literal text, that nonetheless
build incompatibly with each other. Holes are ranked by severity — how likely
two real story authors are to diverge, and how bad the resulting break is.

---

## Hole 1 (critical) — The "unreachable" result has no defined shape, and AD-2's shape has no room for it

AD-2 fixes the adapter's return contract as exactly `{decision, reason,
categories_triggered}`. AD-3 separately requires the adapter to return "a
distinct `unreachable` result — not `ALLOW`." Neither AD says which field
carries that distinction, and AD-2's shape is closed (three named fields,
nothing else). The named real-world precedent this spine claims to match
(`.claude/hooks/prompt_gateway_check.py`) actually uses a **fourth,
separate field** — `result: "unreachable"` — sitting alongside `decision`,
not inside it. The spine never says whether to follow that precedent or
stay inside AD-2's closed three-field shape.

- **Story A** (builds `lib/promptGatewayClient.js` for FR-4): reads AD-3's
  "distinct `unreachable` result" as extending the `decision` field's domain,
  and returns `{decision: "unreachable", reason: "...", categories_triggered: []}`.
  This satisfies AD-2's shape exactly (still three fields) and AD-3's "distinct
  ... not ALLOW" literally.
- **Story B** (builds FR-5's warning surfacing, working from the real
  `.claude/hooks/prompt_gateway_check.py` precedent AD-3 itself cites):
  returns `{decision: null, reason: "...", categories_triggered: [], reachable: false}`,
  keeping `decision` restricted to `ALLOW/FLAG/BLOCK` (matching the Consistency
  Conventions table's exact enum, see Hole 2) and signaling unreachability via
  a separate field, exactly like the precedent's `result` key.

`server.js`'s orchestration branch (`if (unreachable) → proceed + warn`) now
has two incompatible call sites to satisfy: `decision === "unreachable"` vs.
`reachable === false`. Whichever story's `server.js` code lands first, the
other adapter's output is silently misread — a Story-B adapter under a
Story-A server.js sees `decision: undefined`, falls through, and either
crashes or (worse) is coerced into the FLAG/ALLOW branch, defeating AD-3's
whole fail-open safety guarantee.

**Fix:** tighten AD-2 to spell out the *complete* return shape including the
reachability signal explicitly, e.g. `{decision: 'ALLOW'|'FLAG'|'BLOCK'|null,
reason, categories_triggered, reachable: boolean}`, and have AD-3 reference
that exact field name instead of the vague phrase "a distinct `unreachable`
result."

---

## Hole 2 (critical) — AD-3 contradicts the Consistency Conventions' Screening Decision enum

The Consistency Conventions table locks `Screening Decision` values to
exactly `ALLOW`, `FLAG`, `BLOCK` ("matches PromptGateway's own contract
verbatim — never re-cased"). AD-3 simultaneously mandates a "distinct
`unreachable` result" that is explicitly **not** `ALLOW`. If `unreachable`
is a `Screening Decision` value, the convention table is wrong (it's a
4-value enum, not 3); if it isn't, AD-3 never says where it lives (see Hole
1). This is a genuine self-contradiction in the spine, not just vague
wording — a story author who reads only the table concludes one thing, a
story author who reads only AD-3 concludes another.

- **Story A**: treats the Consistency Convention table as authoritative and
  hard-validates any `decision` value against the closed 3-value enum
  wherever it's consumed (e.g., in `public/app.js` rendering logic — `switch
  (decision) { case 'ALLOW': ...; case 'FLAG': ...; case 'BLOCK': ...;
  default: throw }`), because the table says "never re-cased" and implies
  closed.
- **Story B**: treats AD-3 as authoritative and adds a fourth case for
  `unreachable` in the same switch.

Story A's client throws/crashes (or silently drops into an unhandled
default) on exactly the case AD-3 exists to protect: an unreachable
PromptGateway. The two stories' `app.js` implementations are not just
different shapes — one actively breaks on input the other treats as
first-class.

**Fix:** either add `unreachable` (or `UNREACHABLE`) as a fourth, explicit
value in the Consistency Conventions' `Screening Decision` row, or restate
AD-3 to make clear the reachability signal is structurally outside the
`Screening Decision` enum (pairs with the Hole 1 fix).

---

## Hole 3 (high) — AD-4 and AD-5 disagree about what happens to a fully-garbled LLM response

AD-4: "Any parse failure or out-of-enum value resolves to `other`
(Category) or a defined safe default (Priority) — raw model text never
reaches the response as a field value." Read literally, *every* parse
failure — including a response that isn't parseable JSON at all — is
absorbed into a graceful default and the request still succeeds.

AD-5, in the very same document: "triage-adapter failures map to
`TIMEOUT:504`, `NETWORK:502`, `MALFORMED:500`." `MALFORMED:500` is
presented as a live, reachable HTTP outcome for triage-adapter failures —
but AD-4 has just said parse failures never surface as an error at all,
they get defaulted. Nothing in the spine says which class of "parse
failure" triggers AD-4's silent defaulting vs. AD-5's `MALFORMED:500`.

- **Story A** (implements `lib/triageService.js` for FR-2/FR-3, working
  strictly from AD-4): wraps LLM-response parsing in a try/catch that
  **always** resolves to `{category: 'other', priority: <default>, ...}`
  on any parse exception, and the endpoint always returns `200`. It never
  throws a `MALFORMED` error under any input, since AD-4 says raw failures
  "resolve to" a default, full stop.
- **Story B** (implements `server.js`/error handling for AD-5, working
  strictly from AD-5): wires a top-level catch in `server.js` around the
  triage adapter call that maps any thrown parse/format exception to
  `{"error": "..."} ` with HTTP `500` — because AD-5 explicitly promises
  callers a `MALFORMED:500` outcome exists.

Under Story B's server.js sitting on top of Story A's adapter, the
`MALFORMED:500` path is dead code — the adapter never throws, it always
defaults, so AD-5's documented 500 case can never actually be observed by
a client or a test written against it (a story per AD-5 writing a "returns
500 on malformed LLM output" test will fail against a Story-A adapter).
Conversely, a Story-A test asserting "malformed LLM output still returns
200 with category=other" fails against a Story-B server.js that intercepts
and 500s first.

**Fix:** scope AD-4's defaulting explicitly to *field-level* validation
failures (response parses as JSON but `Category`/`Priority` values are
missing/out-of-enum) and reserve `MALFORMED:500` in AD-5 explicitly for
*structural* parse failure (response isn't JSON / doesn't match the
envelope shape at all) — with a one-line rule stating that boundary.

---

## Hole 4 (high) — "a defined safe default (Priority)" never defines it

AD-4 requires Priority to resolve to "a defined safe default" on parse
failure but never states the value, and no other AD or the Consistency
Conventions table pins it (the table only lists the three legal values:
`low`, `medium`, `high`, without marking a default).

- **Story A** (`lib/triageService.js`, FR-3-adjacent reasoning): defaults
  to `priority: 'high'` — reasoning that an unparseable/uncertain triage
  result should fail toward urgent human attention rather than risk a
  slipped ticket.
- **Story B** (same file, written independently for the same AD):
  defaults to `priority: 'low'` — reasoning that an uncertain automated
  classification shouldn't inflate urgency and cause alert fatigue.

Both cite AD-4 verbatim as justification. Any downstream consumer/test
(e.g., a story building a priority-based inbox sort, or a QA test fixture
asserting "malformed LLM output → priority: X") built against one
implementation breaks against the other, and there's no AD text a reviewer
can point to that says either is wrong.

**Fix:** amend AD-4 to name the literal default value, e.g. "...or
`medium` (Priority's defined safe default)."

---

## Hole 5 (medium) — The success-response envelope is entirely unspecified

AD-5 pins the *error* envelope (`{"error": "<message>"}`) but the spine
never fixes a shape for a successful `POST /api/submit-triage` response —
not the Triage Result fields (Category/Priority/Summary/Draft Reply), not
key casing, not how/where the FR-5 FLAG-or-unreachable warning rides along
with a still-successful triage result.

- **Story A** (FR-1/FR-2, `server.js` + `public/app.js`): returns a flat,
  camelCase object — `{category, priority, summary, draftReply, warning}`
  — folding the screening warning into the same top-level object as the
  triage fields.
- **Story B** (FR-5, same endpoint, built independently): returns a
  nested shape — `{result: {Category, Priority, Summary, "Draft Reply"},
  screening: {decision, reason}}` — preserving the PRD's exact field
  capitalization (`Category`, `Priority`, as literally named in FR-2/FR-3)
  and keeping screening metadata segregated from triage output.

`public/app.js` written against one shape (`resp.warning`,
`resp.draftReply`) throws or silently renders `undefined` against the
other (`resp.screening.reason`, `resp.result["Draft Reply"]`). Since AD-4's
Category/Priority enum values are lowercase but the PRD's field *names*
(`Category`, `Priority`, `Draft Reply`) are capitalized with a space, both
stories can also point to different parts of the existing documents to
justify their casing choice — the spine adjudicates neither.

**Fix:** add a minimal AD (or extend AD-5) fixing the success envelope's
exact key names, nesting, and casing — mirroring the rigor already applied
to the error envelope and to the `Screening Decision`/`Category`/`Priority`
*value* casing in the Consistency Conventions table.

---

## Hole 6 (medium) — No HTTP status is fixed for a BLOCK refusal

AD-5's taxonomy covers triage-adapter failures (`TIMEOUT/NETWORK/MALFORMED`)
and over-length input (`400`), and separately states "PromptGateway/
screening failures never surface as an HTTP error to the client (AD-3)."
But a `BLOCK` decision (FR-6) is not a *failure* — it's a successful,
correct screening outcome that happens to refuse the request. AD-5 never
states what status code accompanies a refusal, and AD-3's "never surface as
an HTTP error" sentence is ambiguous about whether it's describing
failures only (leaving BLOCK's status open) or whether it's implicitly
claiming BLOCK also isn't an "HTTP error."

- **Story A** (FR-6, `server.js`): treats refusal as a well-formed,
  non-error outcome and returns `200` with a body like `{blocked: true,
  reason: "..."}`, reasoning that AD-5's error envelope/status taxonomy is
  scoped to failures and BLOCK is an intentional, successful decision.
- **Story B** (FR-6, independently): returns `403` with the AD-5 error
  envelope `{"error": "Request blocked by content screening: <reason>"}`,
  reasoning that "refuse on BLOCK" (FR-6's own title) is definitionally an
  HTTP-level refusal and should use a standard refusal status.

A client (or integration test) written against Story A's `200`+`blocked`
shape silently treats a genuine BLOCK as a normal success and renders the
refusal reason as if it were a Triage Result field; against Story B, the
same client's success-path code never runs at all for BLOCK and only the
generic error handler fires — materially different UX for the same
scenario, both compliant with every AD as literally written.

**Fix:** extend AD-5's taxonomy with an explicit BLOCK line, e.g. `BLOCK →
200 with {blocked: true, reason, categories_triggered}` (or a fixed 4xx —
pick one), so FR-6 has one unambiguous contract.

---

## Summary

**6 incompatible-pair holes found**, ranked critical → medium:

1. **Critical** — `unreachable` result has no defined field/shape; AD-2's
   closed 3-field contract has no room for it (contradicts the cited
   real-world precedent, which uses a 4th field).
2. **Critical** — AD-3's `unreachable` outcome directly contradicts the
   Consistency Conventions' closed 3-value `Screening Decision` enum.
3. **High** — AD-4 (silent defaulting) and AD-5 (`MALFORMED:500`) give
   two different, both-textually-valid outcomes for the same "garbled LLM
   response" case.
4. **High** — AD-4's Priority "defined safe default" is never actually
   defined anywhere in the spine.
5. **Medium** — success-response envelope (shape, nesting, casing) is
   entirely unspecified, unlike the rigorously-pinned error envelope.
6. **Medium** — no HTTP status is fixed for a BLOCK refusal; AD-5's
   "failures only" framing leaves FR-6's own outcome uncovered.

Every pair above independently satisfies each AD's literal text while
producing a `server.js`/`app.js`/adapter contract mismatch — evidence that
the spine's data-shape rules (AD-2, AD-4, AD-5) need field-level precision,
not just directional intent, before two stories can be built against it in
parallel.
