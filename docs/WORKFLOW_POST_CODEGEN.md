# BMAD Workflow: Story Dev → Code Review → Confidence Scoring → Sprint/Retro (Detailed Flow)

This document picks up where [`docs/WORKFLOW.md`](WORKFLOW.md) leaves off. That document maps Brief → PRD.
This one maps everything **after a story is picked up for implementation through what happens once
source code has been generated** — dev execution, the mandatory plan-approval gate, code review,
objective confidence scoring, sprint-status sync, and epic retrospectives — as actually wired in this
repo (stock BMad skills + the Experion/org customization layer on top).

Sources: `.claude/skills/bmad-dev-story/`, `.claude/skills/bmad-code-review/`, `.claude/skills/confidence-scorer/`,
`.claude/skills/agent-project-logger/`, `.claude/skills/bmad-sprint-status/`, `.claude/skills/bmad-retrospective/`,
`_bmad/custom/bmad-dev-story.toml`, `_bmad/custom/bmad-code-review.toml`, `.claude/hooks/session_end_wiki_flag.py`,
`.claude/hooks/session_start_wiki_review.py`.

> **Persona note:** Ledger = `agent-project-logger`, Audit = `confidence-scorer`, Amelia = the Dev agent
> persona used inside `bmad-dev-story` / `bmad-retrospective`.

---

## 0. Where this picks up

By the time a story reaches `bmad-dev-story`, `sprint-status.yaml` already has it as `ready-for-dev`
(produced upstream by `bmad-create-epics-and-stories` / `bmad-sprint-planning` / `bmad-create-story` —
out of scope here). This document starts at story pickup and ends at epic retrospective.

```mermaid
flowchart LR
    S["sprint-status.yaml\nstory: ready-for-dev"] --> D["bmad-dev-story\n(plan → code → tests)"]
    D -- "status: review" --> R["bmad-code-review\n(adversarial, cross-model)"]
    R -- "status: done / in-progress" --> C["confidence-scorer\n(objective, per-file)"]
    C --> L["agent-project-logger\n(audit CSV)"]
    D -.->|"on_complete"| C
    R -.->|"activation_steps: confidence self-score"| L
    C --> SS["bmad-sprint-status\n(visibility + next-action)"]
    SS --> E{"All epic stories done?"}
    E -->|yes| RT["bmad-retrospective\n(lessons, action items)"]
    E -->|no| D
    RT --> W["wiki hooks\n(session_end/session_start)"]
```

---

## PHASE 3 — Dev Story (`bmad-dev-story`)

Files: `SKILL.md`, `customize.toml`, org override `_bmad/custom/bmad-dev-story.toml`.

### 3.1 Org customization layered on top of stock dev-story

The stock skill has empty `activation_steps_prepend/append` and empty `on_complete`. The org override
adds four `persistent_facts` and a non-empty `on_complete` — this is where this project's process
diverges most sharply from stock BMAD:

| Org addition | Effect |
|---|---|
| Fact 1 | Always load `.ai-context.md`, `.ai-context-security.md`, `.ai-context-dependencies.md`; conditionally load `.ai-context-api.md` / `.ai-context-errors.md` / `.ai-context-idea-generation.md` depending on what the story touches. |
| Fact 2 — **Plan-first hard gate** | Before any code generation, write `{story-dir}/{story_key}-plan.md` (frontmatter: `status: pending-approval`, confidence fields) covering scope, impacted files, design, data model, API changes, error handling, security, performance, test strategy, risks, context files consulted, rationale. Present it and **STOP**. |
| Fact 3 — **Plan confidence** | Self-assess `confidence`/`confidence_label`/`confidence_rationale` for the *plan* (not the code) before presenting it; log via `agent-project-logger` immediately after writing the plan file. |
| Fact 4 — **Scope lock** | Generated code must stay strictly inside the approved plan's stated files/modules/schemas; anything else requires stopping to ask first. |
| `on_complete` | Runs `confidence-scorer` once per file in the story's File List — see §3.4. |

### 3.2 Plan-approval gate (blocks Step 5 of the stock workflow)

```mermaid
flowchart TD
    PA1["Story picked up\n(Step 1-4 of stock workflow:\nload story, detect review-continuation,\nmark sprint-status in-progress)"] --> PA2["Write {story_key}-plan.md\nstatus: pending-approval\n+ confidence/confidence_label/confidence_rationale"]
    PA2 --> PA3["Ledger: 'Confidence scored: <label>\n(<score>/100) for implementation plan <story_key>'\nstage=implementation-plan, doc_status=pending-approval"]
    PA3 --> PA4["Present plan to user. STOP."]
    PA4 --> PA5{"User reply?"}
    PA5 -->|"exact phrase:\n'Plan reviewed and approved.\nProceed with code generation\nstrictly as per this plan.'"| PA6["Set plan frontmatter\nstatus: approved"]
    PA5 -->|"generic affirmative\n('yes','looks good','go ahead')"| PA5A["NOT sufficient — remain\nblocked, re-prompt"]
    PA5 -->|"feedback / changes requested"| PA5B["Revise plan, re-present\n(gate does not advance)"]
    PA6 --> PA7["Proceed to Step 5:\nred-green-refactor implementation"]
    PA7 --> PA8{"Plan changes\nmaterially mid-implementation?"}
    PA8 -->|yes| PA8A["Gate RESETS: status back to\npending-approval; must be\nre-approved before further codegen"]
    PA8 -->|no| PA9["Continue"]
```

### 3.3 Implementation loop (stock Steps 5–9, scope-locked to the approved plan)

```mermaid
flowchart TD
    I1["Step 5: Red-Green-Refactor\nper task/subtask, in story order"] --> I1R["RED: write failing tests first;\nconfirm they fail"]
    I1R --> I1G["GREEN: minimal code to pass;\nrun tests; handle edge cases"]
    I1G --> I1F["REFACTOR: clean up,\nkeep tests green;\nfollow Dev Notes architecture"]
    I1F --> I1D{"New dependency needed\nbeyond story spec?"}
    I1D -->|yes| I1H(["HALT: needs user approval"])
    I1D -->|no| I2
    I2["Step 6: Author comprehensive\nunit/integration/e2e tests\nfor the task"] --> I3["Step 7: Run full regression +\nnew tests + lint;\nvalidate against ACs"]
    I3 -->|"regression or new-test failure"| I3H(["STOP — fix before continuing"])
    I3 -->|pass| I4["Step 8: Validate task complete —\nALL tests exist+pass, matches\ntask exactly, no extra scope"]
    I4 --> I4R{"Task was an\n[AI-Review] follow-up?"}
    I4R -->|yes| I4RA["Mark item in Review Follow-ups\nAND matching Action Item in\nSenior Developer Review section;\nChange Log entry"]
    I4R -->|no| I5
    I4RA --> I5{"More incomplete\ntasks remain?"}
    I5 -->|yes| I1
    I5 -->|no| I6["Step 9: Full regression re-run,\nFile List completeness check,\nDefinition-of-Done validation"]
    I6 --> I6F{"DoD passes AND\nall tasks [x]?"}
    I6F -->|no| I6H(["HALT — resolve gaps first"])
    I6F -->|yes| I7["Story Status → 'review';\nsprint-status.yaml\ndevelopment_status[story_key]\n→ 'review'"]
```

**3 consecutive implementation failures** or **missing required configuration** are separate explicit
HALT conditions at any point in Step 5.

### 3.4 Completion → confidence scoring on generated code (`on_complete`)

This is the direct answer to "what happens after the source code is generated": once Status = `review`
and the File List is final, the org `on_complete` chain fires automatically, before the session ends.

```mermaid
flowchart TD
    OC1["Step 10: Summarize to user,\noffer explanations, suggest\nnext steps incl. code-review"] --> OC2["Resolve workflow.on_complete\n(org override, non-empty)"]
    OC2 --> OC3["For EACH file in the story's\nFile List (never batched,\nnever skipped):"]
    OC3 --> OC3A["Derive tests-passed/failed\nfrom Step 7's regression run,\nfiltered to tests touching this file"]
    OC3A --> OC3B["Derive lint-errors/warnings\nfrom the project linter\nrun against this file"]
    OC3B --> OC3C["Derive lines-changed from\n`git diff --stat {baseline_commit} -- <file>`"]
    OC3C --> OC3D["--revision-cycles = count of prior\n'Senior Developer Review (AI)'\ncycles in this story's Change Log\n(0 on first pass)"]
    OC3D --> OC3E["Invoke skill:confidence-scorer\n--doc-status review --doc-type {story_key}\n--stage stories"]
    OC3E --> OC3F["confidence_score.py computes\n0-100 score + Low/Med/High label\nfrom these 4 measured signals ONLY\n(never the model's impression)"]
    OC3F --> OC3G["log_action.py appends ONE row\nto the project audit CSV via\nagent-project-logger\n(action=code_scored)"]
    OC3G --> OC4{"More files in\nFile List?"}
    OC4 -->|yes| OC3A
    OC4 -->|no| OC5["Confirm exactly one audit row\nper File List entry"]
    OC5 --> OC6["Report file/confidence/label\ntable to user before ending session"]
```

**Key property:** this scores the *code that was actually generated* — a different, later measurement
than the plan-confidence score in §3.2, which only rated the *plan* before any code existed. Both are
logged, distinguishable by `stage` (`implementation-plan` vs `stories`) in the same audit log.

---

## PHASE 4 — Code Review (`bmad-code-review`)

Files: `SKILL.md` + `steps/step-01..04-*.md`, org override `_bmad/custom/bmad-code-review.toml`.
The dev-story completion message explicitly recommends running this **in a different LLM session**
than the one that wrote the code, to avoid self-review bias — the org override makes this a hard
persistent fact, not just a tip.

### 4.1 Step 1 — Gather context (read-only)

```mermaid
flowchart TD
    G1["Identify review target — cascade,\nstop at first match:"] --> G1T1["Tier 1: explicit argument this\nmessage (PR/commit/branch/spec/diff\n+ diff-mode keyword scan)"]
    G1 --> G1T2["Tier 2: recent conversation\n(same keyword scan)"]
    G1 --> G1T3["Tier 3: sprint-status.yaml —\nstories with status='review'\n(auto-suggest if exactly one)"]
    G1 --> G1T4["Tier 4: current git branch/HEAD\nif not on default branch"]
    G1 --> G1T5["Tier 5: ASK the user directly"]
    G1T1 --> G2["Construct {diff_output} per source\n(staged / uncommitted / branch diff /\ncommit range / provided diff / file list)"]
    G1T2 --> G2
    G1T3 --> G2
    G1T4 --> G2
    G1T5 --> G2
    G2 -->|empty diff| G2H(["HALT: nothing to review"])
    G2 --> G3{"Spec/story file\nfor context?"}
    G3 -->|yes, or found via Tier1/2| G3A["review_mode = 'full';\nload story's frontmatter\ncontext[] docs too"]
    G3 -->|no| G3B["review_mode = 'no-spec'\n(Acceptance Auditor lens\nlater skipped)"]
    G3A --> G4{"Diff > ~3000 lines?"}
    G3B --> G4
    G4 -->|yes| G4A["Warn; offer to chunk\nby file group"]
    G4 -->|no| G5["CHECKPOINT: present diff stats,\nreview_mode, loaded docs.\nHALT for user confirmation"]
    G4A --> G5
```

### 4.2 Steps 2–3 — Parallel adversarial review + triage (org confidence layer)

Step 2 (`step-02-review.md`) fans out to parallel review lenses — **Blind Hunter**, **Edge Case
Hunter**, and (only in `review_mode='full'`) **Acceptance Auditor** against the spec's ACs — each an
independent adversarial pass over the same diff. Step 3 (`step-03-triage.md`) merges their raw findings
into one triaged list.

The org override adds three persistent facts layered over the stock two-step review:

1. Always load the same `.ai-context*.md` files as dev-story (mirrors the code-generation context).
2. **Fresh-session requirement** — if this session also generated the code under review, say so and
   recommend restarting in a fresh session (anti self-review-bias).
3. **Fixed severity vocabulary** — CRITICAL (security/data-loss, escalate to Tech Lead) / HIGH (plan
   deviation, unhandled exception, perf risk) / MEDIUM (standards, missing log, naming) / LOW (style).
4. **Diff-to-plan reconciliation**, mandatory every run: `git diff` file list vs. the plan's/story's
   stated Impacted Modules & Files — flag files present in the diff but not in the plan, and files in
   the plan but absent from the diff (signals incomplete implementation).
5. **Review-completeness confidence score** (distinct from code-quality findings) — self-assessed at
   Step 4, lowered for any failed/skipped reviewer lens, `no-spec` mode, a diff the user chose to chunk,
   or any best-effort/uncertain finding. Logged via `agent-project-logger` the same way as dev-story's
   plan/code scores, with `stage='code-review'`.

```mermaid
flowchart TD
    T1["Step 2: dispatch parallel\nadversarial lenses"] --> T1A["Blind Hunter\n(assume nothing, hunt bugs\nwith no prior context)"]
    T1 --> T1B["Edge Case Hunter\n(boundary/branch coverage)"]
    T1 --> T1C{"review_mode\n== full?"}
    T1C -->|yes| T1C1["Acceptance Auditor\n(diff vs story ACs)"]
    T1C -->|no| T1C2["Skipped — lowers\nreview-completeness score"]
    T1A --> T2["Step 3: Triage — merge,\ndedupe, classify each finding"]
    T1B --> T2
    T1C1 --> T2
    T1C2 --> T2
    T2 --> T2A["decision-needed\n(ambiguous fix, user must choose)"]
    T2 --> T2B["patch\n(clear, mechanical fix)"]
    T2 --> T2C["defer\n(pre-existing, out of scope)"]
    T2 --> T2D["dismissed as noise"]
    T2A --> T3["Diff-to-plan reconciliation\nresult attached to output"]
    T2B --> T3
    T2C --> T3
    T2D --> T3
    T3 --> T4["Self-assess review-completeness\nconfidence/label/rationale"]
    T4 --> T5["Ledger: 'Confidence scored: <label>\n(<score>/100) for code review of\n<story_key or diff source>'\nstage=code-review"]
```

### 4.3 Step 4 — Present, resolve, and sync status

```mermaid
flowchart TD
    P1{"Zero findings\nafter triage?"} -->|yes| P1A["State clean review;\nskip to Sprint Status Update"]
    P1 -->|no| P2["If {spec_file} set: append\n'Review Findings' subsection to\nstory file (decision-needed unchecked,\npatch unchecked, defer checked+logged\nto deferred-work.md)"]
    P2 --> P3["Announce counts:\n<D> decision-needed, <P> patch,\n<W> defer, <R> dismissed"]
    P3 --> P4{"decision-needed\nfindings exist?"}
    P4 -->|yes| P4A["HALT per finding/batch —\nuser decides fix/defer/dismiss;\ndefer requires 1-line reason"]
    P4 -->|no| P5
    P4A --> P5{"patch findings\nexist (incl. resolved)?"}
    P5 -->|yes| P5A["HALT — user picks:\n1) apply all now\n2) leave as action items (spec_file only)\n3) walk through each"]
    P5 -->|no| P6
    P5A --> P6["Determine {new_status}:\nall decision/patch resolved AND\nno unresolved High/Medium →\n'done', else 'in-progress'"]
    P6 --> P7["Update story Status section;\nsync sprint-status.yaml\ndevelopment_status[story_key]\n= {new_status}"]
    P7 --> P8["Completion summary:\nstatus, fixed/action/deferred/\ndismissed counts"]
    P8 --> P9{"Next step?"}
    P9 -->|"1"| P9A["dev-story — pick up next\nready-for-dev story"]
    P9 -->|"2"| P9B["Re-run code-review after fixes"]
    P9 -->|"3"| P9C(["Done — resolve\nworkflow.on_complete if set"])
```

**Outcome that matters most:** a story only reaches `done` in `sprint-status.yaml` via this step — never
directly from `bmad-dev-story`, which only ever sets `review`. Code review is the sole gate between
"code exists and its own author calls it finished" and "status: done."

---

## PHASE 5 — Sprint Status (`bmad-sprint-status`)

Passive dashboard, not a gate — reads `sprint-status.yaml`, never blocks progress. Runs any time
(commonly after dev-story or code-review) to answer "what's next."

```mermaid
flowchart TD
    SS1["Load sprint-status.yaml"] --> SS2["Classify keys: epics (epic-*),\nretrospectives (*-retrospective),\nstories (everything else)"]
    SS2 --> SS3["Validate all status values;\noffer inline correction menu\nif any are unrecognized"]
    SS3 --> SS4["Detect risks: stale file (>7 days),\norphaned story, in-progress epic\nwith no stories, review-stage\nstories awaiting code-review"]
    SS4 --> SS5["Priority-pick next action:\n1) in-progress → dev-story\n2) review → code-review\n3) ready-for-dev → dev-story\n4) backlog → create-story\n5) retrospective optional → retrospective\n6) else → congratulate, done"]
    SS5 --> SS6["Display counts, risks,\nnext recommendation"]
    SS6 --> SS7{"User picks\naction 1-4?"}
    SS7 -->|"1 run recommended"| SS7A["Hand off to the\nrecommended workflow"]
    SS7 -->|"2/3 inspect"| SS7B["Show stories-by-status /\nraw YAML"]
    SS7 -->|"4 exit"| SS7C(["Resolve on_complete if set"])
```

---

## PHASE 6 — Retrospective (`bmad-retrospective`)

Triggered once every story in an epic is `done` (per sprint-status's own recommendation, priority 5).
Runs as a "party mode" multi-persona facilitated session (Amelia facilitates; Alice/Charlie/Dana/Elena
are fixed supporting personas), always in two parts: **Epic Review** then **Next Epic Preparation**.

```mermaid
flowchart TD
    RT1["Step 1: Epic discovery —\nsprint-status highest epic with\nall stories done, confirm with user"] --> RT1B{"Epic actually\ncomplete?"}
    RT1B -->|no| RT1C["Offer: finish stories first (recommended) /\ncontinue partial / re-run sprint-planning"]
    RT1B -->|yes| RT2["Step 2-3: Load architecture/PRD/epic;\ndeep-read EVERY story file for Dev Notes,\nReview feedback patterns, Lessons Learned,\nTech Debt, Testing insights"]
    RT2 --> RT3["Step 4: Load previous epic's\nretro, cross-check its action items\nagainst what actually happened\n(✅ done / ⏳ in-progress / ❌ not addressed)"]
    RT3 --> RT4["Step 5: Preview next epic —\ndependencies, prep gaps,\ntechnical prerequisites"]
    RT4 --> RT5["Steps 6-8: Facilitated multi-persona\ndiscussion — successes, challenges,\nprevious-retro follow-through,\nnext-epic readiness debate"]
    RT5 --> RT6["Step 9: Synthesize SMART action\nitems + prep tasks + critical path;\ndetect SIGNIFICANT DISCOVERIES that\nwould require updating the next epic"]
    RT6 --> RT7{"Significant\ndiscovery flagged?"}
    RT7 -->|yes| RT7A["Recommend epic-planning review\nsession BEFORE starting next epic;\nadd to critical path"]
    RT7 -->|no| RT8
    RT7A --> RT8["Step 10: Readiness gut-check —\ntesting, deployment, stakeholder\nacceptance, technical health,\nunresolved blockers"]
    RT8 --> RT9["Step 11: Closure — key takeaways,\ncommitments summary"]
    RT9 --> RT10["Step 12: Save\nepic-{N}-retro-{date}.md;\nupdate sprint-status.yaml:\nepic-{N}-retrospective → done;\nappend action_items[] entries;\nupdate prev-epic action item statuses"]
    RT10 --> RT11(["Step 13: Final summary + handoff —\nresolve workflow.on_complete if set"])
```

---

## PHASE 7 — Cross-cutting: audit log + LLM Wiki capture

These two mechanisms run independently of any single phase above, but are triggered by everything in
Phases 3–6.

### 7.1 `agent-project-logger` (Ledger) — the shared audit trail

Every confidence score in Phases 3–4 (plan confidence, code confidence per file, review-completeness
confidence) lands here as one CSV row via `log_action.py` — append-only, one action in / one row out,
never batched or reordered. This is the single source of truth Audit (`confidence-scorer`) reads and
writes against; there is no parallel score store.

### 7.2 LLM Wiki capture (session hooks, independent of BMAD skills entirely)

```mermaid
flowchart TD
    H1["Any Claude Code session ends"] --> H2["SessionEnd hook:\nsession_end_wiki_flag.py\n(plain command, no LLM)"] --> H3["Copy transcript to\n.claude/hooks/pending-review/{session_id}.jsonl;\nappend {session_id, path, ended_at}\nto .wiki-review-pending.jsonl queue"]
    H3 --> H4["Next Claude Code session\nstarts (any time later)"]
    H4 --> H5["SessionStart hook:\nsession_start_wiki_review.py"]
    H5 --> H6{"Queue\nnon-empty?"}
    H6 -->|no| H6A["No-op"]
    H6 -->|yes| H7["Drain queue; inject additionalContext:\nreview each queued transcript against\nwiki/SCHEMA.md, per llm-wiki skill's\ningest workflow"]
    H7 --> H8["Live session skims each transcript for\ndecisions/architecture rationale/lessons/\nbugs-postmortems/workflow notes"]
    H8 --> H9{"Anything\ningest-worthy?"}
    H9 -->|yes| H9A["Ingest into wiki/ (correct subfolder,\nsurgical edits, update index,\nappend to wiki/log.md)"]
    H9 -->|no| H9B["Skip that transcript, note nothing found"]
    H9A --> H10["Delete pending-review/\n(durable copies no longer needed)"]
    H9B --> H10
```

This means implementation sessions (dev-story, code-review, retrospective included) are themselves a
source the wiki draws from on a lag of one session boundary — decisions or lessons surfaced during a
dev-story or retro session, even if never manually written to the wiki, get a second chance to be
captured automatically the next time any Claude Code session starts in this repo.

---

## 8. Full status-field lifecycle across Phases 3–6

| Stage | `sprint-status.yaml` story status | Set by | Trigger |
|---|---|---|---|
| Story queued | `ready-for-dev` | upstream (create-story / sprint-planning) | out of scope here |
| Story picked up | `in-progress` | `bmad-dev-story` Step 4 | first task started or review-continuation resumed |
| All tasks complete, DoD passed | `review` | `bmad-dev-story` Step 9 | never set to `done` directly |
| Code review resolves cleanly | `done` | `bmad-code-review` Step 4 | all decision/patch resolved, no unresolved High/Medium |
| Code review leaves open items | `in-progress` | `bmad-code-review` Step 4 | patch findings left as action items, or unresolved issues remain |
| Epic fully done | `epic-{N}-retrospective`: `optional` → `done` | `bmad-retrospective` Step 12 | run once all stories in the epic are `done` |

Confidence scores (plan / code / review-completeness) are a **parallel, additive** audit trail via
`agent-project-logger` — they never gate the status transitions above; the plan-approval exact-phrase
gate (§3.2) is the only hard human-in-the-loop block in this half of the pipeline.

---

## 9. Answer in one paragraph: "what happens after the source code is generated?"

Once `bmad-dev-story` finishes red-green-refactor for the last task and Definition-of-Done passes, the
story's Status flips to `review` (never straight to `done`) and, still inside the same dev-story run,
the org `on_complete` chain invokes `confidence-scorer` once per changed file — computing an objective
0–100 score from measured test/lint/diff/revision signals and logging one audit row per file via
`agent-project-logger`. The user is then pointed at `bmad-code-review`, which should run in a **separate
session** to avoid self-review bias: it fans out adversarial review lenses (Blind Hunter, Edge Case
Hunter, and — when a spec is available — Acceptance Auditor), reconciles the diff against the approved
plan's stated file scope, triages findings into decision-needed/patch/defer/dismissed, self-scores its
own *review completeness* (a second, distinct confidence number, also logged), and only then decides
whether the story becomes `done` or bounces back to `in-progress`. `bmad-sprint-status` surfaces this
state and recommends the next action; once every story in an epic reaches `done`, `bmad-retrospective`
runs a facilitated multi-persona session that mines every story's Dev Notes/Review/Lessons sections,
checks follow-through on the previous epic's action items, flags any discovery significant enough to
require updating the next epic's plan, and records new action items back into `sprint-status.yaml`.
Independently of all of this, whenever any Claude Code session in this repo ends, its transcript is
queued for review and surfaced to the very next session's start, which is asked to mine it for anything
wiki-worthy (decisions, lessons, bugs) and file it into `wiki/` — so implementation knowledge from dev,
review, and retro sessions has a standing second chance to become durable project memory even if never
manually captured.
