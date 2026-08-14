# Reconciliation: Brief vs. PRD — Support Ticket Triage

**Source input (approved brief):** `_bmad-output/planning-artifacts/briefs/brief-ACME-2026-08-14/brief.md` (v1, approved)
**Downstream:** `_bmad-output/planning-artifacts/prds/prd-ACME-2026-08-14/prd.md` + `addendum.md`
**Date:** 2026-08-14

## Method

Read both documents in full. Compared section-by-section for content that the
brief states, implies, or emphasizes but that the PRD silently drops,
contradicts, or flattens — with particular attention to qualitative/tonal
content (a rigid FR structure tends to lose framing, motivation, and
forward-looking intent even when it preserves literal facts).

Two known, explicitly-logged PRD decisions were excluded from consideration
per instructions:
1. PRD adds a new Content Screening feature (PromptGateway) not in the
   brief's original scope — logged in PRD §5.2, Assumptions Index #2-3,5-6,
   and addendum.md.
2. PRD resolves the brief's two-"Primary"-persona ambiguity by making the
   support agent the sole formal Target User — logged in PRD §1, Assumptions
   Index #1, and addendum.md's "On the two 'Primary' personas" section.

## Gaps Found

### 1. The brief's "reusable demo harness" framing is dropped entirely

The brief's Executive Summary carries a forward-looking, explicitly-flagged
assumption: this product isn't just a demo vehicle for *this* run — it sets
up the repo to become **"a reusable demo harness where the specific product
idea can be swapped for a future demo without changing the chain
underneath it"** (brief lines 35-37, `[ASSUMPTION]`). This is architecturally
consequential: it implies the PRD (and downstream architecture) should care
about keeping product-specific logic decoupled from the generic
governance-chain machinery, since the same chain is meant to outlive this
specific app.

The PRD's Vision (§2) and Document Purpose (§1) both restate "the product
has no real differentiation, it's a vehicle for the demo" — but neither
mentions the harness-reuse angle at all, not even to flag it out of scope
for this PRD run. Unlike the two-Primary-persona resolution (which got an
explicit addendum section explaining the disposition of the dropped
framing), the harness framing has no equivalent acknowledgment anywhere in
the PRD or addendum. It reads as silently dropped rather than considered
and set aside.

**Why it matters:** Architecture is the next consumer of this PRD, and the
addendum already flags one real architecture tension (PromptGateway as a
new cross-process dependency). Whether the app's PromptGateway integration
should be built in a way that's easy to swap out for a future harness reuse
is exactly the kind of question that tension should be evaluated against —
and the PRD gives the architect no signal that this consideration exists.

### 2. The Problem section's "inconsistency across agents" motivation is flattened to individual efficiency only

The brief's Problem section names two distinct costs of manual triage:
**time** ("context-switching per ticket") and **inconsistency** ("two
agents categorize or prioritize the same kind of ticket differently") —
brief lines 44-49. Both are given roughly equal weight as the problem's
justification.

The PRD's Jobs To Be Done (§3.1) carries the time-savings motivation
forward almost verbatim ("so I don't have to read it twice before deciding
what to do with it," "so my first response goes out faster") but the
cross-agent consistency motivation has no corresponding JTBD, FR rationale,
or success metric anywhere in the PRD. FR-2's fixed Category/Priority
enums *incidentally* support consistency (since a fixed vocabulary is more
consistent than free text), but the PRD never states this as a reason for
the design, and SM-5/SM-6 measure categorization accuracy against a single
human reviewer, not consistency across multiple triagers. The brief's
second pillar of motivation is present in effect but absent in stated
rationale — a flattening rather than a full drop, but the qualitative
"inconsistency across agents" framing itself doesn't survive into the PRD.

### 3. "One API call per submission" is carried forward as if still literally true, without caveat for the PRD's own added screening call

The brief's Scope section states plainly: **"One API call per submission;
no caching, no memoization — every submit is a fresh LLM call"** (brief
lines 97-98), and the Executive Summary echoes it: "one input, one LLM
call, one result" (line 21).

PRD §5.1 repeats this almost verbatim: "One API call per submission; no
caching or memoization, so every submission is a genuinely fresh LLM call
(carried from the brief...)" — but by this point in the same document, §5.2
has already introduced a *second* call per submission (the PromptGateway
screening call, FR-4). The PRD never reconciles this: it doesn't say "one
LLM call" (screening isn't an LLM call, so the letter of the brief's intent
may still hold), but it also doesn't clarify that the "one API call"
language it's directly reusing is no longer accurate once screening is
counted. This isn't the Content Screening feature addition itself (which
is out of scope for this review per instructions) — it's the PRD's
uncritical reuse of the brief's exact scope language in a context where
that language now needs a caveat it doesn't get. A reader skimming §5.1
alone could reasonably believe submissions still involve exactly one
network call.

## Non-Gaps (checked, found adequately carried forward)

For completeness, the following brief content *was* checked and found
adequately represented in the PRD, despite restructuring:

- Two-yardstick Success Criteria structure (demo-process vs.
  product-fiction) — carried forward near-verbatim in PRD §8.
- "Illustrative, not validated against a real support team" framing for
  the Problem section — carried forward and even strengthened as a
  Non-Goal (§6) and counter-metric caveat (SM-C1).
- Deferred favorite/save-triage step and its rationale — carried forward
  in PRD §6, §7.2, and addendum.md.
- "Seconds" latency framing downgraded to "aspirational, not a committed
  target" — explicitly flagged as an assumption in PRD §5.1's NFR, not a
  silent drop.
- Shared architectural shape with the prior demo app (Node core `http`,
  vanilla JS, no framework, no persistence) — referenced in PRD §5.1 and
  addressed directly in addendum.md's "Architecture cost, stated plainly"
  section.
- Explicit scope exclusions (ticketing integration, accounts/auth,
  multi-turn conversation) — carried forward verbatim into PRD §6 Non-Goals.
