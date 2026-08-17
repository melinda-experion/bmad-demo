# Addendum: Support Ticket Triage

Depth that belongs to downstream documents (PRD, architecture) or earned a
place in conversation but doesn't fit a 1-2 page brief. Not audit content —
see `.memlog.md` for the decision trail.

## Option considered and deferred: favorite/save-triage step

A client-side favorite/save-triage step (epic 2, mirroring the prior demo
app's favorite-toggle pattern) was considered for v1. **Deferred, not
rejected**, because v1 scope was chosen to keep the demo tight (one epic,
~3 files, matching the runbook's ~45-minute demo budget). If the demo
needs a second epic later — to show epic-to-epic sprint planning, or a
second dev/review pass — this is the natural candidate to reintroduce.

## Two audiences, held separately

For the PRD workflow: acceptance criteria for stories should overwhelmingly
target demo-process success (does the gate hold, does the plan-first check
refuse a bare "yes", does confidence scoring log correctly). The
triage-quality bar (product-fiction success) is real but secondary; a PRD
that inverts this priority optimizes the wrong thing for what this repo is
actually for.

## Persona note

The support-agent persona is explicitly demo-only (see brief's "Who This
Serves"). If a future run of this repo wants the persona to carry more
weight — e.g., a customer specifically asks "would this actually work for
our support team" — that's a signal to re-run Discovery on this brief
rather than let the PRD quietly upgrade an illustrative persona into a
researched one.
