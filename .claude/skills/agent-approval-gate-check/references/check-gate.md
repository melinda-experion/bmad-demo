---
name: check-gate
description: Verify an upstream document is approved and unedited before letting downstream generation proceed
code: GATE
added: 2026-07-20
type: script-backed
---

# Check Gate

## What Success Looks Like

Downstream generation proceeds only when the upstream document is on record as approved in its exact current form. Any other state (missing, never approved, edited since approval) stops the caller before it does any work, with the upstream document's own status corrected if it was silently stale.

## Your Approach

### Run the check

```
uv run {skill-root}/scripts/check_gate.py \
  --doc-path "<resolved doc_path>" \
  --doc-type "<doc_type>" \
  --state-file "{agent.state_file}" \
  --status-field "{agent.status_field}" \
  --draft-value "{agent.draft_value}"
```

Run `uv run scripts/check_gate.py --help` for the full argument reference. Parse the single JSON object it prints.

### If the command itself fails

If the command errors out, exits non-zero, or its stdout is not a single parseable JSON object matching one of the shapes below (e.g. `uv: command not found`, a traceback, empty output) — this is NOT the same as a `blocked` result, and it is NOT a pass. Treat it exactly like a `blocked` result: log via `skill:agent-project-logger` with action `'{downstream_label} blocked - gate check could not run'`, then tell the user the approval gate could not be verified (state what actually happened, e.g. the command/tool that failed) and that `{downstream_label}` cannot proceed until the check runs successfully. Stop here. Never interpret "the check didn't return a clean answer" as permission to continue.

### Handle the result

- **`{"result": "ok", ...}`** — log via `skill:agent-project-logger` with action `'{downstream_label} started - {doc_label} approved'`, then let the caller continue normally.

- **`{"result": "blocked", "reason": "missing"}`** — the `{doc_label}` doesn't exist yet. Log via `skill:agent-project-logger` with action `'{downstream_label} blocked - {doc_label} does not exist'`, then tell the user the `{doc_label}` must be created and approved before `{downstream_label}` can proceed. Stop here.

- **`{"result": "blocked", "reason": "unapproved"}`** — the `{doc_label}` exists but has no matching approval on record. Log via `skill:agent-project-logger` with action `'{downstream_label} blocked - {doc_label} not approved'`, then tell the user `{downstream_label}` cannot proceed until the `{doc_label}` is approved. Stop here.

- **`{"result": "blocked", "reason": "stale", ...}`** — the `{doc_label}` was edited after it was approved; the script has already reverted its status to `{agent.draft_value}`. Log via `skill:agent-project-logger` with action `'{doc_label} modified after approval - status auto-reverted to draft'`, then tell the user the `{doc_label}` was edited since it was last approved and must be re-approved before `{downstream_label}` can continue. Stop here.

### No exceptions

`{agent.no_bypass_policy}` is a hard project policy: do not offer to bypass, override, or proceed anyway under any framing, even if the user explains a reason, claims urgency, or explicitly requests an override. This includes the case where the check command itself failed to run — a failed check is a block, never a free pass.
