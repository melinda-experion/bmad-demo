---
title: BMAD Idea Launcher Architecture Spine
altitude: MVP (Initiative → Shipment)
status: draft
created: 2026-07-13
updated: 2026-07-13
---

# BMAD Idea Launcher: Architecture Spine

## Design Paradigm

**Single-Page Application (SPA) with Local State & Browser Persistence**

A lightweight, stateless-by-design web application that encapsulates three core concerns:

1. **Prompt intake** — capture and validate user input
2. **Idea generation** — call an LLM provider via a backend service
3. **Idea display & interaction** — render cards, manage favorite state, persist to local storage

The paradigm prioritizes simplicity and encapsulation: no shared mutable state, clear separation between client concerns (UI/UX) and external dependencies (LLM). Favorites and recent results live in browser storage; the session owns generation state; the LLM call is a discrete boundary.

---

## Invariants

### AD-1: Prompt-Driven, Stateless Generation

**Binds:** Every generation flow starts with a valid, non-empty prompt; the system does not cache or reuse previous prompts as default state.  
**Prevents:** Accidental re-generation of stale ideas; confusion between user intent and app memory.  
**Rule:** On each `Generate` action, validate the prompt, call the LLM, render three new cards, and clear prior results unless explicitly saved as favorites.

---

### AD-2: Exactly Three Ideas per Generation

**Binds:** The LLM request and response handling enforce exactly three idea cards per prompt submission.  
**Prevents:** UI layout drift; inconsistent card rendering; user confusion about why the number varies.  
**Rule:** If the LLM returns fewer than three ideas, pad with a fallback template. If more than three, truncate to three. Log any deviation as a warning for observability.

---

### AD-3: Favorite State Ownership & Persistence

**Binds:** The browser's `localStorage` is the canonical store for favorite selections; the server does not track or validate favorites.  
**Prevents:** Loss of favorites across page reloads; complexity of server-side persistence for an MVP.  
**Rule:** On every favorite toggle, write the updated favorite set to `localStorage` immediately. On page load, hydrate the favorite state from `localStorage` and visually mark favorited cards.

---

### AD-4: Single-Screen, No Navigation

**Binds:** The entire interaction flow (prompt input, generation, results, favorite toggle) occurs on one route/view. No modal dialogs, tab panels, or multi-page flows.  
**Prevents:** Navigation confusion; broken back-button behavior; accidental loss of results.  
**Rule:** All content renders on a single DOM tree. Use CSS or in-page visibility toggles for conditional display (e.g., show results only after generation).

---

### AD-5: Responsive Layout Constraint

**Binds:** The layout adapts to common breakpoints (mobile ≤600px, tablet 601–1000px, desktop >1000px); all controls remain tappable and visible without horizontal scroll.  
**Prevents:** Broken mobile experience; content clipping on narrow widths.  
**Rule:** Use a mobile-first CSS approach with `min-width` media queries. Test against common device widths (375px, 768px, 1920px). Favor vertical stacking on mobile; grid/flex on desktop.

---

### AD-6: Frontend Stack

**Binds:** The frontend uses vanilla HTML, CSS, and JavaScript (no build step required) or a minimal single-file framework (e.g., Alpine.js, Preact) to keep the artifact lightweight and aligned with the 1–2 hour build goal.  
**Prevents:** Complexity creep (webpack, Node modules, transpilation); deployment friction for a learning artifact.  
**Rule:** If using a framework, it must be <50KB minified and loadable via CDN. No npm build step. All logic must run in the browser; no Node.js runtime required.

---

### AD-7: Backend Boundary & LLM Integration

**Binds:** The backend is a thin, stateless adapter that accepts a prompt and returns exactly three ideas. It does not manage sessions, user profiles, or idea history.  
**Prevents:** Scope creep into full backend complexity; loss of the MVP spirit.  
**Rule:** Backend exposes a single POST endpoint `/api/ideas` (or equivalent) that takes `{prompt: string}` and returns `{ideas: [{title, description}, ...]}` with exactly three items. All state and rendering logic lives on the client.

---

### AD-8: LLM Provider Abstraction

**Binds:** The backend wraps the LLM call behind a provider-agnostic interface so swapping providers (OpenAI, Anthropic, local, etc.) does not require frontend changes.  
**Prevents:** Tight coupling to a single LLM; fragility if provider API changes.  
**Rule:** Define a provider abstraction that the backend uses internally. Provide environment-based configuration (e.g., `LLM_PROVIDER` env var) to select the active provider at startup. Currently, [ASSUMPTION: OpenAI] is the default, but the contract allows extension.

---

### AD-9: Error Handling & Observability

**Binds:** Generation failures (network, LLM timeout, provider error) are surfaced to the user with a clear, brief message and a retry affordance.  
**Prevents:** Silent failures; user confusion; lost context on retry.  
**Rule:** On error, display a user-friendly message (e.g., "Ideas couldn't generate. Try again.") and keep the prompt intact so the user can resubmit. Log errors server-side for debugging. Do not expose raw API errors to the user.

---

### AD-10: Idea Card Data Model

**Binds:** Each idea is a discrete record with exactly two fields: `title` (string, max 60 chars) and `description` (string, max 200 chars). Additional fields (id, timestamp, source) are optional and do not appear in the UI.  
**Prevents:** Unbounded schema drift; UI layout surprises; rendering complexity.  
**Rule:** The backend ensures every idea matches the schema. The frontend renders only `title` and `description`; extra fields are ignored. The client uses title + description as the unique key for a card (for favorite lookup).

---

### AD-11: Favorite Toggle Semantics

**Binds:** A user can favorite multiple ideas from the same generation; favorites persist across sessions via `localStorage`; a favorite idea is visually distinct (e.g., filled star, highlight).  
**Prevents:** Loss of context when refreshing; ambiguity about which ideas are marked.  
**Rule:** Favorite state is a boolean per card (not a rank or score). The client stores favorites as an array of `{title, description, generatedAt}` objects (or a hash for lookup speed) in `localStorage`. On page load, compare incoming ideas to stored favorites by title+description match.

---

## Seed (Initial State)

### Technology Stack

| Layer          | Choice                                                             | Rationale                                                                                   |
| -------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **Frontend**   | HTML + CSS + Vanilla JS (or Alpine.js)                             | Minimal, learnable, no build step.                                                          |
| **Backend**    | Node.js (Express) or Python (FastAPI/Flask)                        | Light, simple REST endpoint. [ASSUMPTION: Node.js with Express chosen for rapid iteration.] |
| **LLM**        | OpenAI API (GPT-4 or equivalent)                                   | Reliable, fast, cost-effective for MVP. Pluggable via AD-8.                                 |
| **Deployment** | Static frontend (CDN or file) + backend on Heroku / Render / local | Fast iteration, minimal ops.                                                                |
| **Storage**    | Browser `localStorage` (client-side only)                          | No server-side DB for MVP. Favorites are per-browser, per-device.                           |

---

### Data Flow

```mermaid
graph LR
  User["👤 User Input"]
  Prompt["📝 Prompt Field"]
  Generate["🎯 Generate Button"]
  Validate["✓ Validate"]
  LLM["🧠 LLM Call"]
  Response["🔄 {ideas: [...]"]
  Render["🎨 Render Cards"]
  LocalStorage["💾 localStorage"]
  Favorite["⭐ Toggle Favorite"]

  User -->|types prompt| Prompt
  Prompt -->|submit| Generate
  Generate -->|send| Validate
  Validate -->|POST /api/ideas| LLM
  LLM -->|{ideas: 3}| Response
  Response -->|render| Render
  Render -->|show cards| User
  User -->|click star| Favorite
  Favorite -->|write| LocalStorage
  LocalStorage -->|on load, hydrate| Render
```

---

### Component Sketch

**Frontend (Single Page)**

- `Header` — branding, minimal nav
- `PromptInput` — text field + button
- `IdeaCardList` — three `IdeaCard` items
- `IdeaCard` — title, description, favorite toggle
- `ErrorBoundary` — error message display
- `LoadingState` — spinner or skeleton during generation

**Backend (Thin Adapter)**

- `POST /api/ideas` — accept prompt, call LLM, return ideas
- `LLMProvider` — abstraction over OpenAI (or other provider)
- `ErrorHandler` — wrap and log errors, return user-safe responses

---

## Deferred (Not Yet Decided)

### D-1: Exact Visual Style & Branding

**Why deferred:** The architectural decisions don't depend on color, typography, or layout details. UX design (bmad-ux) will specify these.  
**Revisit when:** UX design is in progress; brand guidelines are available.

---

### D-2: Backend Hosting & Scaling

**Why deferred:** The MVP assumes a simple, single-instance backend. Scaling, multi-region, or auto-scaling policies are out of scope.  
**Revisit when:** Traffic testing shows a need; production launch is planned.

---

### D-3: Analytics & Telemetry

**Why deferred:** The MVP does not include user tracking, funnel analysis, or telemetry. These are valuable for post-launch learning but not required for the MVP spine.  
**Revisit when:** Post-launch metrics review; feature iteration decisions require data.

---

### D-4: Multi-Language Support (i18n)

**Why deferred:** The MVP targets a single language (English). i18n logic, translation keys, and locale switching are out of scope.  
**Revisit when:** International audience or multi-language requirement emerges.

---

## Assumptions & Gaps

### [ASSUMPTION: OpenAI API Integration]

The backend uses the OpenAI API for idea generation. If the team prefers a different provider (Anthropic, Cohere, local LLM), swap the `LLMProvider` implementation without changing the rest of the spine.

### [ASSUMPTION: No Authentication Required for MVP]

The app does not require user login or per-user state. All users share the same public interface.

### [ASSUMPTION: Frontend Runs in Modern Browsers]

The app targets browsers released in the last 2–3 years (ES2020 support, `localStorage` support, flexbox/grid support).

### [ASSUMPTION: Prompt Templating is Minimal]

The backend does not manipulate or augment the user's prompt—it sends it directly to the LLM. No hidden instructions, no domain-specific injection.

### [OPEN] How Many Ideas Should Fall Back on LLM Failure?

If the LLM returns fewer than three ideas, should the app pad with generic templates, repeat ideas, or show an error? This is a UX call that should be clarified before implementation.

---

## Rationale & Tradeoffs

### Why Single-Page, Not Multi-Step?

A multi-step flow (e.g., "prompt → configure → generate → review") adds complexity and context switching. The MVP is intentionally one screen to reduce friction and keep the scope tight.

### Why Local Storage, Not a Backend Database?

Server-side persistence would require user accounts, a database, API calls, and deployment complexity. Local storage keeps the MVP lean and learnable. Favorites stay private to the device.

### Why Exactly Three Ideas?

Three ideas is enough to show variety without overwhelming; it mirrors design thinking templates (e.g., "lazy, realistic, ambitious"). One idea feels incomplete; five or more invites decision fatigue.

### Why Vanilla Frontend or Minimal Framework?

No build step, no npm complexity, no dependency churn. A single HTML file (or small set of files) can be understood in 10 minutes and modified without tooling knowledge. This aligns with the BMAD learning goal.

### Why Thin Backend, Not Serverless?

Serverless (AWS Lambda, Google Cloud Functions) adds configuration and vendor lock-in. A simple Node/Python server on Heroku or Render is more portable and equally fast for a toy MVP.

---

## Next Steps (Downstream)

1. **UX Design** (`bmad-ux`) — Specify wireframes, typography, color, responsive behavior for each breakpoint.
2. **Epics & Stories** (`bmad-create-epics-and-stories`) — Break the spine into implementation stories (backend, frontend, testing).
3. **Implementation** (`bmad-dev-story`) — Execute stories in parallel or sequence, using the spine as the consistency contract.
4. **Testing** — Define acceptance criteria for each story; test against the invariants (e.g., "exactly three ideas are always rendered").
5. **Post-Launch** — Measure success metrics (SM-1, SM-2 from the PRD); update the spine if new invariants emerge.

---

## Related Documents

- [Product Brief](../../docs/bmad-idea-launcher-brief.md)
- [PRD](../../docs/bmad-idea-launcher-prd.md)
- [Architecture Memlog](.memlog.md)
- [System Design Deep Dive](./SYSTEM-DESIGN.md)
