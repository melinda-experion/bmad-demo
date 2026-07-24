---
title: PRD Reconciliation — Brief v5 vs PRD v1
created: 2026-07-24
---

# Reconciliation: Brief (brief-BMAD-2026-07-23) vs PRD (prd-BMAD-2026-07-24)

Gaps below exclude the PRD's two explained, tagged resolutions (deferring the brief's "optional enhancements" to v1.1; the local-vs-LLM generation `[ASSUMPTION]`).

## 1. Competitive/contrast framing behind the minimalism is dropped
- **Brief location:** "The Problem" — "Existing idea generation tools can feel generic, overloaded, or too heavy for quick experimentation."
- **Gap:** This is the brief's stated *reason* the app should be minimal — it's answering a real pain point, not just hitting a build-time budget. The PRD's Vision section (§2) reframes the same constraint purely as a build-session sizing decision ("Everything about this PRD is sized to a 1-2 hour build"), losing the "why" (reacting against generic/overloaded tools) entirely.
- **Why it matters:** Without this framing, a future reader could reasonably add features that make the tool feel closer to a "real" idea-management product — the PRD gives no textual anchor explaining why that would be a regression.

## 2. Secondary user "developer wanting a minimal demo / concept validation" is dropped
- **Brief location:** "Who This Serves" → Secondary user, first bullet: "A developer who wants a minimal demo of idea generation and concept validation."
- **Gap:** PRD §3.1 Jobs To Be Done has three JTBDs (learner, builder, "someone showing this to another learner"). The "showing to another learner" JTBD covers the brief's *other* secondary user (BMAD practitioner using it for teaching), but the developer/concept-validation persona has no corresponding JTBD or mention anywhere in the PRD.
- **Why it matters:** This persona implies a slightly different quality bar (would this convince a developer the generation approach has legs?) that isn't represented in any requirement or success metric.

## 3. Explicit differentiation ("experimentation launcher, not idea management app") loses its framing
- **Brief location:** "The Solution" → "What makes this different" bullets.
- **Gap:** The brief frames the product's identity twice — as a deliberately small "usable idea flow" and specifically as an "experimentation launcher" rather than an "idea management app." The PRD's Non-Goals (§6, bullet 1) only carries forward the negative half ("not an idea management tool") and drops the positive identity claim ("experimentation launcher") that explains what it *is* rather than only what it isn't.
- **Why it matters:** Flattens a deliberate naming/positioning choice into a pure feature exclusion, losing the tone the brief was going for.

## 4. The app's role as a "launch point for a BMAD learning cycle" is not carried forward — and arguably undercut
- **Brief location:** "Success Criteria" — "The app serves as a launch point for a BMAD learning cycle: brainstorm → define → build."
- **Gap:** This success criterion is about the *built app* being a pedagogical stepping-off point for the user's own subsequent BMAD work. The PRD has no equivalent success metric for this (SM-1 and SM-2 only cover speed-to-ideas and single-session buildability). Worse, PRD §6 Non-Goals bullet 4 states "This does not attempt to teach BMAD phases interactively," dismissing the brief's "How it works"/"Next step" hints as mere "UI polish, not a teaching feature" — without acknowledging that this walks back a stated brief success criterion rather than just deferring an optional enhancement.
- **Why it matters:** Reads as a silent narrowing of what "success" means for the project, not a flagged, deliberate tradeoff like the other two resolved ambiguities.

## 5. The "BMAD Learning Angle" section's full skill arc is only partially carried forward
- **Brief location:** "BMAD Learning Angle" — lists `bmad-brainstorming`, `bmad-ux`, `bmad-architecture`, `bmad-create-story`, and `bmad-help` as the intended learning trajectory, explicitly including `bmad-help` as "a follow-on artifact that can recommend next steps after the launcher is built."
- **Gap:** PRD §1 Document Purpose only mentions handoff to `bmad-ux` and `bmad-create-story`. There's no mention of `bmad-help` or the intent that the finished app should feed into a next-steps recommendation artifact.
- **Why it matters:** Minor, but it's part of the same pattern as #4 — the meta-purpose of the project (teaching/demonstrating the full BMAD arc) is quietly narrowed to just "get this one app built."
