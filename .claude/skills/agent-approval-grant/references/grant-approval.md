---
name: grant-approval
description: Double-confirm with the user, then mark a document approved and record it in the shared approval-state.json
code: GRANT
added: 2026-07-20
type: script-backed
---

# Grant Approval

## What Success Looks Like

The document's frontmatter status is `{agent.approved_value}`, its frontmatter `version` has been bumped by one, and the shared state file has a fresh `{doc_type}` entry recording a content hash of the document's own post-save content — but only after the user gave two separate, explicit affirmatives. A decline at either point leaves the document untouched, in draft, and logged. The approved document is also staged and committed to git under the new version number, though a failed commit does not undo the approval itself. If a companion review skill is wired up for this `doc_type` and its review artifact is missing or predates the document's current content, that review is regenerated automatically, targeted at the version about to be approved, before anything is asked of the user.

## Your Approach

### Resolve the user

Resolve `{user_name}` by reading, in order, `{project-root}/_bmad/config.user.yaml`, then `{project-root}/_bmad/bmm/config.yaml`, then `{project-root}/_bmad/config.yaml` — use the first `user_name` value found. Do this even if `{user_name}` already appears to be set from an earlier activation step, since this skill is frequently invoked as a nested sub-skill call that skips full activation. Never substitute git identity, session/account email, or any other ambient signal for this value; if no config file defines `user_name`, use `unknown` rather than guessing.

### Logging convention for this flow

Every step below ends with a `skill:agent-project-logger` call — pass or fail, this flow logs each step it takes, not just the terminal outcome. Every call passes three extra fields: `--stage "<doc_type>"`, `--agent "agent-approval-grant/GRANT"`, and `--doc-status "<value>"`, where `<value>` is `doc_path`'s current frontmatter `{agent.status_field}` value read fresh at the moment of logging (re-read after `grant_approval.py` runs, since it will have changed).

Log `'{doc_label} approval flow started'` now, before doing anything else.

### Pre-flight: commit any pending edits to the document

Run `git status --porcelain -- <doc_path>` from `doc_path`'s directory. If it reports any pending changes (staged or unstaged), that content was edited outside this flow and never committed on its own — commit it now, before anything else touches this file: `git add <doc_path filename> && git commit -m "Update {doc_type} (draft)"`, run from `doc_path`'s directory.

This exists because of a real incident: a pre-commit hook (`scripts/revert-brief-status.js`, brief-specific but the failure mode generalizes) reverts a doc_type's approval status to draft on any commit that changes its content while status still reads approved — it's guarding against edits smuggled past approval. If a pending edit is left uncommitted and later gets swept into `grant_approval.py`'s own commit below, that hook fires against the *approval* commit itself and silently undoes the approval that was just granted, because that commit now contains both the status/version change and unrelated content. Clearing pending changes here, in their own commit, guarantees the approval commit later touches only status/version — which is what lets a hook like that do its job without ever mistaking a legitimate approval for a smuggled edit.

If there's nothing pending, log `'{doc_label} pre-flight check: no pending changes'` and continue. If there was something to commit, log `'{doc_label} pending edit committed before approval flow'` and continue. If the commit fails, tell the user the git error and stop here — do not proceed into an approval flow with unresolved uncommitted state.

### Check the review is current

Resolve `review_skill` from the argument if given, else `{agent.review_skill_defaults}[doc_type]`. Resolve `review_artifact_label` from the argument if given, else `{agent.review_artifact_label_defaults}[doc_type]`, else `"review report"` if a `review_skill` was resolved by either path. If no `review_skill` resolves, there's no companion review to keep current — log `'{doc_label} review currency check skipped: no review skill configured'` and continue straight to the first confirmation.

Otherwise, read `doc_path`'s current frontmatter `version` field (0 if absent) and compute `target_version = version + 1` — the version this document will carry once this approval lands, and so the version any companion review must be reviewing. Resolve the expected review artifact's filename as the `review_artifact_filename` argument if given, else `{agent.review_artifact_filename_defaults}[doc_type]`, else `"review-report.md"`, resolved in the same directory as `doc_path`. The version-tag frontmatter field that file must carry is `{doc_type}_version` (e.g. `brief_version` for a brief, `prd_version` for a PRD) — the doc_type-appropriate name the review skill writes.

- If that file doesn't exist, or its version-tag frontmatter field is absent or not equal to `target_version`, the review is missing or stale for the version about to be approved. Do not proceed to the first confirmation yet. Log `'{doc_label} review stale or missing for v{target_version} - regenerating via {review_skill}'`, then invoke `skill:{review_skill}` against `doc_path` — specifically its **Validate** (or equivalent standalone review) intent, not Create or Update, since for a full authoring skill invoking it bare would otherwise risk drafting new content instead of just reviewing what's there — to (re)generate the review artifact targeting `target_version`. Once it returns, re-read the file's version-tag field and confirm it now equals `target_version`; if it still doesn't (the review skill failed or targeted the wrong version), tell the user the review could not be regenerated and stop here rather than asking for approval against a stale or missing review.
- Otherwise (the review's version-tag already matches `target_version`), log `'{doc_label} review currency check passed for v{target_version}'` and continue.

### First confirmation — reviewed and approved

Tell the user the `{doc_label}` is ready{, and the `{review_artifact_label}` is ready, if one resolved}. Ask directly:

- If `review_artifact_label` resolved (given or defaulted): "Have you read the {review_artifact_label} and do you approve the {doc_label}?"
- Otherwise: "Do you approve the {doc_label}?"

Wait for an explicit affirmative response.

- If they decline or don't confirm: tell them the `{doc_label}` remains in draft status, log `'{doc_label} approval declined or deferred'`, and stop here.
- If they affirm: log `'{doc_label} first confirmation received'` and continue.

### Second confirmation — read the document itself

Ask a second, separate confirmation: "Please confirm you have read through the entire {doc_label} document itself, not just the {review_artifact_label, or 'summary'}, before I mark it approved." Wait for an explicit second affirmative.

- If they decline this second confirmation: leave status as draft, log `'{doc_label} approval declined at second confirmation'`, and stop here.
- If they affirm: log `'{doc_label} second confirmation received'` and continue.

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

This edits the document's frontmatter status, bumps its frontmatter `version`, saves it, hashes the file's own resulting content, merges `{doc_type}: {doc_path, approved_hash}` into the shared state file without disturbing any other doc_type's entry, and stages and commits the document to git with message `Approve {doc_type} v{version}`. A content hash is used rather than a timestamp because git does not preserve file mtimes across clone/pull/checkout — a teammate pulling the approval commit would otherwise get a local mtime later than the recorded approval time and the gate check would wrongly treat their untouched checkout as edited. Run `uv run scripts/grant_approval.py --help` for the full argument reference.

Then log via `skill:agent-project-logger` with action `'{doc_label} approved by {user_name}'` (`--doc-status` here is `{agent.approved_value}`, the value the script just wrote). Report back the resolved `doc_path`, `approved_hash`, and `version` from the script's output, verbatim.

Check the script's `git_commit` field. If `git_commit.ok` is `false`, the document is still approved — do not treat this as a failed approval — but tell the user plainly that the commit did not go through, along with `git_commit.error`, so they can commit it themselves if needed.
