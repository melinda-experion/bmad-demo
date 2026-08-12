---
name: reopen-document
description: Confirm with the user, then reopen an approved document for revision and mark its approval-state entry superseded
code: REOPEN
added: 2026-07-23
type: script-backed
---

# Reopen Document

## What Success Looks Like

The document's frontmatter status is `{agent.reopen_value}` and the matching entry in the shared state file is kept but flagged `superseded: true` — never deleted, since it is the audit record of the approval that came before. Nothing moves until the user has explicitly confirmed, by name, that this document should be reopened and understood that it will need approving again afterward.

## Your Approach

### Resolve the user

Resolve `{user_name}` the same way Grant Approval does: read, in order, `{project-root}/_bmad/config.user.yaml`, then `{project-root}/_bmad/bmm/config.yaml`, then `{project-root}/_bmad/config.yaml`, and use the first `user_name` value found. Never substitute git identity, session/account email, or any other ambient signal; if none is defined, use `unknown`.

### Logging convention for this flow

Every step below ends with a `skill:agent-project-logger` call — pass or fail, this flow logs each step it takes, not just the terminal outcome. Every call passes three extra fields: `--stage "<doc_type>"`, `--agent "agent-approval-grant/REOPEN"`, and `--doc-status "<value>"`, where `<value>` is `doc_path`'s current frontmatter `{agent.status_field}` value read fresh at the moment of logging (re-read after `reopen_document.py` runs, since it will have changed).

Log `'{doc_label} reopen flow started'` now, before doing anything else.

### Confirm — by name, with the consequence stated

Ask a single, explicit confirmation that names the `{doc_label}` and states the consequence: "Reopening the {doc_label} will put it back in draft and it will need to be approved again before anything downstream can build on it. Do you want to reopen it?" Wait for an explicit affirmative.

- If they decline or don't confirm: leave the document and its approval-state entry untouched, log `'{doc_label} reopen declined'`, and stop here.
- If they affirm: log `'{doc_label} reopen confirmation received'` and continue.

### Reopen it

Only after the explicit affirmative, run:

```
uv run {skill-root}/scripts/reopen_document.py \
  --doc-path "<resolved doc_path>" \
  --doc-type "<doc_type>" \
  --state-file "{agent.state_file}" \
  --status-field "{agent.status_field}" \
  --reopen-value "{agent.reopen_value}"
```

This edits the document's frontmatter status to `{agent.reopen_value}` and, if a matching `{doc_type}` entry exists in the shared state file, adds `superseded: true` to it in place rather than removing it, without disturbing any other doc_type's entry. Run `uv run scripts/reopen_document.py --help` for the full argument reference.

Then log via `skill:agent-project-logger` with action `'{doc_label} reopened for review by {user_name}'` (`--doc-status` here is `{agent.reopen_value}`, the value the script just wrote). Report back the resolved `doc_path` and whether an approval-state entry was found and superseded.
