# Brief Review Report: BMAD Idea Launcher

**Reviewed:** 2026-07-23
**Brief:** `brief.md`
**Reviewer:** Voss (adversarial brief review)

## Summary Assessment

This is a small, intentionally lightweight brief for a 1-2 hour learning exercise, and it reads as one — tight, honest about being a toy, no fabricated moat. One critical finding: the brief's core mechanic (turning an arbitrary prompt into three relevant ideas) is never specified, and the natural way to do that sits in tension with the "no backend" scope boundary. The remaining findings are moderate-to-minor softness typical of a fast-turnaround brief — defensible goals mixed with one vague one, overlapping user descriptions, and a couple of unstated assumptions about how "idea generation" actually works. No critical findings on problem framing or scope discipline.

## 1. Problem Statement Clarity

**Finding (minor):** The Problem section states people "struggle to move from that prompt to concrete project ideas" and that "existing idea generation tools can feel generic, overloaded, or too heavy" — but names no concrete scenario, no specific tool being reacted against, and no example of what "too heavy" looks like in practice. For a learning-project brief this is a defensible level of abstraction, but a skeptic could still ask "which tools, and what did trying them actually feel like?" and get no answer from the text.

**Finding (minor):** The problem is framed twice — once generically ("people... struggle") and once specifically for the BMAD learner ("For someone learning BMAD, the immediate need is..."). The second framing is the one the rest of the brief actually serves; the first reads as scaffolding that doesn't earn its place given the brief is explicitly a BMAD learning exercise, not a general-market tool.

## 2. Defensibility of Stated Goals

**Finding (moderate):** Two of the three Success Criteria are measurable and binary — "under 30 seconds," "buildable in a single front-end session." The third — "The app serves as a launch point for a BMAD learning cycle: brainstorm → define → build" — has no way to fail. Nothing in the brief says what evidence would show the app did or didn't serve as that launch point. A skeptic asking "how would we know if we failed at this one?" gets no answer.

**Finding (minor):** "Buildable in a single front-end session" is a build-time constraint on the team, not a user- or product-success signal, and it's the same claim already made in the Executive Summary ("designed to be built in 1-2 hours"). Counting it as a success criterion alongside the 30-second usability target conflates "we predict this is easy to build" with "this worked."

## 3. Hidden or Unstated Assumptions

**Finding (critical):** The core mechanic — turning a free-text prompt into three specific, presumably-relevant idea cards — is never explained. Scope explicitly excludes "Backend API integration," yet generating three ideas that plausibly respond to an arbitrary user prompt is not something a static front-end typically does on its own (canned/randomized ideas, a client-side rules engine, and a call to an external LLM API all produce very different builds and very different user experiences). The brief needs to say, out loud, which of these it means — otherwise "no backend" may quietly mean "the ideas aren't actually responsive to the prompt," which would undercut the stated Problem and Solution.

**Finding (moderate):** The brief assumes "three idea cards" is inherently the right output shape and that a favorite toggle is inherently useful feedback, but never states why three (not one, not five) or what a user does with a favorited idea beyond seeing it highlighted (Out of scope explicitly excludes persistence beyond an optional localStorage save). If the favorite has no persistent consequence by default, its value in the primary flow is unstated.

**Finding (minor):** "Session-only" state is asserted as sufficient for the target user without acknowledging the assumption that a learner doing a 1-2 hour experiment won't want to revisit or reference results after closing the tab — plausible for this scope, but not stated as a deliberate tradeoff.

## 4. Scope-Creep Risk

**Finding (minor):** The Scope section itself is disciplined and the in/out boundary is clear. The risk sits in "Optional enhancements, if time allows" — four items (localStorage save, Clear button, "How it works" note, "Next step" hint) appended to a brief for a 1-2 hour build. None are individually large, but "if time allows" on a 1-2 hour budget is a soft boundary that invites scope to expand quietly during implementation rather than being cut up front.

**Finding (minor):** "Favorite/save action per card, with a clear highlighted state" (in-scope) and "Save the favorite idea in `localStorage`" (optional) sit close enough together that an implementer could reasonably treat persistence as core rather than optional — the line between them depends on reading the two lists in the right order.

## 5. Gaps in Target-User Definition

**Finding (moderate):** Primary and secondary users overlap without a clear line between them. Primary lists "a BMAD learner" and "someone who wants a quick way to turn a prompt into actionable project ideas" — the second is a restatement of the first, not a distinct persona. Secondary lists "a developer who wants a minimal demo" and "a BMAD practitioner who wants a compact artifact for teaching" — "BMAD learner" (primary) and "BMAD practitioner" (secondary) are not clearly distinguished; a practitioner is presumably a more advanced learner, but the brief doesn't say what differs in what each needs from the tool. Two people reading this brief could reasonably picture different people as "the" user.

**Finding (minor):** No section addresses who is *not* the user — for a brief this small that's a reasonable omission, but it means the audience boundary is defined entirely by inference from the BMAD Learning Angle section rather than stated directly.

## Dimension Summary

| Dimension | Status |
|---|---|
| Problem statement clarity | Minor findings only |
| Defensibility of stated goals | Moderate finding (one unmeasurable criterion) |
| Hidden assumptions | Critical finding (core mechanic unspecified) |
| Scope-creep risk | Minor findings only |
| Target-user definition | Moderate finding (overlapping personas) |
