# AI-Based SDLC Demo Runbook — Greenfield Feature, PRD → Code

A complete, step-by-step process for running this BMAD-based project locally to develop a new
feature from scratch, and for demonstrating it to a customer as an AI-governed SDLC.

The story this runbook tells a customer: **an idea goes in at one end, governed and audited
documents are produced at each stage, gates block anyone from skipping a stage, and code comes
out the other end scored against measured evidence — not vibes.**

---

## 0. What this project actually is

| Layer                    | Location                                                      | What it does                                                                                                                                      |
| ------------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| BMAD method skills       | `.claude/skills/bmad-*`                                       | The SDLC workflows: brief → PRD → UX → architecture → epics/stories → sprint → dev → review                                                       |
| BMAD agents (personas)   | `_bmad/config.toml` `[agents.*]`, `.github/agents/*.agent.md` | Mary (Analyst), John (PM), Sally (UX), Winston (Architect), Amelia (Dev), Paige (Tech Writer)                                                     |
| Custom governance skills | `skills/` and `.claude/skills/`                               | `agent-approval-grant`, `agent-approval-gate-check`, `agent-project-logger`, `experion-brief-review`, `confidence-scorer`, `prompt-gateway-guard` |
| Customization layer      | `_bmad/custom/*.toml`                                         | Injects the governance skills into stock BMAD workflows — this is the differentiator, not the stock skills                                        |
| Approval ledger          | `_bmad/custom/approval-state.json`                            | SHA-256 content hash per approved document                                                                                                        |
| Audit log                | `_bmad-output/<project_name>-project-log.csv`                 | Append-only row per action, with confidence scores                                                                                                |
| Prompt firewall          | `PromptGateway/` + `.claude/hooks/prompt_gateway_check.py`    | Every user prompt screened for PII/secrets/injection/toxicity before Claude sees it                                                               |
| Commit guard             | `.husky/pre-commit` → `scripts/revert-brief-status.js`        | Reverts `approval_status: approved` → `draft` if an approved doc's content changed                                                                |
| Demo app (current)       | `server.js`, `lib/`, `public/`, `test/`                       | The product a previous run of this pipeline produced — **delete for a greenfield demo**                                                           |

### The four control points worth demoing

1. **Prompt gateway** — a prompt containing a secret is BLOCKED before it reaches the model.
2. **Approval gate** — you cannot generate a PRD until the brief is approved _and_ unchanged since approval (hash check).
3. **Plan-first hard gate** — no code is generated until you type an exact approval sentence for the implementation plan.
4. **Confidence scoring** — every document gets an LLM self-assessed score; every generated _file_ gets a deterministic score computed from tests, lint, diff size, and revision count.

---

## 1. Prerequisites

Verified working versions on this machine are shown in brackets.

| Tool                    | Needed for                                       | Check               |
| ----------------------- | ------------------------------------------------ | ------------------- |
| Node.js ≥ 22 [v24.13.0] | app runtime, `node --test`, husky                | `node -v`           |
| Python ≥ 3.10 [3.13.12] | governance skill scripts                         | `python3 -V`        |
| `uv` [0.8.17]           | `resolve_customization.py` — customization merge | `uv --version`      |
| Git [2.50.1]            | approval hashing, diff-based scoring             | `git --version`     |
| Claude Code             | runs the skills                                  | in this repo's root |
| Python 3.11+ venv       | PromptGateway service                            | see §3              |
| Ollama _(optional)_     | PromptGateway's LLM risk classifier              | `ollama list`       |

Install repo dependencies once:

```bash
npm install
```

That also wires the husky pre-commit hook via the `prepare` script.

Sanity-check the customization resolver — everything downstream depends on it:

```bash
uv run _bmad/scripts/resolve_customization.py --skill .claude/skills/bmad-prd --key workflow
```

You should see JSON containing `prd_template`, `activation_steps_prepend`, and `on_complete`.
If this fails, every governance hook silently degrades.

---

## 2. Reset to greenfield

> ⚠️ **Destructive.** Do this on a throwaway branch, never on `develop` directly.
> The current repo contains a _completed_ run (the "BMAD Idea Launcher" app plus its artifacts).
> A greenfield demo needs those gone, but the customization layer kept.

```bash
git checkout -b demo/greenfield-run
```

### 2.1 Delete the previous run's outputs and product code

```bash
rm -rf _bmad-output/planning-artifacts _bmad-output/implementation-artifacts
rm -f  _bmad-output/*-project-log.csv
rm -rf lib public test server.js
rm -f  .ai-context.md .ai-context-*.md
```

**Keep:** `_bmad/`, `skills/`, `.claude/`, `PromptGateway/`, `scripts/`, `.husky/`, `package.json`.

### 2.2 Clear the approval ledger

`approval-state.json` stores **absolute, resolved** document paths. The committed file still holds
Windows paths (`D:\Projects\bmad-demo\...`), which will never match on macOS/Linux — a stale entry
here is the most common cause of a confusing "unapproved" block.

```bash
echo '{}' > _bmad/custom/approval-state.json
```

### 2.3 Name the new project

Two independent names, both matter:

**a) Audit-log filename** — `_bmad/custom/project.json`:

```json
{
  "project_name": "acme-checkout-revamp"
}
```

Produces `_bmad-output/acme-checkout-revamp-project-log.csv`.

**b) Document folder slug** — used in artifact folder names like `brief-BMAD-2026-08-13`.
It comes from `[core] project_name` in `_bmad/config.toml`, which is **installer-managed and
regenerated on every install**. Do not edit it. Pin it instead in the team override file
`_bmad/custom/config.toml`:

```toml
[core]
project_name = "ACME"
```

### 2.4 Neutralize the previous project's context rules

`_bmad/custom/bmad-create-story.toml`, `bmad-dev-story.toml`, and `bmad-code-review.toml` all carry
`persistent_facts` that reference the _old_ app's context files (`.ai-context-idea-generation.md`,
`lib/ideaService.js`). Until you regenerate context (§8), replace those three `persistent_facts`
entries with the generic form, e.g. in `_bmad/custom/bmad-dev-story.toml`:

```toml
persistent_facts = [
  "Always load .ai-context.md as foundational context before working on any story.",
  # ... keep the plan-first gate and confidence-scoring facts exactly as they are ...
]
```

**Do not touch** the plan-first hard-gate fact or the confidence-scoring fact — those are the demo.

### 2.5 Commit the clean baseline

```bash
git add -A && git commit -m "chore: reset to greenfield baseline for demo"
```

Note this commit SHA — the confidence scorer uses a baseline commit for `git diff --stat`.

---

## 3. Start PromptGateway (the prompt firewall)

The `UserPromptSubmit` hook in `.claude/settings.json` screens **every** prompt you type.
It **fails open** — if the gateway is down you get a `[Marshal] check skipped` notice and work
continues. For the demo you want it up.

```bash
cd PromptGateway
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Optional, for the nuanced LLM risk classifier (deterministic regex/PII/injection checks work without it):

```bash
ollama pull llama3.2
```

Verify: open <http://localhost:8000/docs>, or

```bash
curl -s -X POST http://localhost:8000/api/v1/validate -H 'Content-Type: application/json' -d '{"prompt":"hello world"}'
```

Point the hook elsewhere (staging, shared instance) without editing any skill by creating
`_bmad/custom/prompt-gateway-guard.toml`:

```toml
[agent]
base_url = "http://gateway.internal:8000"
api_key = "..."
```

### Demo beat — do this early, it lands well

In Claude Code, type a prompt containing a fake secret, e.g.
`Use my API key sk-ant-api03-AAAA1111BBBB2222CCCC3333DDDD4444 to call the model`.

- **BLOCK** → Claude never sees the prompt; the user sees the risk score, reason, and categories.
- **FLAG** → prompt proceeds, but the warning is injected into Claude's context as `additionalContext`.
- **ALLOW** → silent.

Audit trail lands in `PromptGateway/logs/audit.db` (SQLite) and `PromptGateway/logs/`.

---

## 4. Phase 1 — Analysis → Product Brief

Everything below is typed into Claude Code in this repo's root. Each skill is invoked by its
trigger phrase (shown in quotes); `/skill-name` also works where the skill is listed.

### 4.1 Optional warm-up

- `"help me brainstorm"` → `bmad-brainstorming` — facilitated ideation, writes to `planning-artifacts`.
- `"I need market research"` / `"domain research"` / `"technical research report"` → the three research skills.

Skip these in a short demo; mention they exist.

### 4.2 Create the brief

> **"create a product brief"**

Uses `_bmad/custom/templates/brief-template.md`.

What the customization layer makes happen automatically, in order:

1. **On activation** — `agent-project-logger` writes `Brief generation started`.
2. Coached discovery conversation with **Mary (Analyst)**; `.memlog.md` records the run.
3. **On complete** —
   a. logs `Brief generated`;
   b. logs `Confidence scored: <label> (<n>/100) for brief` with rationale (LLM self-assessment, written into the brief's frontmatter);
   c. runs `experion-brief-review` — adversarial review across five fixed dimensions → `review-report.md`;
   d. logs `Brief review report generated`;
   e. sets `approval_status: review`;
   f. invokes `agent-approval-grant`.

**Artifacts:** `_bmad-output/planning-artifacts/briefs/brief-<PROJECT>-<date>/` containing
`brief.md`, `review-report.md`, `.memlog.md`.

### 4.3 Approve the brief

`agent-approval-grant` **double-confirms** before it writes anything. On approval it:

- sets `approval_status: approved` in the frontmatter,
- records `{doc_path, approved_hash}` (SHA-256 of file bytes) into `_bmad/custom/approval-state.json`.

If the review artifact is missing or stale for this version, it regenerates it first
(`review_skill_defaults` in `_bmad/custom/agent-approval-grant.toml`).

```bash
git add -A && git commit -m "Approve brief v1"
```

### Demo beat — the gate is real

Edit one sentence in the approved `brief.md`, then try to generate the PRD. The gate check
recomputes the hash, sees the mismatch, **reverts the frontmatter to `draft`**, and blocks with
`reason: "stale"`. Content hashing (not mtime) is used deliberately so a fresh `git clone`
doesn't false-positive.

Also worth showing: `git commit` an edited approved doc and watch `.husky/pre-commit`
(`scripts/revert-brief-status.js`) rewrite `approved` → `draft`, re-stage the file, and log
`Brief updated outside approval flow - status reverted to draft`.

---

## 5. Phase 2 — PRD

> **"create a PRD"**

Custom behavior from `_bmad/custom/bmad-prd.toml`:

- **Prepend:** `agent-approval-gate-check` on the **brief** — blocks PRD generation unless the brief is `approved` and unchanged.
- **Prepend:** logs `PRD generation started`.
- Template: `_bmad/custom/templates/prd-template.md`; checklist: `prd-validation-checklist.md`.
- **Persistent fact:** any substantive PRD edit _later in chat_ auto-reverts `approved` → `draft` and logs the change immediately.
- **On complete:** logs `PRD generated` → logs confidence score → sets `approval_status: review` → invokes approval grant.

Drive it with **John (PM)** — Jobs-to-be-Done framing, interrogative style.

Optional explicit pass: **"validate the PRD"** → validation report `review-rubric.md`
(the filename the approval flow looks for, per `review_artifact_filename_defaults`).

**Artifacts:** `_bmad-output/planning-artifacts/prds/prd-<PROJECT>-<date>/` — `prd.md`,
`review-rubric.md`, `reconcile-brief.md`, `.memlog.md`.

Approve, then commit:

```bash
git add -A && git commit -m "Approve prd v1"
```

---

## 6. Phase 3a — UX (optional, but do it if the feature has UI)

> **"let's create UX design"**

Runs with **Sally (UX)**. `_bmad/custom/bmad-ux.toml` adds one thing: an `on_complete` confidence-score
log for `EXPERIENCE.md`. No approval gate on UX — it is advisory input to architecture.

---

## 7. Phase 3b — Architecture spine

> **"create the architecture"**

From `_bmad/custom/bmad-architecture.toml`:

- **Prepend:** gate-check on the **PRD** — blocked unless PRD approved and unchanged.
- **Prepend:** logs `Architecture generation started`.
- Template: `architecture-spine-template.md`.
- **Persistent fact:** the Reviewer Gate's consolidated report is always written to the fixed path
  `review-report.md` with frontmatter `architecture_version` = spine version + 1. Per-lens scratch
  files under `reviews/` (adversarial, tech-currency, rubric) are _not_ canonical.
- **On complete:** logs → confidence score → `approval_status: review` → approval grant.

Drive it with **Winston (Architect)** — boring technology, explicit trade-offs, decisions numbered
`AD-1`, `AD-2`, … These AD-ids get cited by stories and by the do-not-do rules later, which is what
makes the chain auditable.

**Artifacts:** `architecture/architecture-<PROJECT>-<date>/` — `ARCHITECTURE-SPINE.md`,
`review-report.md`, `reviews/*.md`, `reconcile-prd.md`, `.memlog.md`.

Approve and commit.

---

## 8. Generate project context (do this right after architecture)

> **"generate project context"**

Produces the lean, LLM-optimized context the dev/review skills load on every story. In this repo
the previous run's version was a root-level orchestrator plus conditional includes — reproduce that
shape for the new project:

```
.ai-context.md                  # orchestrator: overview, folder rules, testing convention, global DO-NOT rules
.ai-context-security.md         # always loaded
.ai-context-dependencies.md     # always loaded
.ai-context-<feature-area>.md   # conditionally loaded by topic
```

The orchestrator's most demo-relevant section is **Global Do-Not-Do Rules**, each tied back to an
architecture decision, e.g. _"Do NOT introduce a web framework — Node core `http` only (AD-1)"_.
This is how an approved architecture becomes an enforced constraint on generated code.

Now update the `persistent_facts` you neutralized in §2.4 to point at the real filenames, in all
three of `_bmad/custom/bmad-create-story.toml`, `bmad-dev-story.toml`, `bmad-code-review.toml`.

---

## 9. Phase 3c — Epics, stories, readiness

### 9.1 Epics and stories

> **"create the epics and stories list"**

From `_bmad/custom/bmad-create-epics-and-stories.toml`:

- **Persistent fact:** every approved story is mirrored to
  `planning-artifacts/epics/epic-<n>-<slug>/story-<e>.<s>-<slug>.md`.
  **`epics.md` remains canonical** — downstream steps read it, the mirror is convenience only.
- **On complete:** confidence score logged for the epics/stories set.

### 9.2 Readiness check

> **"check implementation readiness"**

Cross-validates PRD ↔ UX ↔ Architecture ↔ Epics/Stories for alignment and completeness. Produces a
readiness report. **Do not skip this in the demo** — it is the last cheap place to catch drift
before code costs money.

---

## 10. Phase 4 — Implementation

### 10.1 Sprint planning

> **"run sprint planning"**

Writes `_bmad-output/implementation-artifacts/sprint-status.yaml` — the ordered plan the
implementation agents follow.

Anytime: **"check sprint status"**.

### 10.2 Create the story context

> **"create the next story"** (or `"create story 1.2"`)

Produces a story file in `implementation-artifacts/` carrying everything the dev agent needs:
acceptance criteria, referenced ADs, and the context files to load.

Then: **"validate story"** — readiness/completeness check before any code is written.

### 10.3 Dev the story — the plan-first hard gate

> **"dev this story <story-file>"**

This is the centerpiece. Per `_bmad/custom/bmad-dev-story.toml`, **before any code is generated**
the agent must:

1. Load `.ai-context.md` and the conditional context files relevant to the story.
2. Write `<story-dir>/<story_key>-plan.md` with frontmatter
   (`story, date, status: pending-approval, confidence, confidence_label, confidence_rationale`)
   and these fixed sections:

   |                          |                                  |
   | ------------------------ | -------------------------------- |
   | Scope Summary            | Impacted Modules & Files         |
   | Detailed Design Approach | Data Model Usage                 |
   | API/Interface Changes    | Error Handling & Edge Cases      |
   | Security Considerations  | Performance Considerations       |
   | Test Strategy            | Risks/Assumptions & Dependencies |
   | Context Files Consulted  | Rationale Summary                |

3. Self-assess plan confidence (0–100 + Low/Medium/High + rationale), lowered for each flagged
   assumption, unresolved version/library uncertainty, or story detail it had to guess at. Log it
   via `agent-project-logger` with `stage='implementation-plan'`.
4. **Present the plan and STOP.**

To proceed you must type this **exact** phrase:

```
Plan reviewed and approved. Proceed with code generation strictly as per this plan.
```

`"yes"`, `"looks good"`, `"go ahead"` are explicitly **not** sufficient and must not be treated as
approval. On approval the plan's `status` flips to `approved`. If the plan changes materially
afterwards, the gate **resets** to `pending-approval` and must be satisfied again.

Generated code must stay strictly inside the approved plan's stated files/modules/schemas — no
out-of-scope refactors, no new patterns, without stopping to ask.

**Demo beat:** try `"yes, go ahead"` first and let it refuse. That single refusal sells the whole
governance story better than any slide.

### 10.4 Per-file confidence scoring (deterministic)

After the story's Status is set to `review`, `on_complete` invokes `confidence-scorer` **once per
file** in the story's File List — never batched, never skipped. For each file it passes measured
values only:

| Signal               | Source                                                                 | Weight                     |
| -------------------- | ---------------------------------------------------------------------- | -------------------------- |
| tests passed/failed  | the regression suite already run, filtered to that file                | 40                         |
| lint errors/warnings | project linter run against that file                                   | 25 (−20/error, −5/warning) |
| lines changed        | `git diff --stat <baseline_commit> -- <file>`                          | 20 (ratio buckets)         |
| revision cycles      | count of prior "Senior Developer Review (AI)" cycles in the Change Log | 15                         |

Labels: **High ≥ 80, Medium 50–79, Low < 50** (`label_cutoffs` in the scorer's `customize.toml`;
weights and cutoffs are team-configurable, the formula and rationale template are not).

The distinction to state out loud: **the plan score is the model's self-assessment of a plan;
the file score is arithmetic over tool output.** Same log, different epistemics.

One row per file lands in `_bmad-output/<project_name>-project-log.csv`, and the agent reports a
file/confidence/label table before ending.

### 10.5 Code review — must be a fresh session

> **"run code review"**

`_bmad/custom/bmad-code-review.toml` enforces:

- **Fresh-session rule:** never review in the same session that generated the code. If it is the
  same session, the agent must say so and recommend restarting. **Open a new Claude Code session
  for this step in the demo.**
- **Diff-to-plan reconciliation:** `git diff` every changed file against the plan's _Impacted
  Modules & Files_; flag files in the diff but not the plan (scope creep) **and** files in the plan
  but not the diff (incomplete implementation). Result documented in the review output.
- **Fixed severities:** CRITICAL (security/data-loss — escalate to Tech Lead) · HIGH (plan deviation,
  unhandled exception, perf risk) · MEDIUM (standards, missing log, naming) · LOW (style).
- **Review-completeness confidence** — scores _how thorough this review pass was_, not how good the
  code is. Lowered for a failed reviewer lens, `no-spec` mode, or a chunked/oversized diff.
  Logged with `stage='code-review'`.

Findings → back to **"dev this story"** for fixes (which increments revision cycles, which lowers
the next file confidence score — the loop is self-penalizing, by design).

### 10.6 Optional closers

- **"create qa automated tests for <feature>"** → `bmad-qa-generate-e2e-tests`
- **"checkpoint"** → `bmad-checkpoint-preview`, a guided human walkthrough of the change
- **"let's retro the epic <n>"** → `bmad-retrospective`
- **"correct course"** → `bmad-correct-course`, when a mid-sprint change invalidates upstream docs

---

## 11. The fast path (when you don't want the full ceremony)

> **"quick dev: <intent>"** → `bmad-quick-dev`

Unified intent-in / code-out: clarify → plan → implement → review → present. It still runs
`confidence-scorer` on every file changed since the baseline commit (`stage='quick-dev'`).

Use it to contrast against the governed path: same scoring, none of the approval gates. Useful for
answering _"do we have to do all of this every time?"_ — no, but then no gate caught anything.

---

## 12. The audit trail — the customer's real deliverable

```bash
column -s, -t _bmad-output/<project_name>-project-log.csv | less -S
```

Header:

```
date,time,user,action,stage,agent,doc_status,confidence,confidence_label,confidence_rationale,doc_path
```

Append-only. One action, one row — never batched, never summarized. `user` is the BMAD
`user_name` from `_bmad/config.user.toml`, **not** the git identity.

Show, in one screen: brief generated → scored → reviewed → approved → PRD started → scored →
architecture → stories → implementation plan scored → each generated file scored → code review
scored. That single CSV _is_ the compliance artifact.

Supporting evidence: per-artifact `.memlog.md` run logs, `approval-state.json` hashes, and
`PromptGateway/logs/audit.db`.

---

## 13. Suggested demo running order (~45 min)

| #   | Beat                                                                                          | Minutes |
| --- | --------------------------------------------------------------------------------------------- | ------- |
| 1   | Repo tour: stock BMAD skills vs `_bmad/custom/*.toml` governance overlay                      | 3       |
| 2   | PromptGateway BLOCK on a prompt containing a secret                                           | 3       |
| 3   | Create brief → auto review report → confidence score → approve                                | 8       |
| 4   | Edit the approved brief → PRD generation **blocked** as stale; husky reverts status on commit | 4       |
| 5   | PRD → architecture (show AD-numbered decisions) → approve each                                | 8       |
| 6   | Epics/stories → readiness check → sprint plan                                                 | 5       |
| 7   | Dev story: plan written, `"yes go ahead"` **refused**, exact phrase accepted                  | 7       |
| 8   | Per-file deterministic confidence table                                                       | 3       |
| 9   | Fresh-session code review with diff-to-plan reconciliation                                    | 3       |
| 10  | The audit CSV, end to end                                                                     | 2       |

Pick a small feature. One epic, two stories, ~3 files. The point is the _governance chain_, not the app.

---

## 14. Troubleshooting

| Symptom                                                            | Cause                                                                                                            | Fix                                                          |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Gate blocks with `reason: "unapproved"` on a doc you just approved | `approval-state.json` holds a different absolute path (e.g. stale Windows `D:\...` entry, or repo moved/renamed) | `echo '{}' > _bmad/custom/approval-state.json`, re-approve   |
| `reason: "stale"` unexpectedly                                     | Content changed by even one byte since approval; the check also reverts frontmatter to `draft`                   | Re-approve, or `git checkout` the doc                        |
| `[Marshal] PromptGateway check skipped (unreachable)`              | Gateway not running — hook **fails open** by design                                                              | Start uvicorn on :8000 (§3)                                  |
| Governance steps silently don't run                                | `uv` missing → `resolve_customization.py` fails → customization not merged                                       | Install `uv`, re-run the §1 sanity check                     |
| Docs land in a folder named `brief-BMAD-...`                       | `[core] project_name` still `BMAD` in installer-managed `_bmad/config.toml`                                      | Pin in `_bmad/custom/config.toml` (§2.3b)                    |
| Log rows go to the wrong CSV                                       | `_bmad/custom/project.json` still names the old project                                                          | Update `project_name`                                        |
| Dev agent starts coding without a plan                             | `bmad-dev-story.toml` `persistent_facts` were edited/dropped                                                     | Restore the plan-first gate fact verbatim                    |
| Code review is suspiciously clean                                  | Review ran in the generating session (self-review bias)                                                          | Restart in a fresh session — the skill is supposed to refuse |
| `git commit` rewrites your doc                                     | `.husky/pre-commit` reverting `approved` → `draft` on a content change                                           | Intended. Re-approve through `agent-approval-grant`          |

---

## 15. Re-running the demo from clean

```bash
git checkout demo/greenfield-run
git reset --hard <baseline-commit-from-§2.5>
git clean -fd _bmad-output
echo '{}' > _bmad/custom/approval-state.json
```

Confirm `_bmad/custom/*.toml`, `skills/`, and `.claude/` survived — those are the demo.
