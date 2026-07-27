---
title: Review Report — BMAD Idea Launcher Brief
date: 2026-07-27
brief_version: 2
---

# Review Report: BMAD Idea Launcher Brief

**Summary assessment:** Two of five dimensions carry findings serious enough to matter before a stakeholder reads this — most notably, the brief never says how "Generate ideas" actually produces ideas, and the section that should let a reader know whether this project succeeded mixes a build constraint in with the only two testable criteria. The other three dimensions are workable but each carry at least a moderate or minor gap. Content is unchanged from the prior review except a one-word wording edit in the Executive Summary ("rapid implementation" → "rapid implementations"), which does not affect any finding below.

## 1. Problem Statement Clarity

**Moderate.** The Problem section states: "People often have a good problem or topic but struggle to move from that prompt to concrete project ideas." This names a real category of friction but never lands on a concrete instance of it — no scenario, no example prompt, no description of what "struggling" looks like in practice (staring at a blank page? drowning in too many options? not knowing where to start?). "Existing idea generation tools can feel generic, overloaded, or too heavy for quick experimentation" is asserted without naming a single such tool or what "too heavy" means operationally. A reader cannot picture the moment this problem shows up.

## 2. Defensibility of Stated Goals

**Critical.** Success Criteria lists three items, but only one is a genuine, measurable user-facing goal:

- "User can enter a prompt and generate three idea cards in under 30 seconds" — measurable, defensible.
- "The project is buildable in a single front-end session (HTML/CSS/JS or small framework)" — this is a build constraint on the team, not a signal that the product works for the user. It doesn't belong in Success Criteria as a measure of the product succeeding.
- "The app serves as a launch point for a BMAD learning cycle: brainstorm → define → build" — nothing in this sentence is testable. What observation would tell you this criterion failed? The brief never says, and no metric or behavior is attached.

A skeptic asking "how would we know if we failed" gets a real answer for one of three criteria.

## 3. Hidden or Unstated Assumptions

**Critical.** The Solution section says the app "gets three idea cards" from a prompt, but never states what generates them. Are they produced by a call to an LLM, a fixed template bank, a random sample, or something else? This is the core mechanic of the product and it is entirely unspecified.

This silence creates a direct tension with Scope: "Backend API integration" is explicitly out of scope, and all state is described as session-only, front-end-buildable in "a single front-end session." If idea generation requires calling an external LLM API to produce non-generic results — which the Problem section implies is the whole point, since it complains that "existing idea generation tools can feel generic" — that requires some backend or client-side API call the brief has ruled out discussing. If instead the ideas come from a static/templated set, the brief needs to say so, because that changes what "three idea cards" can credibly deliver and undercuts the differentiation claim ("delivers a complete, usable idea flow" implies more than a canned response).

## 4. Scope-Creep Risk

**Minor.** The in-scope/out-of-scope lists are tight and clearly bounded. The risk sits in "Optional enhancements, if time allows": localStorage save, a Clear button, a "How it works" note, and a "Next step" hint pointing at `bmad-ux` — four additional items layered onto a stated 1-2 hour build. None is individually large, but the section as written reads as a queue the builder will feel pressure to work through, not a hard boundary, which softens the "1-2 hours" claim made in the Executive Summary.

## 5. Gaps in Target-User Definition

**Moderate.** Primary user is described as "a BMAD learner who wants a hands-on, 1-2 hour experiment" and "someone who wants a quick way to turn a prompt into actionable project ideas." Secondary user is "a developer who wants a minimal demo of idea generation and concept validation" and "a BMAD practitioner who wants a compact artifact for teaching or experimentation." Primary and secondary overlap heavily — a "BMAD learner" and a "BMAD practitioner" are not clearly distinguished, and none of the four descriptions is specific enough that two readers would picture the same person doing the same thing at the same moment. There is no detail on prior experience level, what "hands-on" means in practice, or why the primary/secondary split matters to any product decision in this brief.
