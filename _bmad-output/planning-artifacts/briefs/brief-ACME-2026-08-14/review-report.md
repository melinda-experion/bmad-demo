---
title: Review — Support Ticket Triage Brief
date: 2026-08-14
brief_version: 1
---

# Brief Review: Support Ticket Triage

## Summary Assessment

No critical findings that would sink the brief outright, but three of the five
dimensions need work before this is stakeholder-ready: the problem statement
never lands on a specific pain, one of the two success-criteria groups isn't
measurable, and the target-user section names two "Primary" personas without
resolving which one governs a design conflict. Demo-process success criteria
(lines 75–83) are a genuine strength — concrete, binary, and defensible — and
the brief's own honesty about being a demo vehicle rather than a real product
(Executive Summary) heads off a differentiation attack before it starts.

## 1. Problem Statement Clarity

**Moderate.** The Problem section (lines 40–48) states the pain is
illustrative and unvalidated up front — that's honest, not the issue. The
issue is that the pain itself is generic: "manually read each one, decide
what kind of issue it is, judge how urgent it is" and "context-switching per
ticket" could describe triage in any domain — code review, restaurant
orders, insurance claims. Nothing in the section is specific to support
tickets. No volume ("how many tickets"), no time cost ("how much time per
ticket"), no named consequence of the stated inconsistency (does a
miscategorized ticket breach an SLA? get routed to the wrong team? just
annoy someone?). A skeptical stakeholder's first question — "why does this
matter, concretely?" — has no answer here, only an assertion that it does.

## 2. Defensibility of Stated Goals

**Split finding.** Demo-process success (lines 75–83) is clean: every bullet
is binary and observable — a gate either refuses a bare "yes" or it
doesn't, a file either gets a logged confidence score or it doesn't. No
finding here.

**Moderate**, product-fiction success (lines 85–89): both bullets use
unmeasurable qualifiers. "Plausible for the four listed categories on
reasonably clear ticket text" — "plausible" and "reasonably clear" are not
defined, and no test set or accuracy threshold is named. "Usable with light
editing, not a non-sequitur" has the same problem — "usable" and "light" are
undefined. Asked "how would we know if we failed at this," the brief has no
answer for either bullet as written.

## 3. Hidden or Unstated Assumptions

**Moderate.** Four assumptions the brief needs but never states:

- **Latency.** "Who This Serves" (line 63) promises "a usable triage in
  seconds," while Scope (lines 96–97) forbids caching or memoization —
  every submission is a fresh LLM call. The brief never states a latency
  target or what happens if the call is slow or times out.
- **Category exhaustiveness.** Four fixed categories are named throughout
  (bug / billing / feature-request / question) with no fallback for a
  ticket that fits none of them.
- **Input handling.** No stated bound on ticket-text length, language, or
  malformed/empty input.
- **Content screening.** Ticket text may contain customer PII, and this
  repo already runs a prompt-screening service (PromptGateway) for
  exactly this class of risk — the brief never says whether triage
  submissions pass through it or any equivalent check before reaching the
  LLM. Given the repo's own governance apparatus exists specifically for
  this, its absence here is conspicuous rather than incidental.

## 4. Scope-Creep Risk

**Minor.** The Scope section (lines 91–106) is otherwise disciplined — an
explicit in/out list with the deferred favorite/save step named rather than
silently dropped. Two soft edges:

- The Solution section's closing clause — "an agent can act on elsewhere"
  (line 56) — doesn't say whether "acting elsewhere" is pure manual
  copy-paste or implies some export/handoff mechanism. Left unresolved,
  this is the kind of phrase a PRD quietly expands into an integration.
- "Light editing" (line 89, also flagged under Dimension 2) is undefined
  as a bound — without a cap, it's available as license to build a
  full editing UI that the rest of the brief never scopes for.

## 5. Gaps in Target-User Definition

**Moderate.** "Who This Serves" (lines 58–69) names two personas and labels
both **Primary** — the support agent and "the customer watching the demo."
Dimension 5's own test is whether two readers would picture the same
person; with two co-equal "Primary" labels, two readers would reasonably
disagree about which one actually governs a design trade-off when the two
pull in different directions (e.g., a UI choice that helps the illustrative
agent but adds nothing for the demo audience, or vice versa). At minimum
one should be Primary and the other Secondary, or the brief should state
explicitly that they don't compete.

Separately, the support-agent persona itself (line 60) is named only as
"a generic customer-support agent" — no industry, ticket volume, or tooling
context. Two readers would not picture the same agent. The brief flags this
persona as demo-only and illustrative, which is a legitimate reason to
leave it thin, but the thinness is still a gap this dimension is built to
catch — being intentional doesn't make it stop being a gap.
