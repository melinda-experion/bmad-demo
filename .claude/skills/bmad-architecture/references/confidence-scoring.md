# Confidence Scoring

Before Close, self-assess how much confidence a reader should place in this document as written — not how good the product idea is, how confident *you* feel, or how well-written the prose is. Confidence measures **evidentiary grounding**: how much of the document rests on confirmed input versus inference.

## What lowers confidence

- Unresolved `[ASSUMPTION]` tags remaining in the finished document.
- Open Questions left unanswered.
- Sections drafted from thin or absent user input (Fast path with heavy inference; sparse brain dump).
- Stakeholder or source material the user mentioned but never provided.
- Internal contradictions surfaced during review/reconciliation that were deferred rather than resolved.
- Domain areas the author flagged as uncertain, out of expertise, or unverified (e.g. unverified market claims, unconfirmed technical constraints).

## What raises confidence

- Every major claim traceable to something the user stated, a source document, or verified research.
- Assumptions were surfaced and confirmed with the user during the run, not just tagged and left.
- Coaching-path runs with real back-and-forth generally warrant higher confidence than Fast-path runs of comparable length.
- Reviewer/reconciliation passes ran clean, or their findings were resolved rather than deferred.

## Scoring

Produce three frontmatter fields:

- `confidence`: integer 0-100.
- `confidence_label`: `Low` (<50), `Medium` (50-79), `High` (80+) — derived mechanically from the number, never chosen independently.
- `confidence_rationale`: one to two sentences naming the specific factors that most moved the score — cite counts where useful ("3 unresolved [ASSUMPTION] tags in Success Criteria; no source material for competitive claims").

This is a self-assessment, not a computed metric — reason honestly about it the way you would caveat a claim to the user directly. A short, thin document built entirely from user-confirmed input can score High; a long, polished document built on heavy inference should not.
