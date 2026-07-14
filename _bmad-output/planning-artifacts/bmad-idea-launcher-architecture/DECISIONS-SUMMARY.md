---
title: Architecture Decisions Summary & Next Steps
status: draft
created: 2026-07-13
updated: 2026-07-13
---

# BMAD Idea Launcher: Architecture Summary & Next Steps

## Overview

The BMAD Idea Launcher architecture defines a lightweight, single-screen web application that turns a user prompt into three starter ideas using an LLM. This document summarizes key decisions and charts the path to implementation.

---

## The Architecture in One Sentence

**A stateless SPA frontend** talks to a **thin backend adapter** that calls an LLM, returns exactly three ideas, and stores favorites in the browser.

---

## Key Architecture Decisions (11 Total)

| #         | Decision                                                | Impact                                        |
| --------- | ------------------------------------------------------- | --------------------------------------------- |
| **AD-1**  | Prompt-driven, stateless generation                     | Every flow starts fresh; no caching           |
| **AD-2**  | Exactly three ideas per generation                      | Fixed UI layout, predictable behavior         |
| **AD-3**  | Favorite state in localStorage                          | No backend DB needed; per-device storage      |
| **AD-4**  | Single-screen, no navigation                            | Reduced cognitive load, tight UX focus        |
| **AD-5**  | Responsive layout (mobile-first)                        | Works on 375px–1920px widths                  |
| **AD-6**  | Vanilla JS or minimal framework                         | No build step; learnable codebase             |
| **AD-7**  | Thin backend + LLM abstraction                          | Pluggable LLM provider                        |
| **AD-8**  | LLM provider abstraction                                | Easy to swap OpenAI ↔ Anthropic, etc.         |
| **AD-9**  | User-friendly error handling                            | Preserve prompt on retry                      |
| **AD-10** | Fixed idea schema (title + description only)            | Predictable rendering, no schema drift        |
| **AD-11** | Favorite toggle semantics (boolean, multiple favorites) | Clear visual state, persistent across reloads |

**Read the full decisions in:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md)

---

## Technical Stack (Recommended)

| Layer          | Technology                                      | Why                                      |
| -------------- | ----------------------------------------------- | ---------------------------------------- |
| **Frontend**   | HTML + CSS + Vanilla JS                         | Minimal, no build step, learnable        |
| **Backend**    | Node.js + Express (or Python + FastAPI)         | Light, simple REST endpoint              |
| **LLM**        | OpenAI API (GPT-4)                              | Reliable, fast, pluggable via AD-8       |
| **Storage**    | Browser localStorage                            | No DB, no user accounts, MVP-appropriate |
| **Deployment** | Render or Heroku (backend) + Netlify (frontend) | Fast iteration, low ops burden           |

---

## What Changed from Brief → PRD → Architecture

### Brief Promised

- ✅ Single prompt input
- ✅ Generate three ideas
- ✅ Display as cards
- ✅ Mark favorite(s)
- ✅ One-screen experience
- ✅ Responsive layout
- ✅ Buildable in 1–2 hours

### PRD Detailed

- ✅ Features FR-1 through FR-7 (prompt capture, generation, presentation, favorites, persistence, single-screen, responsive)
- ✅ Acceptance criteria for each feature
- ✅ Success metrics (SM-1, SM-2)

### Architecture Crystallized

- ✅ **How** favorites persist (localStorage, not server)
- ✅ **How** the backend is organized (stateless adapter, provider abstraction)
- ✅ **What** happens on errors (preserve prompt, retry affordance)
- ✅ **Why** exactly three ideas (fixed layout, no variation)
- ✅ **Where** state lives (client for UI, browser storage for favorites)

---

## Open Questions (4 Total)

| #        | Question                                            | Status   | Owner            |
| -------- | --------------------------------------------------- | -------- | ---------------- |
| **OQ-1** | How to handle LLM returning <3 ideas?               | Deferred | UX + Dev team    |
| **OQ-2** | Node + Express or Python + FastAPI?                 | Deferred | Tech lead        |
| **OQ-3** | Should app track generation history?                | Deferred | Post-MVP         |
| **OQ-4** | What if localStorage is cleared (private browsing)? | Accepted | Known limitation |

**Resolution path:** Each open question is logged in [.memlog.md](./.memlog.md) with recommended next steps.

---

## Assumptions (4 Total)

| #        | Assumption                                     | Mitigating Factor                  |
| -------- | ---------------------------------------------- | ---------------------------------- |
| **AS-1** | OpenAI is the LLM provider                     | AD-8 allows easy swapping          |
| **AS-2** | No authentication required for MVP             | Can add later if multi-user needed |
| **AS-3** | Frontend targets modern browsers (ES2020+)     | Aligns with current dev practices  |
| **AS-4** | Prompt is sent directly to LLM (no templating) | Keeps backend simple               |

---

## The Data Flow (Visual)

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  1. User enters prompt                                        │
│     ↓                                                          │
│  2. Frontend validates & disables button                      │
│     ↓                                                          │
│  3. Frontend POST /api/ideas { prompt }                       │
│     ↓ (backend)                                               │
│  4. Backend validates prompt                                  │
│     ↓                                                          │
│  5. Backend → OpenAI (or other provider) + retry logic        │
│     ↓ (LLM returns array of 1–3+ ideas)                       │
│  6. Backend ensures exactly 3 ideas (pad or truncate)         │
│     ↓                                                          │
│  7. Backend returns JSON { ideas: [...] }                     │
│     ↓ (frontend)                                              │
│  8. Frontend renders three IdeaCard components                │
│     ↓                                                          │
│  9. Frontend hydrates favorite state from localStorage        │
│     ↓                                                          │
│ 10. User sees three cards, some may be visually marked ★      │
│     ↓                                                          │
│ 11. User clicks favorite button on a card                     │
│     ↓                                                          │
│ 12. Frontend toggles favorite in memory + localStorage        │
│     ↓                                                          │
│ 13. Frontend re-renders card with new visual state            │
│     ↓                                                          │
│ 14. On page reload, favorites are restored from localStorage  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## File Organization

```
_bmad-output/
└─ planning-artifacts/
   └─ bmad-idea-launcher-architecture/
      ├─ ARCHITECTURE-SPINE.md          ← Main deliverable
      ├─ .memlog.md                     ← Decision log (decisions, assumptions, questions)
      ├─ SYSTEM-DESIGN.md               ← Implementation guide (API, components, deployment)
      ├─ DECISIONS-SUMMARY.md           ← This file (overview + next steps)
      └─ C4-DIAGRAMS.md                 ← System context, container, component views (optional)
```

---

## Consistency Contracts (Invariants)

These are the "rules" that any implementation must respect:

1. **Validation & Generation** — Every prompt is validated; exactly three ideas are returned.
2. **Favorite Persistence** — Favorites survive page reloads via localStorage.
3. **Single Screen** — No navigation; all content on one route.
4. **Responsive** — Works at 375px–1920px widths.
5. **Error Recovery** — Errors preserve prompt; retry is simple.
6. **Frontend Independence** — No auth, no session tracking on client.
7. **Backend Simplicity** — Single POST endpoint; no CRUD, no user management.

Any deviation from these invariants must be logged in the memlog and reviewed before implementation.

---

## Success Criteria (from PRD, validated by architecture)

- **SM-1:** First-time user can enter prompt, generate ideas, and mark favorite **in <2 min without help.**  
  → Architecture supports this via single-screen, no-setup flow.

- **SM-2:** App is usable on **desktop and mobile widths without layout failure.**  
  → Responsive layout via AD-5; mobile-first CSS ensures this.

---

## Downstream Workflows

### Immediate (Next Steps)

1. **bmad-create-epics-and-stories** — Break the spine into epics & user stories
   - Epic 1: Backend setup (provider abstraction, /api/ideas endpoint, error handling)
   - Epic 2: Frontend setup (component tree, state management, localStorage)
   - Epic 3: Integration & testing (E2E, load testing, deployment)

2. **bmad-ux** — Finalize wireframes, typography, color, responsive breakpoints
   - Refine the IdeaCard appearance
   - Specify favorite button visual state
   - Define error message styling

3. **bmad-dev-story** — Execute stories in sprint
   - Developers pull stories from the backlog
   - Use this architecture spine as the consistency contract
   - Reference AD-n IDs in commit messages and PR descriptions

### Mid-Term (v1.1)

- Analytics & observability (error tracking, user funnels)
- Prompt templating / engineering for better idea quality
- History view (see prior generations)

### Long-Term (v2+)

- Idea refinement (iterative follow-up prompts)
- Export & share (JSON/PDF download, shareable links)
- Collaborative brainstorming (multi-user sessions)
- BMAD integration (button to create PRD from favorite idea)

---

## Reviewing & Updating the Architecture

### For Implementation Teams

- **Read:** ARCHITECTURE-SPINE.md first (the invariants).
- **Reference:** SYSTEM-DESIGN.md for API contracts, components, and deployment.
- **Log:** Any deviations or new decisions in .memlog.md with a `decision` entry.
- **Avoid:** Changing an `AD-n` ID; amend the Rule if you find a flaw.

### For Architecture Reviews

- **Checklist:** Are all 11 ADs respected in the code?
- **Gaps:** Are there structural dimensions left undecided (e.g., deployment, ops)?
- **Assumptions:** Which [ASSUMPTIONs] still hold? Which are stale?

---

## Tradeoffs Made

### Why localStorage Over Server Database?

- **Pro:** No DB setup, no user accounts, no ops burden.
- **Con:** Favorites are per-device, no cloud sync.
- **Verdict:** MVP-appropriate; v2 can add cloud sync if needed.

### Why Thin Backend Over Serverless?

- **Pro:** Easier to understand, no cold start, portable.
- **Con:** Slightly more infrastructure knowledge.
- **Verdict:** Learning artifact; simplicity > minimal ops.

### Why Exactly Three Ideas?

- **Pro:** Design-thinking templates use three concepts; fixed layout.
- **Con:** User may want 2 or 5 ideas.
- **Verdict:** MVP constraint; v2 can add customization.

### Why Vanilla JS Over React/Vue?

- **Pro:** No build step, no node_modules churn, learnable.
- **Con:** Manual DOM updates, more boilerplate.
- **Verdict:** BMAD learning goal; any frontend dev can read it in 10 min.

---

## Common Implementation Pitfalls (Watch Out!)

1. **Temptation to add a backend DB early**  
   → Resist. localStorage is the contract. Add DB only if persistence post-MVP demands it.

2. **Prompt engineering without the contract**  
   → All LLM calls go through the provider abstraction (AD-8). Don't let prompts vary per request.

3. **Favorites not persisted on page refresh**  
   → Test localStorage hydration (AD-3) in E2E suite.

4. **Rendering more than three ideas**  
   → Enforce truncation at backend and frontend as a defensive measure (AD-2).

5. **Error messages leaking raw API errors to the user**  
   → Always wrap and sanitize (AD-9).

6. **Skipping responsive testing**  
   → Test at 375px, 768px, 1920px minimum. Use device emulation in browser dev tools.

---

## Appendix: Quick Reference

### Architecture Decision IDs

- **AD-1** — Stateless generation
- **AD-2** — Exactly three ideas
- **AD-3** — localStorage favorites
- **AD-4** — Single-screen
- **AD-5** — Responsive layout
- **AD-6** — Vanilla JS / minimal framework
- **AD-7** — Thin backend
- **AD-8** — LLM provider abstraction
- **AD-9** — Error handling
- **AD-10** — Fixed idea schema
- **AD-11** — Favorite toggle semantics

### Key Files

- **ARCHITECTURE-SPINE.md** — The consistency contract (read first)
- **.memlog.md** — Decision log (reference for context)
- **SYSTEM-DESIGN.md** — Implementation details (read during sprint)

### Command to Amend Architecture

If you find a gap or need to change an AD:

```bash
# Log the change in .memlog.md
uv run _bmad/scripts/memlog.py append \
  --workspace "_bmad-output/planning-artifacts/bmad-idea-launcher-architecture" \
  --type decision \
  --text "AD-12: [new decision title] — [binds/prevents/rule]"

# Then update ARCHITECTURE-SPINE.md with the new AD
```

---

## Sign-Off & Next Steps

**Architecture Status:** ✅ **Ready for Implementation**

**Recommended Next Workflow:**

1. Run **bmad-create-epics-and-stories** to break into user stories
2. Run **bmad-ux** to finalize visual design
3. Run **bmad-dev-story** for each story in the sprint

**Questions?** Refer to .memlog.md (open questions are logged). Unresolved blockers should be triaged during sprint planning.

---

**Architecture Spine Created:** 2026-07-13  
**Status:** Draft (ready for team review)  
**Next Review:** Post-UX-design; pre-epic-breakdown
