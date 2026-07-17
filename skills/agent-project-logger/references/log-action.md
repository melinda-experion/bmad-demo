---
name: log-action
description: Append a timestamped action entry to a project's CSV log
code: LOG
added: 2026-07-17
type: script-backed
---

# Log Action

## What Success Looks Like

Given an action description and a project name, exactly one new row lands at the bottom of that project's log, and every row that was already there is untouched — same order, same content. If this is the project's first logged action, the file is created with its header first.

## Your Approach

### Resolve the project name

Check `{project-root}/_bmad/custom/project.json` for a non-empty `project_name` field. If it's there, use it directly — no prompt. Only if the file is missing or the field is empty or absent, ask the user for the project name, then offer to save it to `{project-root}/_bmad/custom/project.json` (`{"project_name": "<name>"}`, preserving any other fields already in that file) so the rest of the team resolves the same project name on future runs without being asked.

### Log the action

Resolve the filename pattern from `{agent.log_filename_pattern}` (falls back to `{project_name}-project-log.csv` if unset), then run:

```
uv run scripts/log_action.py --project-name "<name>" --action "<description>" --user "{user_name}" --pattern "{agent.log_filename_pattern}" --output-dir "{project-root}/_bmad-output"
```

Run `uv run scripts/log_action.py --help` for the full argument reference. The script resolves the filename, creates the file with its header row if it doesn't exist yet, and appends exactly one row — it never touches existing rows. Report back the resolved filename and the row that was written, verbatim.
