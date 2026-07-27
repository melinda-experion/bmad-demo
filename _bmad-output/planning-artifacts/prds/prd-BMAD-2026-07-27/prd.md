---
title: BMAD Idea Launcher
created: 2026-07-27
updated: 2026-07-27
approval_status: approved
version: 1
---

# PRD: BMAD Idea Launcher

## 1. Document Purpose

This PRD turns the approved BMAD Idea Launcher brief (`brief-BMAD-2026-07-27`, v2) into implementable requirements for a single builder taking this on as a 1-2 hour BMAD learning exercise. Features are grouped with functional requirements (FRs) nested and globally numbered; `[ASSUMPTION]` tags mark points inferred without direct confirmation, indexed in §11.

## 2. Vision

BMAD Idea Launcher is a micro web app that turns a short problem or experiment prompt into three starter ideas. A user types a prompt, clicks `Generate ideas`, and gets three idea cards — each with a title, one-sentence description, and a favorite toggle — on a single responsive screen. The point isn't idea-management sophistication; it's making the leap from "I have a prompt" to "I have three concrete starting points" feel immediate, so a BMAD learner can move straight into brainstorm → define → build.

Shipping a complete, small thing on purpose is the differentiator here, not an afterthought: rather than build toward a large idea-management product, this delivers one narrow, usable flow end to end and stops. If it succeeds, the natural next steps (not committed for v1) are guided idea categories aligned to BMAD phases, a tiny workflow helper surfacing the next BMAD step, and exporting the favorited idea straight into a brief or story.

## 3. Target User

### 3.1 Jobs To Be Done

- Turn a vague problem/experiment prompt into three concrete starting ideas, fast.
- Get a hands-on feel for the BMAD method by building and using a tool that embodies it, in a single short session.
- Have something small and complete to point to as a demo of idea generation and concept validation.

### 3.2 Non-Users (v1)

- Anyone needing persistent, multi-session idea management (editing, tagging, searching past ideas) — out of scope; see §7.2.
- Teams needing shared/collaborative idea generation — this is a single-user, single-session tool.

### 3.3 Key User Journeys

- **UJ-1.** A BMAD learner opens the app, types a problem prompt, clicks `Generate ideas`, reads the three cards, and favorites the one they'll carry into `bmad-brainstorming`.
- **UJ-2.** A developer opens the app to see a minimal, complete idea-generation flow as a demo — no setup beyond having an API key configured. **Edge case:** if the idea-generation call fails or times out, the user sees an inline error and can retry without losing their typed prompt.

## 4. Glossary

- **Prompt** — the short problem or experiment description the user types into the single input field.
- **Idea Card** — one of exactly three generated results, each with a title and a one-sentence description.
- **Favorite** — a per-card toggle marking exactly one idea card as selected at a time; selecting a new Favorite clears any previous one (see FR-4).
- **Idea Generation Service** — the backend call that takes a Prompt and returns three ideas for rendering as Idea Cards. `[ASSUMPTION: implemented as a thin server-side proxy to an LLM API (e.g. Claude), per user decision during PRD discovery — see §9 for the scope implication.]`

## 5. Features

### 5.1 Prompt Input & Idea Generation

**Description:** A single-screen, responsive layout presents one prompt input field (placeholder: "Describe the problem or experiment prompt...") and a `Generate ideas` button. On click, the app sends the Prompt to the Idea Generation Service and renders exactly three Idea Cards from the response. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-1: Prompt entry

User can type a Prompt into a single input field with placeholder text. Realizes UJ-1.

**Consequences (testable):**

- Input field is present on initial page load with the specified placeholder text.
- Field accepts free-text input of at least 280 characters without truncation.

#### FR-2: Generate ideas

User can click `Generate ideas` to send the current Prompt to the Idea Generation Service and receive exactly three ideas back for display. Realizes UJ-1, UJ-2.

**Consequences (testable):**

- Clicking `Generate ideas` with a non-empty Prompt results in exactly three Idea Cards rendered within 30 seconds under normal network conditions (brief's Success Criteria).
- Clicking `Generate ideas` with an empty Prompt does not trigger a call to the Idea Generation Service; the user sees an inline cue (field border color change plus short text) that a prompt is required. `[ASSUMPTION: empty-prompt behavior wasn't specified in the brief.]`
- If the Idea Generation Service call fails or times out, the user sees an inline error message and the typed Prompt is preserved for retry (UJ-2 edge case).

**Out of Scope:**

- Rate limiting, retries-with-backoff, or queuing logic beyond a single retry initiated by the user re-clicking `Generate ideas`.

**Feature-specific NFRs:**

- The Idea Generation Service call must not expose the LLM API key to client-side code — the key lives server-side only. `[ASSUMPTION: this is the minimum viable security bar for a learning project handling a real API key; deeper hardening is out of scope.]`

### 5.2 Idea Cards & Favoriting

**Description:** Each of the three generated ideas renders as a card showing its title, one-sentence description, and a favorite toggle. Favoriting is session-only unless the optional localStorage enhancement (§7) is built. Realizes UJ-1.

**Functional Requirements:**

#### FR-3: View idea cards

User sees exactly three Idea Cards after a successful generation, each showing a title and a one-sentence description.

**Consequences (testable):**

- Exactly three cards render, no more, no fewer, for any successful Idea Generation Service response.
- Each card visibly displays both a title and a description field.

#### FR-4: Favorite an idea card

User can toggle a Favorite state on any one Idea Card, with a clearly highlighted visual state when active.

**Consequences (testable):**

- Clicking the favorite toggle on a card visibly changes its highlighted state (visually distinct border/background, not conveyed by color alone).
- Favorite state is per-card and resets on a new `Generate ideas` click, unless localStorage persistence (§7.2) is built. `[ASSUMPTION: only one card can be favorited at a time, mirroring the brief's singular "the favorite idea" phrasing in its Vision section — not stated explicitly as single-select in the brief itself.]`

## 6. Non-Goals (Explicit)

- This is not an idea-management app: no editing, deleting, tagging, or searching past ideas (brief, Scope: Out of scope).
- This is not a multi-user or authenticated product — no accounts, no shared sessions.
- This is not a general-purpose LLM chat interface; the only supported interaction is prompt-in, three-ideas-out.

## 7. MVP Scope

### 7.1 In Scope

- Single prompt input field with placeholder text
- `Generate ideas` button triggering a call to the Idea Generation Service
- Exactly three Idea Cards rendered per generation (title, description, Favorite toggle)
- Inline error + retry on generation failure
- One-screen, responsive layout (desktop and mobile widths)
- Session-only state for prompt, results, and favorite

### 7.2 Out of Scope for MVP

- Persistent storage beyond runtime, aside from the optional localStorage save of the favorite (deferred, below)
- Full idea management (edit, delete, tag, search)
- Complex authentication or multi-user support
- Rate limiting/cost controls beyond a single manual retry (see §9 Open Questions — `[NOTE FOR PM]` this is worth revisiting if the app sees any real usage beyond the builder's own testing, since each generation is a paid LLM call)

**Deferred, if time allows:**

- Save the favorite idea in `localStorage`
- A `Clear` button to reset the prompt and results
- A small "How it works" note showing the BMAD learning intent
- A tiny "Next step" hint pointing at `bmad-ux`

## 8. Success Metrics

**Primary**

- **SM-1**: Time from clicking `Generate ideas` to three Idea Cards rendering — target under 30 seconds. Validates FR-2.
- **SM-2**: The builder completes the build in a single 1-2 hour session and uses the running app to pick a favorite idea to carry into `bmad-brainstorming`. Validates FR-1 through FR-4.

**Counter-metrics (do not optimize)**

- **SM-C1**: Don't optimize idea-generation latency by caching/reusing responses across different prompts — each Prompt should get a genuinely fresh generation call, since the point is real responsiveness to what the user typed, not the appearance of speed. Counterbalances SM-1.

## 9. Open Questions

1. What LLM/provider backs the Idea Generation Service, and how is the API key supplied/configured for a local build? Brief and discovery didn't specify a provider — left to the builder's implementation choice.
2. Does adding a server-side LLM proxy still fit inside the brief's 1-2 hour build target? `[NOTE FOR PM]` worth a quick sanity check before starting the build. (Context: the brief's "no backend API integration" out-of-scope item is deliberately overridden here — the proxy was confirmed as the intended mechanism during PRD discovery, not a silent scope creep — but the time-budget question itself was never resolved.)
3. Is there any cost ceiling or usage cap intended for the Idea Generation Service, given each `Generate ideas` click is a paid API call?
4. Categories/workflow-helper/export ideas from the brief's Vision (§2) are explicitly not committed for v1 — confirm they stay deferred rather than creeping into this build.

## 10. BMAD Learning Angle

This PRD is one stage of a five-stage BMAD learning exercise named in the brief; the artifacts and skills below are what carry this project through the rest of the method, not just this PRD in isolation:

- `bmad-brainstorming` — the core product idea is itself an ideation tool (realized in UJ-1, SM-2).
- `bmad-ux` — one-screen experience and interaction design for the flow specified in §5 (deferred "Next step" hint in §7.2 points here).
- `bmad-architecture` — minimal data shape and application spine for the Idea Generation Service and card rendering (§4, §5.1).
- `bmad-create-story` — one implementation story for the MVP scoped in §7.1.
- `bmad-help` — a follow-on artifact recommending next BMAD steps once the launcher is built.

## 11. Assumptions Index

- §4 Glossary — Idea Generation Service implemented as a thin server-side LLM proxy, per user decision during PRD discovery.
- §5.1 FR-2 — Empty-prompt behavior (block the call, show inline cue) wasn't specified in the brief.
- §5.1 FR-2 NFR — API key kept server-side only, as the minimum viable security bar.
- §5.2 FR-4 — Favoriting is single-select (one card at a time), inferred from the brief's singular "the favorite idea" phrasing rather than stated explicitly.
