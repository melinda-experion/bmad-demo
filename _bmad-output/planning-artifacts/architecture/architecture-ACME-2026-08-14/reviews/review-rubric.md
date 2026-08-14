---
title: Review — ARCHITECTURE-SPINE.md (rubric)
target: architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md
reviewer: rubric-checklist pass
created: '2026-08-14'
---

# Rubric Review — Support Ticket Triage Architecture Spine

**Verdict: NEEDS REVISION.** The spine is well-scoped for its 5-file
Coaching-path build, and its `Deferred` section is genuinely reasoned
(deployment/environments, non-English text, fail-open hardening, and
"light editing" all trace to an explicit precedent or a named PRD Open
Question — none of those are findings here, per the review brief). But
one real, undecided dimension the spine itself owns is left completely
silent — not decided, not deferred, not raised as an open question — and
a second operational detail is silently wrong-by-omission against the
actual PromptGateway service. Findings below.

## Findings

### 1. [High] Triage LLM provider/config is a fully silent dimension
`lib/triageService.js` is this spine's own module (Structural Seed, AD-4),
yet nothing in the Stack table, Deferred, or Open Questions names: which
LLM provider/model triage uses, whether an SDK dependency is added (this
would silently break AD-1/AD-2's "no new dependency, native `fetch`"
spirit, which is only made explicit for the PromptGateway adapter), how
an API key is configured (env var naming), or what timeout bounds the
call. AD-5's error taxonomy even names `TIMEOUT:504` for "triage-adapter
failures" — implying a timeout exists — without ever stating the bound
(contrast AD-3's explicit 8s for the PromptGateway call). Two stories
implementing `triageService.js` independently could diverge on provider,
dependency choice, and timeout value with nothing in the spine to
prevent it. This is exactly the kind of silent-dimension gap the rubric
flags, and unlike the deployment deferral it has no reasoning trail at
all.

### 2. [Medium] AD-2 omits PromptGateway's API-key gate
Verified against `PromptGateway/app.py:115-121` and
`PromptGateway/models/schemas.py`: the `/api/v1/validate` endpoint and its
`{decision, reason, categories_triggered}` response fields are accurately
named in AD-2 — that part of "named tech" checks out. But the route is
also gated by `dependencies=[Depends(verify_api_key)]`
(`PromptGateway/app.py:119`), active whenever
`settings.require_api_key` is `True` (`PromptGateway/config.py:55`,
default `False`). The spine says nothing about sending an API key, unlike
the real precedent it otherwise cites approvingly
(`.claude/hooks/prompt_gateway_check.py`, which explicitly resolves and
forwards `api_key`). Low risk while the default stays off, but it's an
unaddressed operational dimension, and a 401/403 from a future
`require_api_key=True` config isn't covered by AD-3 (which only defines
`unreachable`, not an auth failure) or AD-5 (scoped to triage-adapter
failures, not the PromptGateway adapter).

### 3. [Low] AD-5's `TIMEOUT:504` for the triage call is not self-enforcing
As noted in Finding 1: the Rule names an error code for a condition
(triage-call timeout) whose trigger value is never defined anywhere in
the spine, so it can't be independently enforced by two implementers the
same way AD-3's PromptGateway timeout can.

## What holds up

- AD-1 through AD-4 and AD-6 are enforceable and each maps to a concrete,
  real divergence risk (framework creep, adapter cross-calls, fail-open
  ownership, raw-LLM-output leakage, persistence/caching creep).
- All 6 FRs are bound and appear in the Capability → Architecture Map;
  FR-2's Summary/Draft-Reply scoping-out of AD-4 is explicitly reasoned,
  not silent.
- `Deferred` entries are each traced to a named precedent or PRD Open
  Question (OQ1, OQ6, OQ7) — correctly not re-litigated here per the
  review brief's instruction not to flag reasoned deferrals.
- Node.js `>=22`, native `fetch`, and `node --test` are current,
  real, dependency-free choices consistent with the stated paradigm.
- The PRD/spine divergence on the `unreachable` third outcome is called
  out by the spine itself, with a stated remediation path — not a silent
  gap.
