# Reconciliation: PRD + Addendum → Architecture Spine

**Source (PRD v1):** `_bmad-output/planning-artifacts/prds/prd-ACME-2026-08-14/prd.md`
**Source (Addendum):** `_bmad-output/planning-artifacts/prds/prd-ACME-2026-08-14/addendum.md`
**Downstream:** `_bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md`
**Date:** 2026-08-14

## Method

Checked all six FRs, the fail-open NFR, the error taxonomy, and the addendum's
explicit "architecture cost" callout against the spine's ADs, Consistency
Conventions, Capability Map, and Deferred section.

## Findings

### Gap 1 — AD-3 silently redefines "fail open" against the addendum's own reference implementation (CONTRADICTION)

- **PRD (§5.2, FR-6 NFR):** "Screening fails open... matching this repo's
  existing `.claude/hooks/prompt_gateway_check.py` precedent."
- **Addendum ("Fail-open behavior"):** "The existing hook treats
  `result: 'unreachable'` or `'http_error'` as a **pass-through with a
  warning**." I.e., the reference implementation the PRD explicitly binds
  itself to does not fail open silently — it surfaces something to the user,
  behaviorally closer to `FLAG` than to a silent `ALLOW`.
- **Spine (AD-3):** "`lib/promptGatewayClient.js` catches unreachable/timeout
  internally (8s bound) and returns an **`ALLOW`-equivalent** result...
  `server.js` never sees a thrown error." Per FR-4's own consequence, `ALLOW`
  means "proceeds... with **no user-visible change**."
- **Gap:** AD-3 collapses "PromptGateway unreachable" into `ALLOW`, which is
  explicitly silent, contradicting the addendum's description of the precedent
  it says to copy ("pass-through **with a warning**"). The spine adopts the
  8-second timeout bound correctly (addendum matched verbatim in AD-3 and the
  Consistency Conventions table), but drops the warning half of the precedent
  it cites as authority. A story built strictly from AD-3 will not show the
  agent any indication that screening was skipped — silently contradicting
  both the cited hook behavior and SM-C2's spirit ("do not let fail-open
  behavior go unmentioned... a real, disclosed trade-off, not a gap to
  hide"). This should either be fixed (fail-open returns a `FLAG`-equivalent
  with a visible "screening unavailable" warning, not `ALLOW`-equivalent) or
  the deviation from the cited precedent should be explicitly justified.

### Gap 2 — AD-5's 400 status for "empty Ticket Text" is unreachable per FR-1, and the spine doesn't say so (CONTRADICTION)

- **PRD (FR-1 consequence):** "Submitting empty Ticket Text is **rejected
  client-side without a network call**." No HTTP request is ever made for
  this case.
- **Spine (AD-5):** "Input-validation failures (**empty** or over-length
  Ticket Text) map to `400`."
- **Gap:** If empty input never produces a network call (FR-1), there is no
  request for the server to return a 400 against — the empty-input branch of
  AD-5 describes a server-side error path that FR-1 says cannot occur. The
  spine never reconciles this: it doesn't say whether (a) client-side
  rejection is the *only* enforcement and the "empty" half of AD-5's 400
  mapping is dead/defense-in-depth-only, or (b) the server independently
  re-validates non-emptiness (contradicting "without a network call" only in
  the case where JS is bypassed) and that's a deliberate defense-in-depth
  choice. Left as written, AD-5 asserts server-side behavior for a case FR-1
  says never reaches the server — a story implementer has no way to resolve
  the contradiction without guessing. (The over-length half of AD-5's 400
  mapping is not contradicted by anything in the PRD and is fine as-is.)

### Gap 3 — Addendum's "architecture cost, stated plainly" ask is implemented but never actually answered in prose

- **Addendum:** Names PromptGateway as "a new cross-process dependency
  (FastAPI/Python service) inside what was otherwise a Node-core-only,
  framework-free app," calls the tension "real," and explicitly asks that
  architecture "explicitly decide how to handle" it and "flag this to
  Winston at architecture time rather than let it be inherited silently."
- **Spine:** AD-2 picks native `fetch` with no new npm dependency, and the
  Stack table notes PromptGateway as "existing in-repo FastAPI service...
  not versioned by this spine, a sibling service." This is a real decision
  and it's a reasonable one — but the spine never states the trade-off in
  prose the way the addendum asked for. Nowhere does the spine say something
  like "this app remains framework-free at the Node layer; the cross-process/
  cross-language dependency on a separate Python service is accepted because
  X" — it just implements the low-friction option (fetch, no library) without
  narrating that this *is* the cost/benefit call the addendum flagged.
  Functionally the decision is fine; procedurally, the addendum's explicit
  ask ("stated plainly," "rather than let it be inherited silently") is not
  satisfied — a reviewer checking "was this tension actually litigated" would
  find only an implicit answer, not a stated one.

### Gap 4 — AD-4 covers only half of FR-2's testable consequences (partial coverage, not a table-only appearance)

- **PRD (FR-2 consequences):** Four testable consequences — Category enum,
  Priority enum, Summary is a single sentence, **Draft Reply is non-empty
  when the triage call succeeds**.
- **Spine (AD-4, "Triage output validation"):** Only governs Category (→
  `other` on parse failure/out-of-enum) and Priority (→ "a defined safe
  default"). Summary and Draft Reply are not mentioned by AD-4 or any other
  AD.
- **Gap:** FR-2 appears fully governed in the Capability Map ("Governed by:
  AD-4"), but AD-4's actual rule text only constrains two of its four
  consequences. There is no invariant anywhere in the spine that would catch
  a triage adapter returning an empty Draft Reply or a multi-sentence
  Summary — this is silently unaddressed rather than deferred explicitly.

## Non-findings (checked, no gap)

- All six FRs (FR-1–FR-6) do appear in both the Capability Map and at least
  one AD's `Binds` list — table appearance is backed by actual AD text for
  FR-1, FR-3, FR-4, FR-5, FR-6 (FR-2 is partial — see Gap 4).
- The 8-second PromptGateway timeout bound from the addendum is carried into
  AD-3 and the Consistency Conventions table correctly (the 15s subprocess
  ceiling is correctly *not* carried over, matching the addendum's note that
  it's an internal margin, not a bound the caller should rely on).
- PRD Open Questions 1, 6, 7 (fail-closed hardening, "light editing" bound,
  non-English input) are all explicitly carried into the spine's Deferred
  section rather than silently dropped.
- Non-Goals (§6) — accounts, persistence, real ticketing integration,
  caching, retries/circuit-breaking — are all respected by AD-6 and the
  Stack/Structural Seed; no silent drop found.
