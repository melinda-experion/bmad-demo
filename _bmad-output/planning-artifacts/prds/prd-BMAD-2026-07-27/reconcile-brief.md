---
title: Brief-to-PRD Reconciliation
input_brief: brief-BMAD-2026-07-27 (v2, approved)
input_prd: prd-BMAD-2026-07-27
created: 2026-07-27
---

# Reconciliation: Brief v2 vs PRD

## Gaps Found

### 1. BMAD Learning Angle mapping is incomplete
The brief names five BMAD skills as the explicit point of the exercise: `bmad-brainstorming`, `bmad-ux`, `bmad-architecture`, `bmad-create-story`, `bmad-help`. The PRD only carries forward two of them — `bmad-brainstorming` (UJ-1, SM-2) and `bmad-ux` (deferred "Next step" hint, §7.2). `bmad-architecture`, `bmad-create-story`, and `bmad-help` are never mentioned anywhere in the PRD, even though the brief frames the whole project as a walk through all five skills. A reader of the PRD alone would not know this artifact is meant to be followed by an architecture pass, a story-creation pass, and a help/next-steps pass.

### 2. Vision's forward-looking ("next version") ideas are dropped
The brief's Vision section lists three concrete post-MVP directions: guided idea categories aligned to BMAD phases, a tiny workflow helper showing next BMAD steps, and export of the favorite idea into a brief or story. None of these appear in the PRD. The PRD's own §2 "Vision" section only restates the MVP description (prompt → three cards) — it isn't actually a vision statement, just a rephrased solution summary. There is no post-MVP/future-direction section anywhere in the PRD, so this content has no home.

### 3. "No backend" scope constraint is quietly overridden without full reconciliation
The brief explicitly lists "Backend API integration" under Out of Scope, consistent with its "single-screen experiment," "front-end flow," 1-2 hour framing. The PRD's entire idea-generation mechanism (FR-2, Glossary "Idea Generation Service") assumes a server-side LLM proxy — a real backend. The PRD does flag this as an `[ASSUMPTION]` and raises it as Open Question #2 ("does this still fit inside a 1-2 hour build?"), so it isn't silently smuggled in, but the tension is never resolved — the PRD proceeds to spec the backend-dependent flow as the primary path rather than treating it as a blocking decision for the PM/builder to settle first.

### 4. Differentiators lose their positive framing
The brief's "What makes this different" section frames smallness and narrow scope as the deliberate differentiators ("delivers a complete, usable idea flow in a very small scope, rather than a large product"; "frames itself as an experimentation launcher rather than a full idea management app"). The PRD folds the second bullet into §6 Non-Goals (what the app is *not*), but never states the first bullet's positive claim — that intentionally shipping a complete, small thing is itself the differentiating design choice, not just an exclusion list. The "why smallness is good" framing is lost in translation to "here is what's excluded."

## Not Flagged as Gaps
- Tone/spirit of "fast, low-ceremony, 1-2 hour learning exercise" is well preserved — repeated in §1 Document Purpose, §2 Vision, §3.1 JTBD, and SM-2.
- Success criteria (30-second generation, single-session build, launch point for brainstorm → define → build) are faithfully carried into SM-1 and SM-2.
- In-scope/out-of-scope feature lists (cards, favorite toggle, responsive layout, localStorage as optional enhancement) match closely between brief and PRD.
