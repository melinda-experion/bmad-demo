---
title: BMAD Idea Launcher
created: 2026-07-16
updated: 2026-07-16
status: approved
---

# PRD Testing Override: BMAD Idea Launcher

## 0. Document Purpose

This PRD defines the BMAD Idea Launcher for PMs, and for the downstream workflows already built on top of it — an architecture spine and epics/stories exist and were **written before this PRD**, so this document was reverse-engineered from those artifacts rather than authored first. Terms defined in the Glossary (§3) are used verbatim everywhere else in this document. Features are grouped with their functional requirements (FR-1 through FR-7) nested underneath; inline `[ASSUMPTION]` tags mark anywhere this PRD infers rather than confirms, indexed in §9.

Existing downstream artifacts this PRD should stay consistent with:

- Architecture: `_bmad-output/planning-artifacts/bmad-idea-launcher-architecture/` (see ARCHITECTURE-SPINE.md for AD-1 through AD-11)
- Epics and stories: `_bmad-output/planning-artifacts/epics/` (Epic 1–3, 7 stories)

## 1. Vision

BMAD Idea Launcher is a single-screen web app that turns a rough, half-formed problem into three concrete starter ideas in one step. A learner working through the BMAD method types a prompt, clicks Create ideas, and gets back exactly three idea cards — a title and a short description each — to compare side by side. Anything promising gets a click to favorite; favorites survive a page refresh with no login and no backend account behind them.

It exists to remove the blank-page problem at the very start of the BMAD workflow: before there's a brief, a PRD, or an architecture, there has to be an idea worth building on. The Idea Launcher is that first five minutes — quick, disposable by default, and low-stakes enough that a learner can throw a rough prompt at it, get something back immediately, and move on to development artifacts built on the idea they liked (`bmad-product-brief`, `bmad-prd`) with real content instead of a blank page.

## 2. Target User

### 2.1 Jobs To Be Done

- Quickly move from a rough problem statement to a first, comparable set of concept directions (Story 1.1).
- Keep track of the most promising directions across a session without losing them (Story 2.1, 2.2).
- Complete the whole idea-generation loop without navigation, setup, or an account getting in the way (Story 3.1).

### 2.2 Non-Users (v1)

- Teams needing multi-user or collaborative brainstorming — this is a single-browser, single-user tool.
- Anyone needing to keep a history of past generations, or edit/delete/search ideas after the fact — out of scope for v1 (see §6.2).

### 2.3 Key User Journeys

- **UJ-1. A BMAD learner turns a rough problem into a favorited starter idea.** A learner opens the app fresh (no login), types a rough prompt, clicks Create ideas, watches a brief loading state, and sees three idea cards appear. They read all three, click the star on the one that clicks, and see it visually marked as a favorite — done, in well under two minutes, on whatever device they had open. **Edge case:** if generation fails, the learner sees a short, plain-language error with their original prompt still intact, so they can just retry.

**Scope dial:** this journey is essentially JTBD restated at Lighter weight — a single-session, single-screen loop with no auth or multi-device handoff to plan around.

## 3. Glossary

- **Idea** — A single generated concept, always exactly two visible fields: a title (≤60 characters) and a description (≤200 characters). Additional fields (id, timestamp) may exist internally but never surface in the UI.
- **Generation** — One request/response cycle: a submitted prompt produces exactly three Ideas.
- **Favorite** — A boolean, per-Idea, per-generation flag a user toggles on/off. Multiple Ideas may be favorited at once. Not a rank or score.
- **Prompt** — The free-text problem statement a user types before requesting a Generation.
- **Learner** — The target user of this product; see §2.

## 4. Features

### 4.1 Prompt Capture and Idea Generation

**Description:** The learner enters a Prompt and requests a Generation. The app validates the Prompt is non-empty and non-whitespace-only before enabling submission — `[ASSUMPTION: "meaningful text" from Story 1.1 means non-empty, non-whitespace; no minimum length threshold, confirmed via user selection over a stricter minimum-length rule]`. On submit, a clear loading/busy state is shown. On success, exactly three Idea cards render; if the underlying generation returns fewer than three, the app pads the remaining slots with clearly-generic filler ideas so the learner always sees three cards — `[ASSUMPTION: padding behavior confirmed by user over showing an error; the architecture's AD-9 error path still applies to genuine request failures, not to short responses]`. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Enter and submit a prompt

A learner can enter a non-empty, non-whitespace prompt and click Create ideas to start generation. Realizes UJ-1.

**Consequences (testable):**

- Submission is blocked until the prompt contains at least one non-whitespace character.
- On click, the app immediately shows a clear loading/busy state.

#### FR-2: Render exactly three starter idea cards

The app renders exactly three Idea cards from a successful generation response, regardless of how many ideas the underlying response actually contained.

**Consequences (testable):**

- Each card shows a title (≤60 chars) and a short description (≤200 chars) and nothing else.
- A response with fewer than three ideas is padded with clearly-generic filler ideas until three cards are shown.
- A response with more than three ideas is truncated to the first three.

**Out of Scope:** Idea editing, deletion, search, or regeneration of a single card.

#### FR-3: Show clear feedback when generation fails

When a generation request fails or errors, the app shows a short, user-friendly error message and preserves the learner's original prompt text so they can retry without re-typing it.

**Consequences (testable):**

- On failure, the interface never appears broken or silent — some visible error state is always rendered.
- The prompt field retains the exact text the learner typed before submitting.

**Feature-specific NFRs:**

- Modern-browser only (ES2020+, `fetch`, flexbox/grid) — no legacy/IE11 support `[carried from architecture AD-6]`.

### 4.2 Save and Review Favorites

**Description:** From any rendered set of Idea cards, the learner can mark one or more as Favorites and unmark them just as easily. Favorites are stored client-side only — in the browser's `localStorage` — so they survive a page refresh with no backend or account involved. Realizes UJ-1.

**Functional Requirements:**

#### FR-4: Toggle favorite state per idea

A learner can click a favorite control on any Idea card to mark it visually distinct as a favorite, and click again to remove that state. Multiple ideas may be favorited at the same time.

**Consequences (testable):**

- Clicking the favorite control toggles that card's favorite state only — no other card is affected.
- More than one card can be in the favorited state simultaneously.

#### FR-5: Persist favorites across a page refresh

Favorite selections survive a page reload, restored entirely client-side.

**Consequences (testable):**

- After a refresh, previously favorited ideas still appear marked as favorites.
- Restoring favorite state requires no backend call and no account/login.

**Out of Scope:** Favorites do not sync across browsers or devices, and are lost if the learner clears browser storage or uses private/incognito mode — an accepted MVP limitation, not a bug.

**Feature-specific NFRs:**

- `localStorage` capacity (~5-10MB/origin) is assumed more than sufficient for MVP favorite volumes.

### 4.3 Single-Screen, Responsive Experience

**Description:** The entire loop — enter prompt, generate, review cards, favorite — happens on one screen with no navigation, modals, or additional views. The layout adapts cleanly across mobile and desktop widths. Realizes UJ-1.

**Functional Requirements:**

#### FR-6: Keep the core flow on a single screen

The prompt input, the generate action, and the results area are all available on the same screen; a learner completes the entire flow without navigating to another page or view.

**Consequences (testable):**

- No route change or page navigation occurs at any point in the prompt → generate → favorite flow.

#### FR-7: Support responsive layouts for mobile and desktop

The interface remains usable at common mobile and desktop widths, with all controls visible and tappable and no content overlap or clipping that blocks the core flow.

**Consequences (testable):**

- Layout is verified at mobile (≤600px), tablet (601-1000px), and desktop (>1000px) breakpoints, tested against 375px, 768px, and 1920px widths specifically `[carried from architecture AD-5]`.
- No horizontal scroll is introduced at any of these widths.

## 5. Non-Goals (Explicit)

- No accounts, login, or authentication of any kind.
- No server-side storage of favorites — client-side `localStorage` only.
- No idea history, editing, deletion, or search after a generation completes.
- No analytics or telemetry in v1.
- No internationalization — English only.
- No multi-user or collaborative brainstorming.

## 6. MVP Scope

### 6.1 In Scope

- Prompt entry with basic non-empty validation and a Create ideas action.
- Generation producing exactly three idea cards (title + description), with graceful padding/truncation to exactly three regardless of upstream response shape.
- Clear loading state during generation and clear, prompt-preserving error state on failure.
- Favorite toggle per idea card, multi-select, persisted via `localStorage` across refreshes.
- Single-screen layout, responsive across mobile and desktop widths.

### 6.2 Out of Scope for MVP

- Generation history / past-prompts view — deferred; a candidate for v1.1 based on learner feedback. `[NOTE FOR PM: flagged in architecture memlog as OQ-3 — revisit if learners ask for it]`
- Analytics/telemetry and prompt-engineering/templating — deferred to v1.1.
- Iterative idea refinement, export/share of ideas, and a hook into the broader BMAD toolchain (e.g., turning a favorited idea directly into a `bmad-product-brief` or `bmad-prd` run) — deferred to v2+. `[NOTE FOR PM: the BMAD-toolchain hook is emotionally load-bearing for the product's own stated vision in §1 — revisit if timeline permits]`

## 7. Open Questions

1. Should a future version let a favorited idea launch directly into `bmad-product-brief` or `bmad-prd`, closing the loop this PRD's vision (§1) gestures at? Deferred to v2+ per §6.2.
2. Should generation history be added in v1.1, and if so, does it change the "disposable by default" framing in §1?
3. Is the LLM provider (assumed OpenAI-compatible per architecture AD-8) a firm decision, or should this PRD stay silent on provider to preserve the architecture's provider-agnostic stance?

## 8. Assumptions Index

- §4.1 — "Meaningful text" validation means non-empty, non-whitespace only; no minimum character threshold. Confirmed with user.
- §4.1 — On a short generation response (fewer than 3 ideas), the app pads with generic filler ideas rather than erroring. Confirmed with user.
- §4.2 — `localStorage` capacity is sufficient for MVP favorite volumes; no eviction/quota handling specified.
- §7 — LLM provider choice is out of this PRD's scope; architecture AD-8 keeps it pluggable.
