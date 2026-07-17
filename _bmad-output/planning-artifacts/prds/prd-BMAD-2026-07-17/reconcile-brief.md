# Reconciliation: Brief vs PRD+Addendum — BMAD Idea Launcher

Source input: `_bmad-output/planning-artifacts/briefs/brief-BMAD-2026-07-17/brief.md`
Checked against: `prd.md` + `addendum.md` (same prd folder)

## Gaps Found

### 1. Brief's forward-looking "Vision" section (next-version ideas) is dropped entirely
The brief's `## Vision` section is explicit that it describes *future* versions, listing three concrete candidate features:
- Guided idea categories aligned to BMAD phases
- A tiny workflow helper showing next BMAD steps
- Export of the favorite idea into a brief or story

The PRD's `## 1. Vision` section reuses the "Vision" heading but repurposes it to restate the *current* (v1) product vision/pedagogical value — it does not carry forward any of the three future-version ideas. They are not mentioned anywhere else in the PRD (not in Open Questions, not in Non-Goals as "explicitly deferred," not in an Assumptions Index entry). A reader of the PRD alone would have no signal that the brief ever imagined a v2 direction, or what shape it might take. This is exactly the kind of qualitative/roadmap intent that a rigid FR structure silently drops, and it should be preserved somewhere (e.g., an "Out of Scope / Future Vision" subsection or an Open Question) rather than lost.

### 2. Brief's "BMAD Learning Angle" mapping is only partially carried forward — `bmad-brainstorming` and `bmad-help` are missing
The brief's `## BMAD Learning Angle` section explicitly maps the project to five BMAD skills, each with a distinct rationale:
- `bmad-brainstorming` — "the core product idea is an ideation tool" (i.e., the *product itself* is meant to embody/teach the brainstorming skill — a nuance about the product's identity, not just a workflow step)
- `bmad-ux` — one-screen experience and interaction design
- `bmad-architecture` — minimal data shape and application spine
- `bmad-create-story` — one implementation story for the MVP
- `bmad-help` — "a follow-on artifact that can recommend next steps after the launcher is built"

The PRD's Document Purpose (§0) only names `bmad-ux`, `bmad-architecture`, `bmad-create-story`. `bmad-brainstorming` is never mentioned — the idea that the app itself is a teaching vehicle for the brainstorming skill (not just "an ideation tool" generically) is lost. `bmad-help` is also never mentioned by name; FR-9 ("Next step" hint pointing at `bmad-ux`) is a much narrower, static-hint version of the brief's richer idea of a follow-on `bmad-help` *artifact* that can actively recommend next steps. The PRD substitutes a static UI hint for what the brief framed as a downstream BMAD-skill artifact — the distinction is meaningful and unaddressed.

### 3. "What Makes This Different" positioning/identity statement is not preserved explicitly
The brief's `## What Makes This Different` section frames the product's identity in contrast terms: "Uses the idea of an experimentation launcher rather than a full idea management app." This is a deliberate naming/positioning choice (the product is a *launcher*, not a *management tool*) that gives the project its tone and scope discipline.

The PRD captures the scope consequence of this (Non-Goals §5: "not a general-purpose idea/brainstorm management tool") but never states the positive framing — that the product is specifically an "experimentation launcher." The contrast is implicit only; the brief's explicit differentiation statement (which also includes "Focused on BMAD learning, not on building a large product" and "Delivers a complete, usable idea flow in a very small scope") is not restated or referenced anywhere in the PRD, e.g. in the Vision section or Document Purpose, even though it's the closest thing the brief has to a project tagline/identity.

## Not Gaps (verified present)
- Core success criterion (prompt → 3 cards < 30s) — carried into SM-1 and UJ-1.
- "brainstorm → define → build" learning-cycle framing — carried into PRD §1 Vision.
- Scope in/out lists (prompt input, generate button, 3 cards, favorite toggle, responsive layout, optional enhancements) — fully mapped to FR-1–FR-9.
- Tech stack simplicity ("basic," single front-end session) — carried into addendum's Tech Stack Direction and PRD's ASSUMPTION notes on local/templated generation.
- Secondary user framing (developer / BMAD practitioner) — captured in JTBD §2.1.
