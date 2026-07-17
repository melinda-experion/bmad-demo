---
title: BMAD Idea Launcher
status: draft
created: 2026-07-17
updated: 2026-07-17
---

# PRD: BMAD Idea Launcher
*Working title — confirm.*

## 0. Document Purpose

This PRD scopes BMAD Idea Launcher for its builder(s) and any downstream BMAD workflow (`bmad-ux`, `bmad-architecture`, `bmad-create-story`). It builds directly on the approved product brief (`brief-BMAD-2026-07-17/brief.md`) — vision, problem, and scope boundaries are not re-litigated here, only translated into features, FRs, and testable criteria. Terms are defined once in the Glossary and used verbatim throughout; FRs are numbered globally for stable reference by later stories.

## 1. Vision

BMAD Idea Launcher is a tiny, single-screen web app that turns a short problem or experiment prompt into three concrete starter ideas. It exists to make the BMAD learning cycle (brainstorm → define → build) tangible in an hour or two, not to be a product in its own right. Success looks like: type a prompt, get three usable idea cards, pick a favorite — done, with nothing left running behind the scenes.

Its value is pedagogical as much as functional: it is small enough to build in one sitting, so the person building it experiences the full BMAD arc (brief → PRD → UX → architecture → story → code) without the scope itself becoming the obstacle.

## 2. Target User

### 2.1 Jobs To Be Done

- As a BMAD learner, I want a minimal real target to run the full BMAD workflow against, so I can learn the method by building something finishable in 1-2 hours.
- As a BMAD learner, I want to type a rough prompt and immediately see concrete idea options, so an ambiguous topic starts feeling actionable.
- As a developer or BMAD practitioner, I want a compact, working demo of an idea-generation flow, so I have something to show or teach from without a full product's overhead.

### 2.2 Non-Users (v1)

- Anyone needing persistent, multi-session idea management (saved history, editing, tagging, search) — out of scope by brief.
- Anyone needing multi-user or authenticated use — no accounts exist in v1.

### 2.3 Key User Journeys

Single-operator, single-session tool — one lightweight journey covers it (Lighter scope dial per template).

- **UJ-1. A learner turns a rough prompt into three concrete ideas.** A BMAD learner opens the app, types a short problem or experiment prompt into the input field, and clicks "Generate ideas." Three idea cards (title + one-sentence description each) appear on the same screen within seconds. They toggle "favorite" on the one they like best, see it visibly highlighted, and move on to defining it further (e.g., into a brief). Realizes the brief's core success criterion: prompt → 3 ideas in under 30 seconds.

## 3. Glossary

- **Prompt** — the free-text problem or experiment description the user types into the input field. One per generation.
- **Idea Card** — a generated result consisting of a title and a one-sentence description. Exactly three are produced per generation.
- **Favorite** — a per-card toggle marking one idea card as selected. Multiple cards may be favorited; state is visually highlighted.
- **Session** — the runtime lifetime of a single page load. All state (prompt, idea cards, favorites) is Session-scoped unless explicitly persisted (see FR-5).

## 4. Features

### 4.1 Prompt-to-Ideas Generation

**Description:** The core interaction: the user enters a Prompt and generates exactly three Idea Cards from it. `[ASSUMPTION: idea generation is templated/rule-based logic running client-side — not a live LLM API call — per user direction to keep this "basic."]` This keeps the app fully self-contained (no backend, no API keys) and buildable in a single front-end session, consistent with the brief's scope. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Prompt input

User can type a Prompt into a single text input field with placeholder text ("Describe the problem or experiment prompt..."). Realizes UJ-1.

**Consequences (testable):**
- Input accepts free text of reasonable length (no artificial character cap beyond basic sanity bound, e.g. 500 chars).
- Empty prompt does not trigger generation (see FR-2).

#### FR-2: Generate ideas

User can click a "Generate ideas" button to produce exactly three Idea Cards from the current Prompt. Realizes UJ-1.

**Consequences (testable):**
- Clicking with a non-empty Prompt renders exactly 3 Idea Cards within the same view, in under 30 seconds (brief's success criterion; in practice near-instant since generation is local/templated).
- Clicking with an empty Prompt does nothing observable (or shows a minimal inline hint) — no crash, no empty cards.
- Re-clicking "Generate ideas" replaces the previous three Idea Cards (no accumulation).

**Out of Scope:**
- No live LLM/API-backed generation in v1 `[ASSUMPTION]`.
- No idea history or regeneration diffing.

**Feature-specific NFRs:**
- Generation must complete fast enough to feel instant (no visible loading spinner required given local logic; if generation is later swapped for an API call, this NFR should be revisited).

### 4.2 Idea Cards & Favoriting

**Description:** Each generated Idea Card displays a title and one-sentence description, and carries an independent Favorite toggle with a clear highlighted state when active. Realizes UJ-1.

**Functional Requirements:**

#### FR-3: Idea card display

System displays each of the three generated results as a card containing a title and a one-sentence description. Realizes UJ-1.

**Consequences (testable):**
- Each card's title and description are non-empty and legible at both desktop and mobile widths (see FR-6).
- Cards are visually distinct from one another (clear boundaries/spacing).

#### FR-4: Favorite toggle

User can toggle Favorite on/off for any individual Idea Card. Realizes UJ-1.

**Consequences (testable):**
- Toggling a card's Favorite visibly highlights it (e.g., border/background change) distinct from non-favorited cards.
- Toggling is independent per card — favoriting one does not un-favorite another.
- Favorite state holds for the lifetime of the current Session (cleared on reload unless FR-5 is implemented).

#### FR-5: Favorite persistence *(optional enhancement, if time allows)*

System can persist the favorited idea in browser `localStorage` so it survives a page reload.

**Consequences (testable):**
- On reload, a previously favorited card's Favorite state is restored if the same Prompt/results are regenerated deterministically, or the favorited idea's content is otherwise retrievable.

**Out of Scope:**
- Only the favorite is persisted (per brief) — not full generation history.

### 4.3 One-Screen Responsive Layout

**Description:** The entire flow — prompt input, generate action, three idea cards, favoriting — lives on a single screen with no navigation, at both desktop and mobile widths.

**Functional Requirements:**

#### FR-6: Single-screen responsive layout

System renders the full flow (input, button, three cards) on one screen without routing/navigation, adapting layout between desktop and mobile widths.

**Consequences (testable):**
- No second screen, route, or modal is required to complete the core flow.
- Layout remains usable (no horizontal scroll, no overlapping elements) at common mobile widths (~375px) and desktop widths (~1280px+).

### 4.4 Optional Nice-to-Haves *(if time allows, per brief)*

**Description:** Small additions that reinforce the BMAD-learning framing without expanding core scope.

**Functional Requirements:**

#### FR-7: Clear button *(optional)*

User can click "Clear" to reset the Prompt input and remove all current Idea Cards.

#### FR-8: "How it works" note *(optional)*

System displays a small static note explaining the BMAD learning intent of the app.

#### FR-9: "Next step" hint *(optional)*

System displays a small hint pointing the user at `bmad-ux` as the next BMAD workflow step.

**Notes:** FR-7 through FR-9 are explicitly optional per the brief ("if time allows") — they should not block MVP completion and can be dropped without re-opening this PRD.

## 5. Non-Goals (Explicit)

- This is not a general-purpose idea/brainstorm management tool — no edit, delete, tag, or search of ideas.
- This is not building toward a live-LLM-backed product in v1 — generation logic is intentionally local/templated `[ASSUMPTION]`.
- This is not introducing accounts, authentication, or multi-user state.
- This is not a backend service — no server-side persistence beyond the browser (`localStorage`, optional).

## 6. MVP Scope

### 6.1 In Scope

- Prompt input field (FR-1)
- "Generate ideas" button producing exactly 3 idea cards (FR-2)
- Idea card display: title + one-sentence description (FR-3)
- Per-card favorite toggle with highlighted state (FR-4)
- Single-screen, responsive layout, desktop + mobile (FR-6)

### 6.2 Out of Scope for MVP

- Backend API integration (per brief)
- Persistent storage beyond runtime, except optional favorite persistence in `localStorage` (FR-5, deferred if time-constrained)
- Full idea management: edit, delete, tag, search
- Authentication or multi-user support
- Live LLM-backed idea generation `[ASSUMPTION — confirm before UX/architecture if this should instead be a real API call]`

## 7. Success Metrics

**Primary**
- **SM-1**: Time from prompt entry to three visible idea cards — target under 30 seconds (brief's stated bar; expect near-instant given local generation). Validates FR-2.
- **SM-2**: The project is completed end-to-end (brief → PRD → UX → architecture → story → working app) in a single front-end build session. Validates the overall Vision, not a specific FR.

**Counter-metrics (do not optimize)**
- **SM-C1**: Do not optimize idea "quality"/sophistication at the cost of build time or scope creep — the point is a finishable BMAD-learning artifact, not a good idea generator. Counterbalances SM-2.

## 8. Open Questions

1. Should idea generation ever move from templated/local logic to a real LLM call, and if so, in this version or a v2? `[ASSUMPTION: local/templated for v1]`
2. Are FR-7–FR-9 (Clear button, "How it works" note, "Next step" hint) worth committing to now, or purely stretch goals evaluated during build?
3. Should FR-5 (favorite persistence via `localStorage`) be pulled into MVP scope, or stay optional as the brief frames it?

## 9. Assumptions Index

- §4.1 (FR-2) — Idea generation is templated/rule-based client-side logic, not a live LLM API call. Confirmed by user ("basic") during Fast-path discovery.
- §6.2 — Live LLM-backed generation explicitly deferred/out of scope pending answer to Open Question 1.
