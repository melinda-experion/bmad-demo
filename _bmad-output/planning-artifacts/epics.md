---
stepsCompleted: ['extract-requirements', 'design-epics', 'create-stories']
inputDocuments: ['_bmad-output/planning-artifacts/prds/prd-ACME-2026-08-14/prd.md', '_bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md']
confidence: 90
confidence_label: High
confidence_rationale: Every FR/NFR traces directly to the approved PRD and architecture spine, not inference; requirements extraction, epic structure, and all 3 stories each got explicit user approval at their own gate. Docked slightly for one inherited, correctly-unresolved gap -- the triage LLM provider remains undecided (architecture's own Deferred item), so Story 1.1 will need a mid-implementation decision not pinned here.
---

# Support Ticket Triage - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Support
Ticket Triage, decomposing the requirements from the PRD and Architecture
Spine into implementable stories. Per team preference, each approved story
is also mirrored to `_bmad-output/planning-artifacts/epics/epic-{n}-{slug}/
story-{epic}.{story}-{slug}.md` for convenience — **this file remains the
single canonical document** that downstream steps (readiness-check,
sprint-planning, etc.) read.

## Requirements Inventory

### Functional Requirements

FR1: A Triaging Agent can submit Ticket Text (up to the 2000-char cap) for
triage via a single action; empty Ticket Text is rejected client-side with
no network call.

FR2: The system returns a structured Triage Result — Category (always one
of the fixed enum, never free text), Priority (always one of the fixed
enum), Summary (a single sentence), and Draft Reply (non-empty on success).

FR3: Ticket Text that doesn't clearly fit `bug`/`billing`/`feature-request`/
`question` is categorized `other` rather than forced into the nearest fixed
category.

FR4: Every triage submission is screened via PromptGateway before the
triage LLM call executes — no Ticket Text reaches the triage LLM without a
prior screening attempt.

FR5: A `FLAG` Screening Decision proceeds to the triage call, but the agent
sees a visible warning alongside the Triage Result.

FR6: A `BLOCK` Screening Decision prevents the triage call entirely; the
agent sees a plain message asking them to remove sensitive content and
resubmit, without echoing the raw flagged content back.

### NonFunctional Requirements

NFR1: No hard latency SLA in v1 — the triage LLM call is never cached or
memoized, so every screened submission is a fresh call.

NFR2: PromptGateway screening fails open — if PromptGateway is unreachable
or times out (20s bound), triage proceeds with a visible warning rather
than blocking the agent (Architecture AD-3).

NFR3: Ticket Text is capped at 2000 characters before screening or triage.

NFR4: All state is client-side and session-only — no database, session
store, accounts, or auth (Architecture AD-6).

### Additional Requirements

- **No starter template** — greenfield, no framework. Epic 1 Story 1 must
  scaffold the layered+adapter structure directly: `server.js` (HTTP layer
  only), `lib/promptGatewayClient.js`, `lib/triageService.js` (adapters),
  `public/` (client), `test/` (Architecture AD-1).
- `server.js` may not call PromptGateway or the triage LLM directly — only
  through their respective adapters, and adapters never call each other
  (AD-1, AD-2).
- PromptGateway integration: `POST /api/v1/validate`, native `fetch`, no
  new npm dependency; normalized `decision` is a closed 4-value set
  (`ALLOW`/`FLAG`/`BLOCK`/`UNREACHABLE`) — `UNREACHABLE` is this app's own
  addition, never returned by PromptGateway itself, and is treated the
  same as `FLAG` (AD-2, AD-3).
- Triage output validation: parse as structured data (valid JSON with
  `category`/`priority`/`summary`/`draftReply` string keys) before any
  enum check; a response that fails that check is `MALFORMED:500`, not a
  soft default; only a same-type-wrong-value enum mismatch resolves to
  `other`/`medium` (AD-4).
- Error/status taxonomy: `TIMEOUT:504`, `NETWORK:502`, `MALFORMED:500` for
  triage-adapter failures; `400` for over-length input; `403` for `BLOCK`;
  empty input never reaches the server at all. Error envelope
  `{"error": "<message>"}`; success envelope `{"category", "priority",
  "summary", "draftReply", "screeningWarning"}` (AD-5).
- Optional `X-API-Key` passthrough to PromptGateway if `REQUIRE_API_KEY`
  is enabled in a given deployment (AD-2) — not exercised by default.
- Deployment/CI/infra is explicitly out of scope (Architecture Deferred).
- Triage LLM provider is explicitly undecided (Architecture Deferred, PRD
  is deliberately provider-agnostic) — a story implementing FR2/FR3 must
  pick one and document the choice; it becomes a de facto decision, not a
  silent implementation detail.

### UX Design Requirements

Not applicable — no UX design contract exists for this run.

### FR Coverage Map

FR1: Epic 1 - Submit ticket text for triage
FR2: Epic 1 - Return a structured Triage Result
FR3: Epic 1 - Category fallback
FR4: Epic 1 - Screen submitted ticket text before triage
FR5: Epic 1 - Surface a screening FLAG without blocking
FR6: Epic 1 - Refuse triage on a screening BLOCK
NFR1-NFR4: Epic 1 - Enforced across all stories (no caching, fail-open, input cap, session-only state)

## Epic List

### Epic 1: Support Ticket Triage Core Flow
Paste a ticket, get a screened, structured triage — category, priority,
summary, and a draft reply an agent can act on. Covers the entire user
journey (UJ-1) end to end, including the PromptGateway screening step
that makes the flow safe to demo, not a separable add-on.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6

### Story 1.1: Triage Adapter — Structured Output With Validated Fallbacks

As a Triaging Agent,
I want the system to turn my raw ticket text into a validated Category, Priority, Summary, and Draft Reply,
So that I never see a broken or out-of-scope value in a triage result.

**Acceptance Criteria:**

**Given** ticket text describing a billing issue
**When** `lib/triageService.js` processes it
**Then** it returns `category="billing"` (one of the 5-value enum), a `priority` from the 3-value enum, a one-sentence summary, and a non-empty draft reply (FR2)

**Given** ticket text that doesn't clearly match bug/billing/feature-request/question
**When** processed
**Then** `category` resolves to `"other"` without erroring (FR3)

**Given** a triage LLM response that isn't valid structured data (invalid JSON, or a missing/wrong-typed key)
**When** processed
**Then** the adapter reports a `MALFORMED`-class failure rather than guessing a value (AD-4)

**Given** a triage LLM response with a `category` or `priority` value outside its enum (right type, wrong value)
**When** processed
**Then** they resolve to `other`/`medium` respectively — never the raw out-of-enum value (AD-4)

**And** two calls with identical input each invoke the LLM — no caching or memoization (NFR1)

### Story 1.2: PromptGateway Adapter — Screening With Fail-Open

As a Triaging Agent,
I want ticket text screened for PII/secrets before it reaches the triage LLM,
So that sensitive customer information doesn't leak to an LLM call I didn't intend to risk.

**Acceptance Criteria:**

**Given** ticket text
**When** `lib/promptGatewayClient.js` calls PromptGateway (`POST /api/v1/validate`)
**Then** it returns `decision` exactly as PromptGateway reported (`ALLOW`/`FLAG`/`BLOCK`), normalized into `{decision, reason, categories_triggered}` (FR4, AD-2)

**Given** PromptGateway is unreachable or exceeds the 20s timeout
**When** the call fails
**Then** the adapter catches it internally and returns `decision: "UNREACHABLE"` with `reason`/`categories_triggered` always populated (never throws, never `null`) (NFR2, AD-3)

**Given** PromptGateway's `REQUIRE_API_KEY` is enabled
**When** the adapter calls PromptGateway
**Then** it forwards `X-API-Key` (AD-2)

**And** no new npm HTTP client dependency is added — uses Node's native `fetch` (AD-2)

### Story 1.3: Submit–Screen–Triage Endpoint and Result UI

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
