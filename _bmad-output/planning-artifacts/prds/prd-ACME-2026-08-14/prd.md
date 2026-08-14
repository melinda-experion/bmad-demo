---
title: Support Ticket Triage
approval_status: review
created: 2026-08-14
updated: 2026-08-14
confidence: 71
confidence_label: Medium
confidence_rationale: Fast-path/Internal-stakes PRD with 8 unresolved [ASSUMPTION] tags and 7 deliberately-left-open Open Questions (none phase-blocking); however the one consequential fork (wiring PromptGateway into the runtime) was explicitly user-confirmed rather than inferred, and both input reconciliation (7/7 gaps found and fixed, not deferred) and the Reviewer Gate (4/4 findings fixed; rubric verdict strong on 5/7 dimensions, adequate on the remaining 2, no critical/high findings) ran clean.
---

# PRD: Support Ticket Triage

## 1. Document Purpose

This PRD is for whoever builds the architecture, epics, and stories that
follow it, and for anyone reviewing this repo's AI-governed SDLC as a
customer-facing demo. It builds on the approved product brief
(`_bmad-output/planning-artifacts/briefs/brief-ACME-2026-08-14/brief.md`,
v1) and does not restate its Executive Summary — read that first for why
this product exists. This document's job is narrower: turn the brief's
scope into globally-numbered, testable functional requirements.

**Reader note carried from the brief:** `[ASSUMPTION]` this product's
audience is two-layered, but only the support agent (§3) is a formal
Target User — the actual PRD reviewer is often a customer watching a
governed-SDLC demo, whose success criterion isn't about the triage tool
at all (see brief, "Who This Serves"; Assumptions Index item 1). The
brief's separate "reusable demo harness" framing (this repo as a vehicle
for swapping in a different product later) stays out of scope for this
PRD, which specs one product.

As the brief states plainly, the product itself has no real
differentiation. What makes this PRD non-trivial rather than a rubber
stamp is that Support Ticket Triage now does one real thing: it screens
submitted text through PromptGateway (this repo's own prompt-safety
service) before that text reaches the triage model — see §5.2. That's a
genuine functional requirement with real failure modes, not demo
dressing.

## 2. Vision

Support Ticket Triage is a single-screen micro app: paste raw customer
support ticket text into one field, submit it, and get back a structured
triage — category, priority, one-sentence summary, and a draft first-reply
— from one triage LLM call, preceded by a separate PromptGateway screening
call (§5.2). No accounts, no ticket queue, no persistence past the page
reload.

## 3. Target User

`[ASSUMPTION]` This persona stays intentionally thin — no industry, ticket
volume, or tooling context — inherited unchanged from the brief's explicit
"demo-only, not researched" framing rather than a gap introduced here; see
addendum.md for the guardrail on when that should change.

### 3.1 Jobs To Be Done

- As a support agent, I want to paste a raw ticket and immediately see what
  kind of issue it is and how urgent it is, so I don't have to read it
  twice before deciding what to do with it.
- As a support agent, I want a draft reply I can lightly edit rather than
  write from scratch, so my first response goes out faster.
- `[ASSUMPTION]` As a support agent, I want to trust that ticket text I
  paste — which may contain a customer's personal information — isn't
  sent to an LLM unscreened.
- As a support agent, I want my categorization of a ticket to match what a
  colleague would call it, so two agents don't triage the same kind of
  ticket differently.

### 3.2 Non-Users (v1)

- Support teams expecting real ticketing-system integration (Zendesk,
  Intercom, email) — there is none; this is a standalone triage step.
- Anyone needing multi-agent, multi-tenant, or audit-per-user tracking —
  there are no accounts.

### 3.3 Key User Journeys

Single-operator-role internal tool — lightweight shape per PRD scope dial.

- **UJ-1. An agent triages a ticket in one pass.** A support agent, mid
  queue, pastes a customer's raw ticket text into the single text area and
  submits. The app screens the text via PromptGateway; if it's clean, the
  triage call runs and returns category, priority, a one-line summary, and
  a draft reply. The agent reads the result, lightly edits the draft if
  needed, and copies it into whatever real channel they use — the app's
  job ends there. **Edge case:** if PromptGateway flags the text as
  containing likely PII or a secret (`BLOCK`), the agent sees a plain
  message asking them to remove the sensitive content and resubmit; no
  triage call happens. Realizes FR-1 through FR-6.

## 4. Glossary

- **Ticket Text** — the raw, pasted customer-support ticket content
  submitted for triage. Session-only; never persisted.
- **Triage Result** — the structured output of a triage submission:
  Category, Priority, Summary, Draft Reply.
- **Category** — one of a fixed set: `bug`, `billing`, `feature-request`,
  `question`, `other` (fallback for anything not fitting the first four).
- **Priority** — one of `low`, `medium`, `high`.
- **Draft Reply** — a single LLM-generated first-response draft, editable
  by the agent before use; never sent by the app itself.
- **Screening Decision** — PromptGateway's verdict on submitted Ticket
  Text: `ALLOW`, `FLAG`, or `BLOCK` (see PromptGateway's own contract;
  Support Ticket Triage consumes this verdict, it does not redefine it).
- **Triaging Agent** — the formal Target User: the person pasting ticket
  text and acting on the Triage Result. Used interchangeably with
  "support agent" in narrative text (§3, UJ-1) for readability — same
  entity, not a second persona. Distinct from the brief's "demo
  audience," which is not a Glossary term used elsewhere in this PRD.

## 5. Features

### 5.1 Ticket Triage

**Description:** The core loop — an agent pastes Ticket Text, submits it,
and receives a Triage Result. One triage LLM call per submission (a
separate PromptGateway screening call precedes it, §5.2); no caching or
memoization on the triage call, so every submission that passes screening
is a genuinely fresh LLM call (carried from the brief and the prior demo
app's architecture precedent). Realizes UJ-1.

#### FR-1: Submit ticket text for triage

A Triaging Agent can submit Ticket Text (up to the length cap in FR-6) for
triage via a single action.

**Consequences (testable):**
- Submitting non-empty Ticket Text under the length cap that passes
  screening (FR-4) triggers exactly one triage LLM call.
- Submitting empty Ticket Text is rejected client-side without a network
  call.

#### FR-2: Return a structured Triage Result

The system returns a Category, Priority, Summary, and Draft Reply for
screened Ticket Text.

**Consequences (testable):**
- Category is always one of the five fixed values (§4); never free text.
- Priority is always one of the three fixed values.
- Summary is a single sentence.
- Draft Reply is non-empty when the triage call succeeds.

**Out of Scope:** Multi-turn refinement of a Triage Result — one
submission, one result (see §6).

#### FR-3: Category fallback

`[ASSUMPTION — added to resolve a gap the brief's review-report flagged]`
Ticket Text that doesn't clearly fit `bug` / `billing` / `feature-request`
/ `question` is categorized `other` rather than forced into the nearest
fixed category.

**Consequences (testable):**
- No submission ever fails or errors solely because it doesn't fit the
  first four categories.
- Ticket Text that doesn't match `bug`/`billing`/`feature-request`/
  `question` deterministically returns `other` — verifiable against a
  held-out sample of ambiguous tickets (feeds SM-5).

**Feature-specific NFRs:**
- No hard latency SLA in v1. `[ASSUMPTION]` The brief's "seconds" framing
  is aspirational, not a committed target, since caching is explicitly
  forbidden (architecture precedent, brief §Scope). Deferred to §6.

### 5.2 Content Screening (PromptGateway)

**Description:** Before Ticket Text reaches the triage LLM call, it is
submitted to PromptGateway (this repo's own prompt-safety service) for a
policy check. This directly answers a gap the brief's review-report named
explicitly: ticket text may carry customer PII, and this repo already runs
a service built for exactly that risk — the brief never wired it in.
Realizes UJ-1's edge case.

#### FR-4: Screen submitted ticket text before triage

Every triage submission (FR-1) is screened via PromptGateway before the
triage LLM call executes.

**Consequences (testable):**
- No Ticket Text reaches the triage LLM call without a prior PromptGateway
  screening attempt.
- A screening `ALLOW` proceeds to the triage call with no user-visible
  change.

#### FR-5: Surface a screening `FLAG` without blocking

A `FLAG` Screening Decision proceeds to the triage call, but the agent
sees a visible warning alongside the eventual Triage Result.

**Consequences (testable):**
- A `FLAG`'d submission still produces a Triage Result.
- The warning is visible in the same result view, not a separate step the
  agent must seek out.

#### FR-6: Refuse triage on a screening `BLOCK`

A `BLOCK` Screening Decision prevents the triage call entirely; the agent
sees a plain message explaining the submission was blocked and asking
them to remove the sensitive content and resubmit.

**Consequences (testable):**
- A `BLOCK`'d submission produces zero triage LLM calls.
- The block message does not echo the raw flagged content back at all.

**Feature-specific NFRs:**
- `[ASSUMPTION]` Screening fails open: if PromptGateway is unreachable or
  errors, triage proceeds without screening rather than blocking the
  agent entirely, matching this repo's existing
  `.claude/hooks/prompt_gateway_check.py` precedent and its stated
  rationale (a screening outage shouldn't take down the whole feature).
  This is a v1 convenience trade-off, not a hardened security posture —
  see §6 Non-Goals.
- Ticket Text is capped at 2000 characters before screening or triage.
  `[ASSUMPTION]` — reuses the prior demo app's own `MAX_PROMPT_LENGTH`
  precedent rather than inventing a new limit.

## 6. Non-Goals (Explicit)

- Real ticketing-system integration of any kind (Zendesk, Intercom, email,
  or otherwise) — a Triage Result is read and acted on manually, outside
  this app.
- User accounts, authentication, or multi-tenant anything.
- Persistence of Ticket Text or Triage Results beyond the current page
  session.
- A saved/favorited-triage step. `[NOTE FOR PM]` Deferred, not rejected —
  see brief's addendum.md for the rationale; natural candidate for a
  second epic if the demo needs one.
- Multi-turn conversation or follow-up questions on a single ticket.
- Hardened PromptGateway failure handling (retries, fail-closed mode,
  circuit breaking) — v1 fails open only (§5.2).
- Any latency SLA or client-side request timeout.
- Evaluating triage accuracy against a real support team's judgment — see
  §8's counter-metric.

## 7. MVP Scope

### 7.1 In Scope

- Single screen: text area, submit action, result area (Category,
  Priority, Summary, Draft Reply, screening warning if `FLAG`'d).
- PromptGateway screening call ahead of every triage submission.
- One triage LLM call per submission, no caching.
- Session-only client state.

### 7.2 Out of Scope for MVP

See §6 Non-Goals for the full list — not restated here to avoid drift
between two lists that would otherwise say the same thing twice.

## 8. Success Metrics

Two separate yardsticks, kept explicit rather than blended — carried
directly from the brief's own structure; collapsing these into one list
would misrepresent what this repo is actually for. **Directive for
whoever writes epics/stories from this PRD:** acceptance criteria should
overwhelmingly target Primary/Demo-process metrics below, not Secondary/
Product-fiction ones — carried forward from the brief's addendum, restated
here because this is where a story author will actually be looking.

**Primary — Demo-process success** (what actually matters here)

- **SM-1**: Every gate in the brief→PRD→architecture→epics/stories→sprint→
  story chain executes and none is silently skippable. Validates the
  governance chain this PRD feeds, not any FR above.
- **SM-2**: The plan-first hard gate refuses a bare "yes"/"looks good" and
  requires the exact approval phrase before code generation starts.
- **SM-3**: Every generated file gets a deterministic, tool-measured
  confidence score (not a model self-assessment) logged to the project
  audit CSV.
- **SM-4**: Code review runs in a fresh session and performs diff-to-plan
  reconciliation, catching any file touched outside the approved plan.

**Secondary — Product-fiction success** (illustrative; not measured
against real users) `[ASSUMPTION]` — the brief left these qualitative
("plausible," "reasonably clear"); tightened here into something a demo
could actually check without a real evaluation program:

- **SM-5**: On a fixed set of 10 sample tickets spanning the five
  categories, at least 8 are categorized the way a human skimming the
  same ticket would categorize it. Validates FR-2, FR-3.
- **SM-6**: On the same set, the Draft Reply for each is judged usable
  with light editing (not a non-sequitur) by a single human reviewer —
  binary pass/fail per ticket, no rubric (see Open Question 6 on what
  "light editing" bounds). Validates FR-2.

**Counter-metrics (do not optimize)**

- **SM-C1**: Do not tune Category/Priority prompting against the 10-ticket
  sample until it scores perfectly — SM-5/SM-6 exist to catch a broken
  triage call, not to be gamed into 10/10 on a fixed, tiny, non-blind set.
  Counterbalances SM-5, SM-6.
- **SM-C2**: Do not let PromptGateway's fail-open behavior (§5.2) go
  unmentioned in the demo narrative to make SM-1 look cleaner than it is
  — a fail-open screening step is a real, disclosed trade-off, not a gap
  to hide. Counterbalances SM-1.

## 9. Open Questions

1. Should PromptGateway's fail-open behavior in v1 (§5.2) become
   fail-closed in a hardened future version, and if so, what should the
   agent see when triage is unavailable because screening is down?
2. Does the favorite/save-triage step become an actual epic 2, or stay
   permanently deferred? (Brief's addendum: natural candidate if a second
   epic is needed for the sprint-planning demo beat.)
3. Is there ever a real evaluation of SM-5/SM-6 planned beyond the 10
   sample tickets, or are they permanently illustrative-only?
4. Should the demo narrative include showing PromptGateway's audit log
   (`PromptGateway/logs/audit.db`) alongside the project's own audit CSV,
   given Support Ticket Triage now actually depends on it at runtime?
5. The brief's review-report flagged the Problem framing as generic (no
   ticket volume, no time cost, no named consequence of miscategorization)
   — this PRD did not sharpen it, since the brief's Problem section is
   explicitly illustrative by design (brief §The Problem). Left open
   rather than silently dropped: does that framing need real specificity
   before architecture/stories, or does "illustrative by design" cover it
   through to done?
6. "Light editing" (JTBD, SM-6) has no defined bound — carried unchanged
   from the brief, which the review-report also flagged. Does this need a
   concrete cap (e.g., "under N edited words") before SM-6 is checkable,
   or does a single human reviewer's binary judgment call suffice for a
   demo-only metric?
7. Non-English or malformed Ticket Text has no defined handling — FR-1
   only specifies empty-input rejection. Deferred rather than resolved;
   worth a call before architecture if the demo might use a non-English
   sample ticket.

## 10. Assumptions Index

1. §1 — The demo audience is not treated as a second product persona; only
   the support agent is a formal Target User.
2. §3.1 — Support agent JTBD includes a trust expectation about PII
   screening, inferred from the brief's review-report finding, not stated
   by the agent persona itself (which is explicitly illustrative/demo-only,
   per the brief).
3. §5.1 FR-3 — `other` category fallback added; not in the original brief.
4. §5.1 FR-3 NFR — No hard latency SLA in v1.
5. §5.2 FR-4-6 NFR — PromptGateway screening fails open in v1.
6. §5.2 FR-4-6 NFR — 2000-character Ticket Text cap, reused from the prior
   app's precedent.
7. §8 SM-5/SM-6 — Product-fiction success metrics tightened from the
   brief's qualitative language into a checkable (if very lightweight)
   10-sample-ticket measure.
8. §3.1 — The support-agent persona stays intentionally thin (no
   industry, ticket volume, or tooling context), inherited unchanged from
   the brief's explicit "demo-only, not researched" framing — not a new
   gap introduced by this PRD. See addendum.md for the brief's own
   guardrail on when that should change.
