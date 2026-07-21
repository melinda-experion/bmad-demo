---
name: grant-approval
description: Double-confirm with the user, then mark a document approved and record it in the shared approval-state.json
code: GRANT
added: 2026-07-20
type: script-backed
---

# Grant Approval

## What Success Looks Like

The document's frontmatter status is `{agent.approved_value}` and the shared state file has a fresh `{doc_type}` entry recording the document's own post-save mtime — but only after the user gave two separate, explicit affirmatives. A decline at either point leaves the document untouched, in draft, and logged.

## Your Approach

### Resolve the user

Resolve `{user_name}` by reading, in order, `{project-root}/_bmad/config.user.yaml`, then `{project-root}/_bmad/bmm/config.yaml`, then `{project-root}/_bmad/config.yaml` — use the first `user_name` value found. Do this even if `{user_name}` already appears to be set from an earlier activation step, since this skill is frequently invoked as a nested sub-skill call that skips full activation. Never substitute git identity, session/account email, or any other ambient signal for this value; if no config file defines `user_name`, use `unknown` rather than guessing.

### First confirmation — reviewed and approved

Tell the user the `{doc_label}` is ready{, and the `{review_artifact_label}` is ready, if one was given}. Ask directly:

- If `review_artifact_label` was given: "Have you read the {review_artifact_label} and do you approve the {doc_label}?"
- Otherwise: "Do you approve the {doc_label}?"

Wait for an explicit affirmative response. If they decline or don't confirm: tell them the `{doc_label}` remains in draft status, log via `skill:agent-project-logger` with action `'{doc_label} approval declined or deferred'`, and stop here.

### Second confirmation — read the document itself

If they approved, ask a second, separate confirmation: "Please confirm you have read through the entire {doc_label} document itself, not just the {review_artifact_label, or 'summary'}, before I mark it approved." Wait for an explicit second affirmative. If they decline this second confirmation, leave status as draft, log `'{doc_label} approval declined at second confirmation'` via `skill:agent-project-logger`, and stop here.

### Grant it

Only after both confirmations are explicitly given, run:

```
uv run {skill-root}/scripts/grant_approval.py \
  --doc-path "<resolved doc_path>" \
  --doc-type "<doc_type>" \
  --state-file "{agent.state_file}" \
  --status-field "{agent.status_field}" \
  --approved-value "{agent.approved_value}"
```

This edits the document's frontmatter status, saves it, reads the file's own resulting mtime, and merges `{doc_type}: {doc_path, approved_mtime}` into the shared state file without disturbing any other doc_type's entry. Run `uv run scripts/grant_approval.py --help` for the full argument reference.

Then log via `skill:agent-project-logger` with action `'{doc_label} approved by {user_name}'`. Report back the resolved `doc_path` and `approved_mtime` from the script's output, verbatim.
