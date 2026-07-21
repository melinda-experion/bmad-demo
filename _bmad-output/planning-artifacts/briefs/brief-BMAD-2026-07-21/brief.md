---
title: Idea Spark App
created: 2026-07-21
updated: 2026-07-21
status: draft
---

# Product Brief: Idea Spark App

## Executive Summary

Idea Spark is a simple web app for generating software-product ideas. A user types a prompt describing an interest, problem space, or theme, and the app returns three distinct software-product ideas. There's no account system, no idea library, no complexity beyond the core loop: type a prompt, get three ideas back.

This project exists primarily to learn the BMAD method end to end — brief through to a working build — using a small, low-stakes app as the vehicle. `[ASSUMPTION]` The learning goal takes priority over the product's real-world usefulness, so scope should stay deliberately minimal rather than growing toward a "real" product.

## The Problem

People trying to come up with a software product to build (for a side project, a hackathon, or just to practice) often stare at a blank page. A prompt like "something for gardeners" is a starting point, but turning it into a few concrete, buildable product ideas takes effort most people don't want to spend just to get unstuck.

`[ASSUMPTION]` For this exercise, the "problem" is intentionally light — it's a real but small annoyance (idea-generation friction), not a validated, painful gap in the market. That's fine given the purpose of this project.

## The Solution

A single-page web app with one input (a text prompt) and one action (generate). Submitting the prompt returns exactly three software-product ideas, each concise enough to read at a glance — a name/concept and a short description of what it does and who it's for.

`[ASSUMPTION]` Idea generation is powered by an LLM call, since that's the simplest way to produce varied, relevant ideas from an arbitrary prompt without building any custom logic.

## Who This Serves

Primary user: Mel, building this as a learning exercise. `[ASSUMPTION]` No other users are in scope — this isn't being built for external distribution, so there's no persona work, no onboarding flow, no multi-user concerns.

## Success Criteria

- The BMAD workflow was followed end-to-end (brief, PRD, architecture, stories, implementation) and produced a working small app.
- The app reliably takes a prompt and returns exactly 3 relevant software-product ideas.
- The tech stack stayed simple — no more moving parts than the core loop requires.

`[ASSUMPTION]` "Working" means running locally / deployable for personal use, not production-hardened (no auth, no scaling concerns, no monitoring).

## Scope

**In for v1:**

- One page: prompt input, submit action, display of 3 generated ideas.
- Web app, simplest viable stack (`[ASSUMPTION]` e.g. a single frontend framework or even server-rendered pages, one backend endpoint that calls an LLM API — exact stack choice deferred to the architecture phase).

**Explicitly out for v1:**

- Accounts, login, or saved history of past prompts/ideas.
- Regenerate/refine/favorite individual ideas.
- Any idea categories beyond "software product."
- Non-web form factors (mobile app, CLI).

`[ASSUMPTION]` These are inferred from "keep it as simple as possible" — flag anything you'd actually like in v1 and I'll move it in.

## Vision

`[ASSUMPTION]` No roadmap beyond this exercise. If it proves genuinely useful afterward, saved ideas, refinement, or sharing would be natural next steps — out of scope here.
