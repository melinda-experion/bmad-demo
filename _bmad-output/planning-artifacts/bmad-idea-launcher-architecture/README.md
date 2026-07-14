---
title: BMAD Idea Launcher Architecture - Index & Navigation
created: 2026-07-13
updated: 2026-07-13
---

# BMAD Idea Launcher: Architecture Documentation Index

Welcome! This folder contains the complete architecture for the BMAD Idea Launcher MVP. Use this index to navigate the materials and find what you need.

---

## 📋 Quick Navigation

| Document                                             | Purpose                                               | Audience                          | Read Time |
| ---------------------------------------------------- | ----------------------------------------------------- | --------------------------------- | --------- |
| **[ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md)** | Core architecture; the consistency contract           | Developers, architects, reviewers | 15 min    |
| **[DECISIONS-SUMMARY.md](./DECISIONS-SUMMARY.md)**   | High-level overview of all decisions & next steps     | Everyone                          | 10 min    |
| **[SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md)**           | Implementation guide with API, components, deployment | Developers building the app       | 30 min    |
| **[.memlog.md](./.memlog.md)**                       | Decision log; detailed reasoning & assumptions        | Architects, decision reviewers    | 20 min    |

---

## 🎯 Start Here (by Role)

### I'm a Developer Building This App

1. **Start:** [DECISIONS-SUMMARY.md](./DECISIONS-SUMMARY.md) — Get the lay of the land (5 min)
2. **Read:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md) — Understand the invariants you must respect (15 min)
3. **Reference:** [SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md) — Pull API contracts, component specs, and code scaffolds as you code (30 min)
4. **Log:** As you implement, add decisions to `.memlog.md` if you deviate from the spine

**Time Investment:** ~1 hour (then refer back as needed during implementation)

---

### I'm a UX Designer Refining the Design

1. **Start:** [DECISIONS-SUMMARY.md](./DECISIONS-SUMMARY.md) — Understand scope & constraints (5 min)
2. **Read:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md#ad-4-single-screen-no-navigation) — Focus on AD-4 (single-screen), AD-5 (responsive), AD-11 (favorite state) (5 min)
3. **Reference:** [SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md#15-responsive-css-strategy) — See CSS breakpoints and component sketches (10 min)

**Constraints You Must Respect:**

- Single-screen layout (no navigation, modals, or tab panels)
- Responsive at 375px, 768px, 1920px (no horizontal scroll)
- Three idea cards (exactly three, always)
- Favorite toggle with clear visual state

---

### I'm a Tech Lead Reviewing the Architecture

1. **Read:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md) — All 11 ADs and the paradigm (20 min)
2. **Skim:** [.memlog.md](./.memlog.md) — Check assumptions and open questions (10 min)
3. **Review:** [SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md) — Verify technical feasibility (20 min)

**Key Questions to Ask:**

- Are all 11 ADs clear and binding?
- Do the assumptions hold for your team & environment?
- Are any open questions blockers for sprint planning?
- Is the thin backend model sufficient, or do you need more?

---

### I'm a Product Manager Tracking Scope

1. **Read:** [DECISIONS-SUMMARY.md](./DECISIONS-SUMMARY.md) — See what changed from PRD to architecture (5 min)
2. **Skim:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md#deferred-not-yet-decided) — What's deferred to post-MVP? (5 min)

**Key Takeaways:**

- All PRD features (FR-1 through FR-7) are covered by the architecture.
- D-1 through D-4 are deferred (visual style, scaling, analytics, i18n).
- Success metrics SM-1 and SM-2 are validated by the design.

---

### I'm an Architect Extending or Updating This

1. **Read:** [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md) — Understand the paradigm and all ADs (20 min)
2. **Study:** [.memlog.md](./.memlog.md) — See the decision context & tradeoffs (20 min)
3. **Reference:** [SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md) — Understand how the spine manifests in tech choices (15 min)

**To Amend the Architecture:**

- New decision? Add a `decision` entry to `.memlog.md` first.
- Update the spine? Edit [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md) and keep AD IDs stable.
- Rationale changes? Log them in `.memlog.md`, not the spine.

---

## 📑 Document Breakdown

### ARCHITECTURE-SPINE.md

**What it is:** The core architecture document defining the invariants, decisions, and consistency rules.

**Structure:**

- **Design Paradigm** — Single-page app with local state & browser persistence
- **Invariants (AD-1 to AD-11)** — The 11 binding decisions
- **Seed** — Technology stack, data flow diagram, component sketch
- **Deferred** — What's not yet decided (visual style, scaling, analytics, i18n)
- **Assumptions & Gaps** — [ASSUMPTION] tags for things taken for granted
- **Rationale & Tradeoffs** — Why each major decision was made
- **Next Steps** — Downstream workflows (bmad-ux, bmad-create-epics-and-stories, bmad-dev-story)

**How to use it:**

- When implementing: "Must I respect AD-n?" → Yes, it's an invariant.
- When reviewing code: "Does this comply with the spine?" → Check ADs 1–11.
- When extending: "Can I change this?" → No, unless logged in `.memlog.md` and reviewed.

**Key IDs to remember:**

- `AD-2` — Exactly three ideas (hard constraint)
- `AD-3` — localStorage favorites (no server DB)
- `AD-6` — Vanilla JS (no build step)
- `AD-7` — Thin backend (one POST endpoint)

---

### DECISIONS-SUMMARY.md

**What it is:** A digestible overview of the entire architecture, suitable for stakeholders, teams, and quick reference.

**Structure:**

- **The Architecture in One Sentence**
- **Key Decisions Table** — All 11 ADs at a glance
- **Technical Stack** — Frontend, backend, LLM, storage, deployment
- **What Changed** — Brief→PRD→Architecture evolution
- **Open Questions** — The 4 open issues and who owns them
- **Assumptions** — The 4 key assumptions & mitigating factors
- **Data Flow Diagram** — Visual representation of the user journey
- **Consistency Contracts** — The 7 "rules" any implementation must follow
- **Tradeoffs Made** — Why each major choice (no DB, thin backend, etc.)
- **Common Pitfalls** — 6 implementation mistakes to avoid
- **Quick Reference** — AD IDs and file organization

**How to use it:**

- **Starting a sprint:** Read this to understand scope and constraints.
- **Team alignment:** Share this to get everyone on the same page.
- **Stakeholder updates:** Reference the tradeoffs and open questions.
- **During implementation:** Use the pitfalls section to avoid common mistakes.

---

### SYSTEM-DESIGN.md

**What it is:** The implementation guide for developers building the app. Detailed API contracts, component specs, code scaffolds, deployment info, and testing strategies.

**Structure:**

- **Frontend Architecture** — Component tree, IdeaCard contract, state management, event flow, responsive CSS
- **Backend Architecture** — REST API contract, LLM provider abstraction, error handling, environment config
- **Data Model & Contracts** — Idea schema, favorite uniqueness logic, data flow
- **Deployment & Operations** — Recommended stack, local dev setup, environment files, deployment checklist
- **Testing Strategy** — Frontend unit tests, backend integration tests, E2E tests, success metrics
- **Known Limitations & Future Enhancements** — MVP bounds and v2 ideas
- **Code Scaffolds** — Express.js backend scaffold, HTML+Vanilla JS frontend scaffold

**How to use it:**

- **Starting dev:** Copy the frontend/backend scaffolds and fill in details.
- **API design:** Reference the `/api/ideas` contract; don't deviate.
- **Component implementation:** Use IdeaCard contract and event flow diagrams.
- **Testing:** Follow the unit/integration/E2E test examples.
- **Deployment:** Use the checklist and environment file template.

**Key API to remember:**

```
POST /api/ideas
Request:  { prompt: "..." }
Response: { ideas: [{ title: "...", description: "..." }, ...] }
```

---

### .memlog.md

**What it is:** The decision log tracking every architecture decision, assumption, and open question with context and rationale.

**Structure:**

- **Decisions Log (AD-1 to AD-11)** — Each decision with context, decision, binds, prevents, and rationale
- **Constraints Inherited** — Constraints from parent spines (if any)
- **Assumptions (4 total)** — Key assumptions with mitigating factors
- **Open Questions (4 total)** — Unresolved questions, impact, who decides
- **Decisions Triaged** — Blockers (resolved) and non-blockers (deferred)
- **Technical Direction Notes** — Why not full DB? Why not serverless? Why localStorage?
- **Status Tracking** — Decision count, next steps

**How to use it:**

- **When blocked:** Check open questions; find the owner and ask.
- **When curious about a decision:** Look up `AD-n` for full context (e.g., why exactly 3 ideas?).
- **When deviating:** Add a new `decision` entry if you change the spine; keep `AD` IDs stable.
- **Post-mortem:** Reference the assumptions to see what held and what was wrong.

---

## 🔄 The Architecture Lifecycle

### Creating (You Are Here)

- ✅ Paradigm defined (single-page app with local state)
- ✅ 11 invariants documented (AD-1 to AD-11)
- ✅ Technology stack recommended
- ✅ Open questions identified
- ✅ Assumptions logged

### Implementing

- Document any deviations in `.memlog.md` as new `decision` entries
- Reference AD-n IDs in PRs and commit messages
- Raise blockers early if an assumption is wrong

### Reviewing

- Check all code against the spine (are all ADs respected?)
- Verify no silent architecture changes (all changes logged?)
- Validate assumptions hold (did anything change?)

### Evolving (Post-MVP)

- Log changes in `.memlog.md`; don't renumber `AD` IDs
- Update rationale if assumptions were wrong
- Promote deferred items (D-1 to D-4) to decisions if needed

---

## 🎓 Learning from This Architecture

**This architecture demonstrates:**

- How to define invariants vs. seed vs. deferred
- Why a thin backend beats a complex one for an MVP
- How to make tradeoffs explicit (localStorage vs. DB, vanilla JS vs. framework)
- The value of logging decisions for team alignment
- How to balance simplicity (learning goal) with completeness (buildable system)

**Patterns worth copying:**

- Use `AD-n` IDs to make decisions stable and referenceable
- Log assumptions explicitly; don't hide them
- Deferred items are not failures; they're honest scope
- The memlog is the decision authority; the spine is the rendering

---

## 📞 Questions & Issues

**Question:** "Do I have to follow AD-n exactly?"  
**Answer:** Yes. If you find a flaw in an AD, log it in `.memlog.md` as a new decision, and raise it with the team. Don't silently deviate.

**Question:** "What if I disagree with a tradeoff?"  
**Answer:** See the memlog for the rationale. If the tradeoff no longer makes sense, log it as a discussion and escalate to the tech lead.

**Question:** "Can I add a feature not in the spine?"  
**Answer:** Features are in-scope or out-of-scope per the PRD. Architecture adds _how_ to build them. New features require a new story and may need spine amendments (logged in memlog).

**Question:** "What if the open questions block my sprint?"  
**Answer:** Escalate immediately to the owner (see `.memlog.md`). Don't assume an answer; get it decided and logged.

---

## 🚀 Next Steps (After Architecture Sign-Off)

**Recommended Sequence:**

1. **bmad-create-epics-and-stories** (1–2 hours)
   - Break the spine into epics (backend, frontend, integration, testing)
   - Create user stories for each epic
   - Estimate story points

2. **bmad-ux** (1–2 hours)
   - Finalize wireframes and visual design
   - Specify typography, colors, spacing
   - Create responsive mockups for 375px, 768px, 1920px

3. **bmad-dev-story** (parallel sprints)
   - Execute stories one-by-one or in parallel
   - Developers use the spine as the consistency contract
   - Reference ADs in PR descriptions

4. **Testing & Launch**
   - Verify SM-1 (user can complete flow in <2 min)
   - Verify SM-2 (no layout issues on mobile/desktop)
   - Deploy to production

---

## 📚 Related Documents

- **[Product Brief](../../docs/bmad-idea-launcher-brief.md)** — The vision and problem statement
- **[PRD](../../docs/bmad-idea-launcher-prd.md)** — Detailed requirements and acceptance criteria

---

## 📄 Document Metadata

| Attribute       | Value                                                      |
| --------------- | ---------------------------------------------------------- |
| **Created**     | 2026-07-13                                                 |
| **Status**      | Draft (ready for team review)                              |
| **Author**      | BMAD Architecture Workflow                                 |
| **Audience**    | Developers, architects, product managers, designers        |
| **Scope**       | BMAD Idea Launcher MVP (single-screen idea generation app) |
| **Next Review** | Post-UX-design; pre-epic-breakdown                         |

---

## 🎬 TL;DR (Ultra-Quick Version)

**What is this?**  
Architecture for a single-screen web app that turns a prompt into three starter ideas using an LLM.

**What's the big idea?**  
Frontend talks to thin backend → backend calls OpenAI → returns exactly 3 ideas → frontend stores favorites in browser.

**What do I need to know?**

- Read [ARCHITECTURE-SPINE.md](./ARCHITECTURE-SPINE.md) (the consistency contract)
- Follow [DECISIONS-SUMMARY.md](./DECISIONS-SUMMARY.md) (the overview)
- Reference [SYSTEM-DESIGN.md](./SYSTEM-DESIGN.md) (the how-to)
- Check [.memlog.md](./.memlog.md) for decisions & assumptions

**What's not decided yet?**  
Visual style, scaling strategy, analytics, i18n — all deferred to v2.

**Ready to build?**  
Run `bmad-create-epics-and-stories` next to break the spine into user stories.

---

**Architecture Spine Status:** ✅ **Ready for Implementation**

Questions? Check the memlog. Blockers? Escalate. Deviations? Log them. Happy building! 🚀
