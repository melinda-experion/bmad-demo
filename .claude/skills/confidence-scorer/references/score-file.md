---
name: score-file
description: Compute and log a deterministic code-confidence score for one file
code: SCORE
added: 2026-08-03
type: script-backed
---

# Score File

## What Success Looks Like

Given a generated code artifact (a set of changed files from a story implementation or similar run), every file in that artifact gets exactly one new row in the project's existing audit log, via `log_action.py` -- no new files, no new schema, no LLM-guessed number. Each row's `confidence` is the output of `confidence_score.py`, computed purely from measured counts (test results, lint results, diff size, revision cycles), never from the model's own impression of the code.

## Your Approach

### Resolve the user, project name, and stage

Resolve `{user_name}` and the project name the same way `agent-project-logger` does: `{user_name}` from `{project-root}/_bmad/config.user.yaml` → `{project-root}/_bmad/bmm/config.yaml` → `{project-root}/_bmad/config.yaml` (first value found, else `unknown`); project name from `{project-root}/_bmad/custom/project.json`'s `project_name` field, asking and offering to save it only if absent.

`{stage}` is the development-cycle stage this run concerns (e.g. `stories`, `dev`). `{doc_type}` is the state-file key for this specific run (e.g. `story-3.2`) -- prefer a value the calling flow already knows (the story ID) over the generic `{agent.doc_type}` fallback in `customize.toml`.

### Enumerate the files to score

Take the list of files changed by the code artifact under review (e.g. from `git diff --name-only` against the base the story branched from, or the file list the calling flow already has). Score every file in that list -- do not sample or skip files to save time; if a file must be skipped (e.g. binary, generated, vendored), say so explicitly rather than silently omitting its row.

### Gather raw signals per file (deterministic tools only, never a model guess)

For each file:

- **Tests**: run the project's actual test runner filtered to tests that touch this file (by path convention, import graph, or coverage mapping -- whatever the project already uses), and count passed/failed. If no tests touch the file, both counts are 0.
- **Lint**: run the project's actual linter/static-analysis tool against this file and count errors and warnings separately.
- **Diff size**: run `git diff --stat` (or equivalent) for this file against the base ref to get lines changed (added + removed); the file's current total line count is read automatically by `confidence_score.py` from `--file-path` unless you pass `--file-size` explicitly.
- **Revision cycles / doc_status**: leave these to the script -- pass `--state-file "{agent.state_file}" --doc-type "{doc_type}"` and it resolves both from `approval-state.json` (a missing entry is `unapproved`; a `superseded: true` entry is `draft` with its cycle count from that document's frontmatter `version`; otherwise `approved` with that same `version`). Only pass `--revision-cycles` / `--doc-status` explicitly if the calling flow already computed them some other way.

None of these four steps involve the model rating the code -- they are tool invocations whose output is fed straight into the script as numbers.

### Compute the score

Run, once per file:

```
uv run {skill-root}/scripts/confidence_score.py \
  --file-path "<file>" \
  --tests-passed <n> --tests-failed <n> \
  --lint-errors <n> --lint-warnings <n> \
  --lines-changed <n> \
  --state-file "{agent.state_file}" --doc-type "<doc_type>" \
  --test-weight {agent.test_weight} --lint-weight {agent.lint_weight} \
  --diff-weight {agent.diff_weight} --revision-weight {agent.revision_weight} \
  --no-tests-score {agent.no_tests_score} \
  --error-penalty {agent.error_penalty} --warning-penalty {agent.warning_penalty} \
  --diff-ratio-cutoffs '{agent.diff_ratio_cutoffs}' \
  --revision-cycle-cutoffs '{agent.revision_cycle_cutoffs}' \
  --label-cutoffs '{agent.label_cutoffs}'
```

Run `uv run scripts/confidence_score.py --help` for the full argument reference. It prints one JSON object: `{file_path, confidence, confidence_label, confidence_rationale, doc_status, components}`. `confidence_rationale` is already a fully detailed, templated string covering all four signals -- each one's phrase, raw score, weight, and weighted contribution to the final number (e.g. `"test: 9/9 tests passed (score=100, weight=40%, contrib=40.0); lint: no lint issues (score=100, weight=25%, contrib=25.0); diff: 115 lines changed of 115 (100%) (score=40, weight=20%, contrib=8.0); revision: no revision cycles (score=100, weight=15%, contrib=15.0); total=88"`) -- pass it through to the log verbatim, do not rewrite, rephrase, or shorten it.

### Log the result (one row per file)

Call `skill:agent-project-logger` -- or run `log_action.py` directly -- once per file:

```
uv run {log-action-skill-root}/scripts/log_action.py \
  --project-name "<name>" \
  --action "code_scored" \
  --user "{user_name}" \
  --stage "{stage}" \
  --agent "confidence-scorer" \
  --doc-status "<doc_status from the script output>" \
  --confidence "<confidence>" \
  --confidence-label "<confidence_label>" \
  --confidence-rationale "<confidence_rationale>" \
  --doc-path "<file>" \
  --pattern "{agent.log_filename_pattern}" \
  --output-dir "{project-root}/_bmad-output"
```

Do this for every file before reporting back. Never batch multiple files' results into one row, and never skip a file's log row because its score was high -- passing scores are as much a part of the audit trail as failing ones.

### Report back

Summarize the run as a table of `file, confidence, label` (weakest first), plus how many rows were appended and to which log file. If any file's rationale flags a weak signal, call it out explicitly rather than letting it pass silently inside an aggregate.
