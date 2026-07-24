---
title: BMAD Idea Launcher
status: final
approval_status: draft
created: 2026-07-24
updated: 2026-07-24
version: 1
---

# PRD: BMAD Idea Launcher

## 1. Document Purpose

This PRD turns the approved [Product Brief v5](../../briefs/brief-BMAD-2026-07-23/brief.md) into implementable requirements for a single build session. It's written for whoever picks this up next — most likely the builder themselves, moving on to `bmad-ux` for the one-screen layout, `bmad-create-story` for the implementation story, and `bmad-help` afterward for what to do next in the BMAD arc. Features are grouped with FRs nested and numbered globally (FR-1 through FR-N) so later artifacts can reference them by ID. `[ASSUMPTION]` tags mark places where this PRD makes a call the brief left open — see §10 for the current list and what's already been confirmed.

## 2. Vision

BMAD Idea Launcher is a tiny, single-screen web app: type a problem or experiment prompt, click Generate ideas, get three idea cards back, favorite the one that lands. It exists to make the ideation step of the BMAD method feel concrete and repeatable in under 30 seconds, without requiring a backend, an account, or a real idea-generation model — the "product" is the interaction loop, not the sophistication of the ideas themselves. It's deliberately a minimal experimentation launcher, not an idea-management app: the brief's own framing is a reaction against existing idea-generation tools that "feel generic, overloaded, or too heavy for quick experimentation" — this app should stay small on purpose, not just because of the build-time budget.

Everything about this PRD is sized to a 1-2 hour build. Where the brief left something ambiguous (see §6, §7), this PRD resolves it in favor of shipping the smallest complete loop rather than leaving it as a maybe.

## 3. Target User

### 3.1 Jobs To Be Done

- As a BMAD learner, I want to see the method's ideation step turn a prompt into something concrete, so I understand what "input → actionable output" actually looks like in practice.
- As the builder, I want a project I can finish in one sitting, so I get a complete build → learn cycle instead of an abandoned half-feature.
- As someone showing this to another learner, I want a self-explanatory single screen, so I don't have to narrate what's happening.
- As a developer evaluating the approach, I want a minimal working demo of prompt-to-ideas generation, so I can validate the concept before investing in anything more elaborate.

### 3.2 Key User Journeys

- **UJ-1.** Jordan, a BMAD learner, opens the app, types a one-line prompt, clicks Generate ideas, reads the three cards, and favorites the one they'd actually build next.

## 4. Glossary

- **Prompt** — the free-text problem or experiment description the user types into the single input field.
- **Idea Card** — one of exactly three generated results, each with a title, a one-sentence description, and a favorite toggle.
- **Favorite** — a per-card boolean state, toggled independently per card, shown with a distinct highlighted visual state.
- **Session** — the lifetime of one browser tab load; state (prompt, cards, favorites) is scoped to it unless otherwise noted.

## 5. Features

### 5.1 Prompt-to-Ideas Generation

**Description:** The user types a Prompt into a single input field and clicks Generate ideas. The system produces exactly three Idea Cards from that Prompt and renders them on the same screen. Realizes UJ-1. Idea generation is a local, templated/keyword-driven transform of the Prompt — not a call to an external LLM API — confirmed for v1: this keeps the build backend-free and inside the 1-2 hour budget. An LLM-backed generator is a possible v2 direction, not ruled out permanently, just out of scope for this PRD.

**Functional Requirements:**

#### FR-1: Generate three idea cards from a prompt

A user can enter a Prompt and generate exactly three Idea Cards by clicking Generate ideas. Realizes UJ-1.

**Consequences (testable):**

- Clicking Generate ideas with a non-empty Prompt renders exactly three Idea Cards, each with a title and a one-sentence description.
- Clicking Generate ideas with an empty Prompt does not generate cards; the Prompt input shows a brief red-outline validation state instead of silently doing nothing.
- The full round trip — click to three cards rendered — completes in under 5 seconds on a typical laptop, well inside the 30-second target in SM-1.
- Generating again with a new Prompt replaces the previous three Idea Cards; it does not append to them.

#### FR-2: View results in a responsive one-screen layout

A user can view the Prompt input and generated Idea Cards on one screen, at desktop and mobile widths, without navigating away. Realizes UJ-1.

**Consequences (testable):**

- The input field, Generate ideas button, and all three Idea Cards are visible on a single screen at both a 1440px-class desktop width and a 375px-class mobile width, without horizontal scrolling.
- No routing or page transition occurs between entering a Prompt and seeing results.

### 5.2 Favoriting

**Description:** Each Idea Card carries its own Favorite toggle. Favoriting is the one piece of state the user actively curates. Realizes UJ-1.

**Functional Requirements:**

#### FR-3: Toggle favorite per idea card

A user can toggle Favorite on any Idea Card independently of the other two.

**Consequences (testable):**

- Toggling Favorite on one Idea Card does not change the Favorite state of the other two.
- A favorited Idea Card is visually distinguishable from a non-favorited one (e.g. border, fill, or icon state change) without relying on color alone.
- Favorite state does not persist past a page reload in MVP — see D-1 in §7.2 for the deferred persistence option. `[ASSUMPTION]`

**Feature-specific NFRs:**

- The favorited-state indicator must be distinguishable without color alone (e.g. an icon or border change), so the feature doesn't depend on color perception.

## 6. Non-Goals (Explicit)

- This is not an idea *management* tool — no editing, deleting, tagging, or searching past ideas (matches brief).
- This is not multi-user or authenticated — no accounts, no sharing, no server-side anything.
- This is not an LLM product demo for v1 — see §5.1 for the generation-approach decision.
- This does not attempt to teach BMAD phases *interactively within the app itself* — the "How it works" / "Next step" hints from the brief are deferred to v1.1 (§7.2). **This narrows *how* the app supports learning, not *whether* it does:** the brief's success criterion that the app "serves as a launch point for a BMAD learning cycle" still holds — a working MVP is itself the concrete artifact that lets the builder move on to `bmad-ux`, `bmad-create-story`, and `bmad-help`. That's carried as SM-3 in §8, not dropped.

## 7. MVP Scope

### 7.1 In Scope

- Single Prompt input field with placeholder text.
- Generate ideas button producing exactly three Idea Cards (FR-1).
- One-screen, responsive layout at desktop and mobile widths (FR-2).
- Per-card Favorite toggle with a distinct highlighted state (FR-3).

### 7.2 Out of Scope for MVP

The brief's review flagged its "optional enhancements, if time allows" list as an unresolved soft edge; this PRD resolves it by explicitly deferring all four to v1.1:

- **D-1 (deferred, not an FR): Persist the favorited idea in `localStorage`** across reloads. Reason: not needed for the core loop to be complete; add only once FR-1 through FR-3 work end-to-end. Deliberately unnumbered as an FR so it isn't mistaken for in-scope MVP work by downstream story generation.
- **Clear button** to reset the prompt and results. Reason: nice-to-have convenience, not required for the loop (reloading the page achieves the same thing in MVP).
- **"How it works" note** explaining the BMAD learning intent. Reason: documentation, not functionality — better placed in a README than burning build-session time.
- **"Next step" hint pointing at `bmad-ux`.** Reason: same as above; sequencing which BMAD skill comes next is this PRD's job, not the running app's.
- Backend API integration, persistent storage beyond the deferred D-1, full idea management, and authentication/multi-user support (all already out of scope per the brief, carried forward unchanged).

## 8. Success Metrics

**Primary**

- **SM-1**: Time-to-first-ideas — a user completes Prompt entry through three rendered Idea Cards in under 30 seconds. Validates FR-1, FR-2.

**Secondary**

- **SM-2**: Single-session buildability — the MVP (FR-1 through FR-3) is implementable and demoable within one 1-2 hour front-end coding session. Validates FR-1, FR-2, FR-3.
- **SM-3**: Learning-cycle continuity — once built, the MVP itself is the concrete artifact the builder carries into the next BMAD steps (`bmad-ux`, `bmad-create-story`, `bmad-help`). Success here is qualitative: the builder can point at a working prompt-to-ideas loop when starting those steps, rather than a half-finished app. Validates FR-1, FR-2, FR-3 collectively (the loop working end-to-end is the whole point).

**Counter-metrics (do not optimize)**

- **SM-C1**: Idea sophistication — do not chase cleverer or more varied generated ideas at the cost of the 1-2 hour build constraint (SM-2). A simple templated generator that ships beats a fancier one that blows the timebox. Counterbalances SM-2.

## 9. Open Questions

1. Should the three Idea Cards vary per Prompt in any deterministic way, or is visibly-similar output across different prompts acceptable for a learning-scoped MVP?

## 10. Assumptions Index

- §5.2 (FR-3) — Favorite state does not persist across a page reload in MVP; persistence is deferred to v1.1 (§7.2, D-1).

**Confirmed during drafting (no longer open):** idea generation is local/templated, not LLM-backed, for v1 — confirmed by the user; see §5.1, §6, §8 (SM-C1).
