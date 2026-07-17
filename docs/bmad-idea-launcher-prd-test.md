---
title: BMAD Idea Launcher
created: 2026-07-13
updated: 2026-07-13
---

# PRD: BMAD Idea Launcher

_Working title — confirm._

## 0. Document Purpose

This PRD captures the MVP for BMAD Idea Launcher, a single-screen learning experiment that turns a short prompt into three starter ideas. It is written for the builder, BMAD workflow owners, and anyone reviewing implementation scope. It builds on the existing brief and feature list rather than duplicating them.

## 1. Vision

BMAD Idea Launcher helps a learner or builder quickly turn a rough prompt into three concrete starting ideas. The product is intentionally tiny: one input, one action, three outputs, and one favorite selection. The value is not sophisticated idea management; it is giving someone a fast, repeatable first step in the BMAD ideation workflow.

## 2. Target User

### 2.1 Jobs To Be Done

- Convert a rough problem prompt into three concrete early concepts quickly.
- Experience the BMAD ideation flow in a lightweight, hands-on tool.
- Compare possible ideas without leaving the page or setting up a larger product.

### 2.2 Non-Users (v1)

- Users who need persistent idea databases, collaboration, or multi-user workflows.
- Users who need AI-generated content beyond simple starter ideas.

### 2.3 Key User Journeys

- **UJ-1. Prompt to starter ideas**
  - **Persona + context:** A BMAD learner or developer has a problem prompt and wants a fast first-pass concept set.
  - **Entry state:** The user lands on a single page with an empty prompt field.
  - **Path:** The user enters a prompt, clicks Generate ideas, reviews the three idea cards, and optionally marks one as a favorite.
  - **Climax:** The page shows three clearly structured ideas and confirms the user’s favorite selection.
  - **Resolution:** The user can iterate with a new prompt or keep the current result set.

## 3. Glossary

- **Prompt** — The short input text provided by the user describing a problem or experiment.
- **Idea Card** — One of the three generated starter concepts shown on the page.
- **Favorite** — The single idea chosen by the user as the most promising.
- **Generation** — The action that creates the three starter ideas from the prompt.
- **MVP** — The initial version of the product scoped for a one-screen, single-session experience.

## 4. Features

### 4.1 Prompt Capture and Idea Generation

**Description:** The product offers a simple entry point where a user types a prompt and triggers generation of three starter ideas. The experience should feel immediate and low-friction. Realizes UJ-1.

**Functional Requirements:**

#### FR-1: Prompt entry

The user can enter a short problem or experiment prompt in a single text input field.

**Consequences (testable):**

- The interface displays a clearly labeled input field with supporting placeholder text.
- The input accepts text and does not require additional setup before generation.

#### FR-2: Idea generation

The system can generate exactly three starter ideas when the user submits a non-empty prompt.

**Consequences (testable):**

- The user sees three idea cards after clicking Generate ideas.
- The app does not generate zero or more than three cards for a single submission.

#### FR-3: Idea presentation

Each generated idea is presented as a card containing a title and a short description.

**Consequences (testable):**

- Every card displays a title and a one-sentence description.
- The layout remains readable on both small and large screens.

### 4.2 Favorite Selection

**Description:** The user can mark any number of ideas as favorites. The interface should make each favorite choice easy to understand at a glance. Realizes UJ-1.

**Functional Requirements:**

#### FR-4: Favorite toggle

The user can mark an idea as a favorite and remove that favorite if they change their mind.

**Consequences (testable):**

- Multiple ideas can be marked as favorites at the same time.
- Each favorite card is visually differentiated from the other cards.

#### FR-5: Persistent favorite state

The app stores the set of favorite selections in browser storage so they persist across page refreshes.

**Consequences (testable):**

- Reloading the page preserves the selected favorites until the user changes them.
- The app does not require a backend to support this persistence.

### 4.3 Responsive Single-Screen Experience

**Description:** The MVP should feel lightweight and clear on both desktop and mobile widths. The main flow should remain one-screen and require no additional navigation. Realizes UJ-1.

**Functional Requirements:**

#### FR-6: Single-screen layout

The app presents the input, generation action, and results on a single screen.

**Consequences (testable):**

- Users can complete the core flow without navigating to another view.
- The screen remains understandable without hidden steps or extra panels.

#### FR-7: Responsive behavior

The layout adapts to common desktop and mobile widths without overlapping or clipping core content.

**Consequences (testable):**

- The interface remains usable at narrow widths.
- Core controls remain visible and tappable on mobile.

**Feature-specific NFRs:**

- The experience should feel fast and lightweight, with generation and rendering completed in under 30 seconds for typical use.
- The interface should be easy to understand for a first-time user with no onboarding required.

## 5. Non-Goals (Explicit)

- The MVP will not include backend API integration beyond the LLM-based generation flow if that is used.
- The MVP will not include advanced persistence beyond browser-side storage for favorites and recent results.
- The MVP will not include full idea management features such as edit, delete, tag, search, or export.
- The MVP will not include authentication, multi-user collaboration, or shared workspaces.

## 6. MVP Scope

### 6.1 In Scope

- One prompt input field.
- A Generate ideas action that produces exactly three idea cards.
- A favorite selection mechanism for one card.
- A single-screen responsive layout.
- Minimal styling that keeps the focus on the ideas.

### 6.2 Out of Scope for MVP

- Fully custom prompt engineering or advanced LLM orchestration beyond simple generation.
- Long-term storage or account-based persistence.
- Advanced idea organization or workflow features.
- Analytics, onboarding, or admin tooling.

## 7. Success Metrics

**Primary**

- **SM-1:** A first-time user can enter a prompt, generate three ideas, and mark a favorite in under two minutes without assistance. Validates FR-1, FR-2, FR-3, FR-4.
- **SM-2:** The core experience is usable on desktop and mobile widths without layout failure. Validates FR-6, FR-7.

**Secondary**

- **SM-3:** The app is understandable as a BMAD learning artifact, with users recognizing the idea-generation flow as a quick experiment rather than a full product. Validates FR-1 through FR-7.

**Counter-metrics**

- **SM-C1:** The MVP should not become a bloated idea-management tool; feature complexity should stay low to preserve the learning goal.

## 8. Open Questions

1. Which LLM provider or service will power the idea generation flow?
2. What level of prompt templating or response formatting is needed to keep the output consistent?
3. Is there any preferred visual style or brand language for the app beyond the existing brief?

## 9. Assumptions Index

- [ASSUMPTION: The MVP will use a lightweight front-end stack such as plain HTML/CSS/JavaScript.] This keeps the implementation aligned with the 1–2 hour build goal.
- [ASSUMPTION: The MVP is meant as a learning artifact and demo, not a production-grade ideation platform.] This shapes the scope and feature set.
- [ASSUMPTION: The app will use browser storage for favorite persistence and optionally recent results.] This supports the one-screen and low-friction design goal.

## Stories

- **Story-1:** As a BMAD learner, I can enter a prompt and generate three starter ideas so I can quickly move from a rough problem to a first concept set.
  - **Acceptance:** The user can submit a prompt and see exactly three idea cards.
- **Story-2:** As a learner, I can favorite multiple ideas so I can keep several promising directions in view.
  - **Acceptance:** The user can select more than one idea as favorite and see a clear visual state change for each.
- **Story-3:** As a first-time user, I can use the app on a phone or desktop so I can experience the flow without friction.
  - **Acceptance:** The main interaction remains usable and readable at common mobile and desktop widths.
