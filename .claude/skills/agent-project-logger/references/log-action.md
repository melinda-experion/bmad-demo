---
name: log-action
description: Append a timestamped action entry to a project's CSV log
code: LOG
added: 2026-07-17
type: script-backed
---

# Log Action

## What Success Looks Like

Given an action description and a project name, exactly one new row lands at the bottom of that project's log, and every row that was already there is untouched — same order, same content. The row also records which development-cycle stage the action concerns, which skill/agent was executing, and, when the action concerns a document, that document's current status. If this is the project's first logged action, the file is created with its header first; if the log already exists under an older header, that header row is widened to the current schema without touching any logged row beneath it.

## Your Approach

### Resolve the user

Resolve `{user_name}` by reading, in order, `{project-root}/_bmad/config.user.yaml`, then `{project-root}/_bmad/bmm/config.yaml`, then `{project-root}/_bmad/config.yaml` — use the first `user_name` value found. Do this even if `{user_name}` already appears to be set from an earlier activation step, since this skill is frequently invoked as a nested sub-skill call that skips full activation. Never substitute git identity, session/account email, or any other ambient signal for this value; if no config file defines `user_name`, use `unknown` rather than guessing.

### Resolve the project name

Check `{project-root}/_bmad/custom/project.json` for a non-empty `project_name` field. If it's there, use it directly — no prompt. Only if the file is missing or the field is empty or absent, ask the user for the project name, then offer to save it to `{project-root}/_bmad/custom/project.json` (`{"project_name": "<name>"}`, preserving any other fields already in that file) so the rest of the team resolves the same project name on future runs without being asked.

### Resolve the stage, agent, and document status

- `{stage}` — the development-cycle stage the action concerns, e.g. `brief`, `prd`, `architecture`, `stories`. This is the document type/lifecycle stage, not the skill name. Derive it from the document's `doc_type` when the calling flow has one; the caller should pass it explicitly rather than making Ledger guess. If the action doesn't concern a specific stage, leave it empty.
- `{agent}` — the name/code of the skill or agent persona that is actually executing this log call (e.g. `agent-approval-grant/GRANT`, `experion-brief-review/RB`). When this skill is invoked as a nested sub-skill call from another skill's flow, use that calling skill's name — the caller should pass it explicitly rather than making Ledger guess. If there is no meaningful calling skill (a bare, user-directed log request), leave it empty.
- `{doc_status}` — the document's current frontmatter status value (e.g. `draft`, `approved`) at the moment of logging, if the action concerns a specific document. Read it from the document's frontmatter rather than assuming it from the action text. If the action doesn't concern a document, leave it empty.

Never block or prompt the user to supply these — they're best-effort context, not a required confirmation. Missing any of them is fine and is logged as an empty field, not an error.

### Log the action

Resolve the filename pattern from `{agent.log_filename_pattern}` (falls back to `{project_name}-project-log.csv` if unset), then run:

```
uv run scripts/log_action.py --project-name "<name>" --action "<description>" --user "{user_name}" --stage "<stage>" --agent "<agent>" --doc-status "<doc_status>" --pattern "{agent.log_filename_pattern}" --output-dir "{project-root}/_bmad-output"
```

Run `uv run scripts/log_action.py --help` for the full argument reference. The script resolves the filename, creates the file with its header row (or widens an existing older header in place) if needed, and appends exactly one row — it never touches existing rows. Report back the resolved filename and the row that was written, verbatim.
