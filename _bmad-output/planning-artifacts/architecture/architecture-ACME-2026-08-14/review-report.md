---
title: Architecture Spine Review — Support Ticket Triage
architecture_version: 1
date: 2026-08-14
---

# Architecture Spine Review: Support Ticket Triage

## Overall verdict

**Strong**, after two fix passes. Deterministic lint clean (0 findings)
on both passes. A first Finalize-mode pass (rubric walker + web/reality
version-check + adversarial incompatible-builders lens, all as parallel
subagents) found 6 real issues — 2 critical, 2 high, 2 medium — all fixed.
A second, fresh re-check of the fixed spine (triggered by this approval
flow's own currency check, which found no `review-report.md` on record)
found 2 more real issues the first fix pass had missed — a timeout
overclaim and an incompletely-closed AD-4/AD-5 boundary gap — both fixed.
One additional claim from the first pass ("the prior demo app precedent
has no corresponding code anywhere in this repo") was independently
verified and rejected as false: `server.js` is committed at `5fdbb69`
and `8e9bc31`, recoverable via `git show HEAD:server.js`, only deleted
(uncommitted) in the working tree as part of this session's greenfield
reset.

## Findings, round 1 (fixed)

- **Critical** — `UNREACHABLE`/fail-open outcome had no defined shape and
  contradicted the Consistency Conventions table's closed 3-value
  `Screening Decision` enum. *Fixed:* enum extended to 4 values
  (`ALLOW`/`FLAG`/`BLOCK`/`UNREACHABLE`), consistently in AD-2, AD-3, and
  the Conventions table.
- **High** — AD-4 (silent defaulting) and AD-5 (`MALFORMED:500`) gave no
  boundary for a fully-garbled triage response. *Fixed* (see round 2 —
  the first attempt at this fix was incomplete).
- **High** — AD-4's Priority "safe default" was required but never named.
  *Fixed:* named as `medium`.
- **Medium** — Success-response envelope was entirely unspecified.
  *Fixed:* `{"category", "priority", "summary", "draftReply",
  "screeningWarning"}` added to AD-5 and the Conventions table.
- **Medium** — No HTTP status fixed for a `BLOCK` refusal. *Fixed:*
  mapped to `403`.
- **High** (rubric walker) — Triage LLM provider/SDK/timeout was a fully
  silent dimension. *Fixed:* explicit `Deferred` entry naming why
  (PRD is deliberately provider-agnostic) and what happens when a
  provider is chosen.
- **Medium** (rubric walker) — PromptGateway's optional `X-API-Key` gating
  wasn't addressed. *Fixed:* AD-2 now notes the passthrough convention.
- **Low** — Node 22 presented as unqualified "current" when it's
  Maintenance LTS (24 is Active). *Fixed:* Stack table now states both.

## Findings, round 2 (fixed)

- **High** — Round 1's AD-3 timeout fix (8s → 20s) claimed to "clear
  PromptGateway's worst case with margin," but that worst case is
  actually ~30s (15s timeout × `max_retries: 1`, verified directly
  against `PromptGateway/policy.yaml` and `validators/llm_validator.py`),
  not 15s. *Fixed:* AD-3 now states 20s as a UX bound, not a worst-case
  guarantee, and explains why that's an acceptable trade-off (a timeout
  fires into `UNREACHABLE` → `FLAG`-equivalent, a graceful degradation,
  not a hard failure).
- **High** — Round 1's AD-4 fix ("fails to parse at all" vs. "parses with
  an out-of-enum value") left "parses as structured data" undefined,
  so a response with a missing or wrong-typed field could be routed
  either way by two independently-built stories. *Fixed:* AD-4 now
  defines the schema check precisely — valid JSON with all four required
  string keys — before either branch applies.
- **Low** — `UNREACHABLE`'s `reason`/`categories_triggered` fields were
  unspecified (risk of `null` vs. a real value across two
  implementations). *Fixed:* both fields are now always populated with
  fixed values.

## Mechanical notes

- Reviewed against the good-spine checklist (real divergence points
  covered; every AD's Rule enforceable; nothing under Deferred admits
  silent divergence; named tech verified-current; PRD's FR-1–FR-6 all
  covered; every dimension the feature altitude owns is decided, deferred,
  or an open question — including the operational envelope, which is
  explicitly deferred with reasoning, not silently skipped).
- Per-lens scratch files from round 1 remain at `reviews/review-*.md` for
  reference; this file is the canonical, currency-checked artifact.
