---
stepsCompleted:
  - validate-prerequisites
  - design-epics
  - create-stories
inputDocuments:
  - docs/bmad-idea-launcher-prd.md
  - _bmad-output/planning-artifacts/bmad-idea-launcher-architecture/ARCHITECTURE-SPINE.md
---

# BMAD Idea Launcher - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for BMAD Idea Launcher, decomposing the requirements from the PRD and the architecture spine into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: The user can enter a short problem or experiment prompt in a single text input field.
FR2: The system can generate exactly three starter ideas when the user submits a non-empty prompt.
FR3: Each generated idea is presented as a card containing a title and a short description.
FR4: The user can mark an idea as a favorite and remove that favorite if they change their mind.
FR5: The app stores the set of favorite selections in browser storage so they persist across page refreshes.
FR6: The app presents the input, generation action, and results on a single screen.
FR7: The layout adapts to common desktop and mobile widths without overlapping or clipping core content.

### NonFunctional Requirements

NFR1: The generation and rendering flow should feel fast and lightweight, completing in under 30 seconds for typical use.
NFR2: The interface should be easy to understand for a first-time user with no onboarding required.
NFR3: The experience should remain usable and readable on both mobile and desktop widths.
NFR4: The implementation should stay lightweight and aligned with a simple front-end learning artifact rather than a production-grade ideation platform.

### Additional Requirements

- The backend should expose a single POST endpoint for idea generation that accepts a prompt and returns exactly three ideas.
- The app should enforce the invariant that each generation produces exactly three idea cards, padding or truncating as needed.
- The frontend should use browser storage as the canonical store for favorite selections and restore that state on page load.
- The experience should remain single-screen and avoid additional navigation or hidden steps.
- Errors during generation should be surfaced clearly to the user while preserving the prompt so the user can retry.

### UX Design Requirements

- No separate UX design contract was provided for this workflow, so detailed visual design and interaction polish are deferred.
- The implementation should preserve a simple, readable layout that supports the core prompt-to-ideas flow without extra onboarding.

### FR Coverage Map

FR1: Epic 1 - prompt capture and submission flow
FR2: Epic 1 - generation flow and response normalization
FR3: Epic 1 - idea card presentation
FR4: Epic 2 - favorite toggle behavior
FR5: Epic 2 - favorite persistence in browser storage
FR6: Epic 3 - single-screen app experience
FR7: Epic 3 - responsive layout across device widths

## Epic List

### Epic 1: Capture and Generate Starter Ideas

Users can enter a prompt and immediately receive a clear set of three starter ideas that are easy to compare.
**FRs covered:** FR1, FR2, FR3

### Epic 2: Save and Review Promising Ideas

Users can mark ideas as favorites and keep those selections across refreshes while evaluating options.
**FRs covered:** FR4, FR5

### Epic 3: Deliver a Lightweight Single-Screen Experience

Users can complete the full flow on one responsive screen without friction or extra navigation.
**FRs covered:** FR6, FR7

## Epic 1: Capture and Generate Starter Ideas

Users can enter a prompt and immediately receive a clear set of three starter ideas that are easy to compare.

### Story 1.1: Enter a Prompt and Submit a Generation Request

As a BMAD learner,
I want to enter a prompt and submit it for idea generation,
So that I can quickly move from a rough problem to a first concept set.

**Acceptance Criteria:**

**Given** the app is loaded and the prompt field is visible
**When** the user enters a non-empty prompt and clicks Generate ideas
**Then** the app starts the generation flow and shows a clear loading or busy state
**And** the app prevents submission until the prompt contains meaningful text

### Story 1.2: Render Exactly Three Starter Idea Cards

As a learner,
I want the app to display exactly three idea cards from a generation request,
So that I can compare a concise set of starter directions.

**Acceptance Criteria:**

**Given** a valid prompt has been submitted
**When** the generation response is received
**Then** the app renders exactly three idea cards
**And** each card shows a title and a short description
**And** the app handles responses that contain too many or too few ideas by normalizing to three cards

### Story 1.3: Show Clear Feedback When Generation Fails

As a learner,
I want the app to explain generation failures clearly,
So that I can recover quickly and retry without losing context.

**Acceptance Criteria:**

**Given** the generation request fails or returns an error
**When** the user is returned to the page
**Then** the app displays a short user-friendly error message
**And** the prompt remains intact so the user can try again
**And** the app does not leave the interface in a broken or silent state

## Epic 2: Save and Review Promising Ideas

Users can mark ideas as favorites and keep those selections across refreshes while evaluating options.

### Story 2.1: Toggle Favorite State for an Idea

As a learner,
I want to mark ideas as favorites and remove that selection later,
So that I can keep track of the most promising directions.

**Acceptance Criteria:**

**Given** the app has displayed one or more idea cards
**When** the user clicks the favorite control for an idea
**Then** the card is visually marked as a favorite
**And** clicking the same control again removes that favorite state
**And** the user can favorite more than one idea at the same time

### Story 2.2: Persist Favorite Selections in Browser Storage

As a learner,
I want my favorite selections to persist after a refresh,
So that I do not lose the ideas I have already chosen.

**Acceptance Criteria:**

**Given** the user has marked one or more ideas as favorites
**When** the page is refreshed
**Then** the same ideas appear as favorites on reload
**And** the favorite state is restored without requiring a backend or account

## Epic 3: Deliver a Lightweight Single-Screen Experience

Users can complete the full flow on one responsive screen without friction or extra navigation.

### Story 3.1: Keep the Core Flow on a Single Screen

As a first-time user,
I want the prompt input, generation action, and results to appear in one view,
So that I can complete the experience without navigation or setup.

**Acceptance Criteria:**

**Given** the app is opened in a browser
**When** the user starts the idea-generation flow
**Then** the prompt input, action, and result area are all available on the same screen
**And** the user can complete the core flow without moving to another page or view

### Story 3.2: Support Responsive Layouts for Mobile and Desktop

As a user,
I want the interface to remain usable on mobile and desktop screens,
So that I can use the app comfortably on different devices.

**Acceptance Criteria:**

**Given** the app is viewed at common mobile and desktop widths
**When** the layout is rendered
**Then** the main controls remain visible and tappable
**And** the content does not overlap or clip in a way that blocks the core flow
