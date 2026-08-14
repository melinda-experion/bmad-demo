# Addendum: Support Ticket Triage PRD

Technical-how and downstream-relevant depth that doesn't belong in a
capability-level PRD. Not audit content — see `.memlog.md` for the
decision trail.

## PromptGateway integration contract (for architecture)

### Contract shape

PromptGateway exposes `POST /api/v1/validate` (FastAPI, `app.py`), taking
`{"prompt": "<text>"}` and returning a decision object:

```json
{
  "decision": "ALLOW" | "FLAG" | "BLOCK",
  "risk_score": <float>,
  "reason": "<string>",
  "categories_triggered": ["..."],
  "sanitized_prompt": "<PII-redacted text>",
  "validator_results": [...]
}
```

For FR-4/FR-5/FR-6, the app should call this endpoint with the raw Ticket
Text and branch on `decision` exactly the way
`.claude/hooks/prompt_gateway_check.py` already does for chat prompts:
`BLOCK` → refuse, `FLAG` → proceed with `reason`/`categories_triggered`
surfaced as a warning, `ALLOW` → proceed silently. That hook is the
existing, working reference implementation for this exact branching logic
— architecture should point at it rather than re-deriving the pattern.

### Fail-open behavior

The existing hook treats `result: "unreachable"` or `"http_error"` as a
pass-through with a warning. It uses an 8-second timeout on the gateway
call itself (`--timeout 8`, the user-facing bound), backed by a 15-second
ceiling at the subprocess layer (`timeout=15`, an internal safety margin
above the 8s call — not a second bound the caller should rely on). Support
Ticket Triage's screening call should use the same 8-second bound — this
is a synchronous step in front of a user-facing submit action, not a
background check, so it cannot silently hang for longer than that.

### Architecture cost, stated plainly

This is a new cross-process dependency (FastAPI/Python service) inside
what was otherwise a Node-core-only, framework-free app (matching the
prior demo app's AD-1). That tension is real and worth having
architecture explicitly decide how to handle — a direct HTTP call from
`server.js` is the obvious default, but it's not free of the "no
framework" spirit the way a pure-Node dependency would be. Flag this to
Winston at architecture time rather than let it be inherited silently.

## Input-length precedent

The prior demo app (`server.js`) defined `MAX_PROMPT_LENGTH = 2000` as a
plain constant, not derived from any measured constraint. FR-6's 2000-char
Ticket Text cap reuses that exact precedent for consistency across the two
demo apps built from this repo, not because 2000 is independently
justified for support-ticket text specifically.

## Carried from the brief's addendum

### Favorite/save-triage step

Still deferred, not rejected — same reason as the brief: v1 was kept to
one epic (~3 files) to fit the runbook's ~45-minute demo budget. If epic 2
becomes real (to show epic-to-epic sprint planning, or a second dev/review
pass — the brief's named triggers), it mirrors the prior app's client-side
favorite-toggle pattern (no persistence, no backend change) and would let
an agent star a Triage Result within the current session only — consistent
with §6's Non-Goals until then.

### Persona guardrail

The brief's addendum names a specific trigger: if a future run of this
repo wants the support-agent persona to carry more real weight — e.g., a
customer specifically asks "would this actually work for our support
team" — that's a signal to re-run Discovery on the *brief*, not to let
this PRD (or a later architecture/stories pass) quietly upgrade an
illustrative persona into a researched one by accretion. This PRD's thin
§3.1 (Assumptions Index item 8) is downstream of that guardrail, not a
replacement for it.

## On the two "Primary" personas (brief resolution, PRD consequence)

The brief named both the support agent and "the customer watching the
demo" as Primary. This PRD resolved that by making the support agent the
sole formal Target User (Assumptions Index item 1) — but the demo-audience
framing isn't discarded, it's relocated to §1 Document Purpose as a reader
note. Downstream UX/architecture work should keep treating the demo
audience as *context for why this exists*, not as a persona whose needs
generate FRs. If a future run of this PRD needs to formally serve the demo
audience as a product user (e.g., an actual "audience view" per Open
Question 4), that's a scope change, not a UX nuance — revisit Discovery,
don't quietly grow FRs to cover it.
