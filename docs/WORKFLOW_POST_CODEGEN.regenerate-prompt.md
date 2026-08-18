# Regeneration prompt for `docs/WORKFLOW_POST_CODEGEN.md`

Paste the block below into a fresh Claude Code session in this repo to regenerate or refresh this
document if the underlying skills/customizations drift. Keep this prompt file in sync with the
sources list in the target doc's header whenever new skills are added to that stage of the pipeline.

---

You are a technical architect documenting this repo's actual, wired BMAD workflow — not the stock
BMad framework in the abstract. Produce (or refresh) `docs/WORKFLOW_POST_CODEGEN.md`, covering the
pipeline from **story pickup through epic retrospective** (i.e. everything that happens once a story
is `ready-for-dev`, through code generation, code review, confidence scoring, sprint tracking, and
retrospectives). This complements `docs/WORKFLOW.md`, which already covers Brief → PRD — do not
duplicate that document; cross-link it instead.

Ground every claim in the actual files in this repo, not general BMAD knowledge. Read, in this order:

1. `.claude/skills/bmad-dev-story/SKILL.md` and `.claude/skills/bmad-dev-story/customize.toml` —
   the stock dev-story workflow steps (activation, story discovery, implementation loop,
   completion/DoD, `on_complete` hook).
2. `_bmad/custom/bmad-dev-story.toml` — the org override: persistent_facts (context loading,
   plan-first approval gate with its exact required approval phrase, plan confidence scoring, scope
   lock) and the `on_complete` chain (per-file `confidence-scorer` invocation with exact signal
   derivations).
3. `.claude/skills/bmad-code-review/SKILL.md` and every file under
   `.claude/skills/bmad-code-review/steps/` (currently step-01 gather-context, step-02 review,
   step-03 triage, step-04 present) — the adversarial review lenses, diff-source cascade, triage
   categories, and story-status/sprint-status sync logic.
4. `_bmad/custom/bmad-code-review.toml` — org additions: context files, fresh-session
   self-review-bias rule, fixed severity vocabulary, diff-to-plan reconciliation requirement, and
   the review-completeness confidence score (distinct from code-quality findings).
5. `.claude/skills/confidence-scorer/SKILL.md` and
   `.claude/skills/confidence-scorer/references/score-file.md` — how the deterministic 0–100 score
   is computed (test/lint/diff/revision-cycle signals only, never model impression) and logged.
6. `.claude/skills/agent-project-logger/SKILL.md` — the shared append-only audit CSV that every
   confidence score (plan, code, review-completeness) writes one row into.
7. `.claude/skills/bmad-sprint-status/SKILL.md` — how sprint-status.yaml is read, validated, and
   used to recommend the next workflow action (priority order matters — reproduce it exactly).
8. `.claude/skills/bmad-retrospective/SKILL.md` — the full multi-persona retrospective flow: epic
   discovery, deep story-file mining for lessons, previous-retro follow-through cross-check,
   next-epic readiness, significant-discovery detection, and the sprint-status.yaml writes at the
   end (retrospective status → done, `action_items[]` entries).
9. `.claude/hooks/session_end_wiki_flag.py` and `.claude/hooks/session_start_wiki_review.py` — the
   cross-cutting mechanism that queues every session's transcript for wiki-worthiness review at the
   start of the *next* session, independent of any BMAD skill.
10. Re-check `_bmad/custom/*.toml` for any NEW override files beyond the ones above (an override
    file may have been added since this prompt was last run) — glob `_bmad/custom/*.toml` and diff
    against the list here before writing.

Output requirements:

- One Mermaid `flowchart` per phase/step-group, matching the level of granularity in
  `docs/WORKFLOW.md` (every HALT, every branch, every status-field mutation shown explicitly —
  do not collapse decision points into prose).
- A top-of-document flowchart giving the phase-to-phase overview (story → dev → review → score →
  sprint-status → retrospective → wiki).
- Explicitly show, for each phase, which parts are **stock BMad** vs **org customization layered on
  top** (via `_bmad/custom/*.toml`) — call out every place the org layer changes stock behavior,
  the same way `docs/WORKFLOW.md` documents the Brief/PRD customization layer.
- A status-field lifecycle table (sprint-status.yaml story/epic/retrospective statuses, what sets
  each, what triggers it) analogous to the one in `docs/WORKFLOW.md` §7.
- Close with a single-paragraph plain-English answer to "what happens after the source code is
  generated?" that a reader could act on without reading the diagrams.
- Cite every source file path used, in a header block, exactly as `docs/WORKFLOW.md` does.
- Keep it under the wiki's atomic-page conventions if this content is ever sharded into `wiki/`
  (soft cap ~400 lines per resulting page) — if the combined document exceeds that meaningfully,
  note it as a candidate for `bmad-shard-doc` rather than force-shrinking it here.

Do not speculate about steps that aren't in the read files. If a skill's `on_complete` or
`activation_steps_*` is empty in both `customize.toml` and any org override, say so explicitly (an
empty hook is itself a fact worth documenting, e.g. it shows dev-story's own stock `on_complete` is
empty and the entire confidence-scoring trigger is an org addition).
