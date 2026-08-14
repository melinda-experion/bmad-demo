---
title: BMAD Idea Launcher
created: 2026-08-14
updated: 2026-08-14
approval_status: review
confidence: 72
confidence_label: Medium
confidence_rationale: Fast-path draft, but every major claim traces to real, inspected artifacts (server.js, lib/ideaService.js, sprint-status.yaml, Story 1.1) rather than pure inference. Two [ASSUMPTION] tags (retroactive framing, Epic 1 as the completion bar) were surfaced and the user explicitly confirmed the draft as-is, though the tags remain in the text rather than being rewritten as settled fact.
---

# Product Brief: BMAD Idea Launcher

## Executive Summary

BMAD Idea Launcher is a small web app that turns a single problem statement into three distinct, AI-generated starter ideas for an application that could solve it. A user types in a problem, clicks generate, and gets three titled idea cards back within seconds — no accounts, no saved projects, no complexity.

The app itself is not the point: it's a real, working artifact meant to demonstrate the BMAD workflow end to end — brief through PRD, architecture, epics, stories, and implementation — on something small enough to build in a couple of hours but real enough to require genuine decisions (an actual LLM call, real error handling, real tests) rather than a toy stub. It is a genuinely working implementation, not a mockup: the LLM call is real, and each failure path (timeout, network, malformed response) has distinct handling and test coverage. [ASSUMPTION: this brief is written after the fact, since Epic 1 is already partly built — see Scope below for what's real vs. planned.]

## The Problem

Two problems, one demo-shaped:

1. **The end-user problem (the app's own premise):** someone with a vague problem statement ("people forget to water their plants") wants a quick nudge toward possible application ideas, without doing the brainstorming themselves.
2. **The actual problem this project solves:** BMAD as a workflow is easiest to trust once you've watched it produce something real. A brief written for a fictional or trivial demo doesn't exercise the same muscles (LLM integration, error codes, timeouts, testing) as a brief written for something someone could actually deploy. This project is the "something real."

## The Solution

A single-page web app: a textarea for the problem statement, a "Generate ideas" button, and three result cards (title + description) rendered on response. Submission hits a small Node HTTP server (`server.js`, no framework) which calls `lib/ideaService.js`, an adapter that sends the prompt to the Anthropic Messages API and parses the response into exactly three `{title, description}` ideas — throwing distinct, coded errors (`TIMEOUT`, `NETWORK`, `MALFORMED`) that map to specific HTTP status codes rather than collapsing into a generic failure.

No caching, no memoization — every click is a fresh LLM call, which is a deliberate simplicity choice, not an oversight.

## Who This Serves

**Primary user (in-app):** anyone with a rough problem statement who wants three concrete starter ideas — no specific persona beyond "has a problem, wants ideas fast." Success for them is getting three coherent, distinct, non-generic ideas back in under ~30 seconds.

**Primary audience (of this brief and the project):** whoever is walking through the BMAD workflow demo — a learner, evaluator, or team considering BMAD — who wants to see a believable chain from problem statement to working, tested code.

## Success Criteria

- A user can submit a non-empty problem statement and receive exactly three distinct, well-formed idea cards (title + description) rendered in the browser.
- Failure modes are distinguishable and handled, not swallowed: provider timeout, network failure, and malformed LLM output each produce a specific error response rather than a generic crash.
- [ASSUMPTION] The project completes Epic 1 (generate → favorite → inline validation) with test coverage — see Scope below.
- No proprietary metrics or business KPIs apply — this is a demo, not a monetized product.

## Scope

**In (already built, Story 1.1 — in review):**
- Problem-statement input and "Generate ideas" button
- Real LLM-backed idea generation via `lib/ideaService.js` (Anthropic Messages API), returning exactly three `{title, description}` ideas
- Coded error handling: `TIMEOUT` → 504, `NETWORK` → 502, `MALFORMED` → 500, plus existing 400s for invalid JSON / empty prompt / >2000 characters
- No caching — every submission is a fresh provider call
- Unit and integration test coverage for the above

**In (in progress, Story 1.2):**
- Favoriting an idea card

**In (backlog, Story 1.3):**
- Inline validation cue for an empty prompt

**Out (explicitly, for this demo):**
- User accounts, persistence beyond the current session, saved idea history
- Multi-provider or model-switching support
- Styling/design polish beyond a functional UI
- Distinctness-checking across the three generated ideas (acknowledged as a gap, accepted for MVP per Story 1.1's review notes)

## Vision

This project doesn't need a 2-3 year roadmap — its purpose is fulfilled once it demonstrates the BMAD workflow convincingly. If it outlived that purpose, the natural next step would be turning it into an actual minimal brainstorming tool (saved history, shareable idea sets, maybe iterating on a chosen idea) — but that would be a new brief, not an extension of this one.
