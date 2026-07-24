---
name: review-brief
description: Adversarially review a product brief across five fixed dimensions and write a version-tagged findings report beside it
code: RB
---

# Review a Brief

## What Success Looks Like

The outcome is a report at `{brief-folder}/review-report.md` — one canonical file, not one per run — with a `brief_version` frontmatter field set to `target_version`: the brief's current frontmatter `version` (0 if absent) plus one, i.e. the version the brief will carry once this draft is approved, and so the version this review is actually reviewing. History across re-reviews lives in git, the same way it does for the brief itself, not in parallel files. The report is one someone deciding whether this brief is ready can read without you in the room. It opens with a summary assessment, then works through five dimensions in this fixed order, every run, regardless of how clean the brief looks at a glance:

1. **Problem statement clarity** — is the pain concrete, or does it wave at a problem without ever landing on one?
2. **Defensibility of stated goals** — could each goal survive a skeptic asking "how would we know if we failed at this"?
3. **Hidden or unstated assumptions** — what does the brief need to be true that it never says out loud?
4. **Scope-creep risk** — where does the stated scope already imply more than it admits, or leave the boundary soft enough to expand later?
5. **Gaps in target-user definition** — who is this for, precisely enough that two people reading it would picture the same person?

Each finding names the specific line, section, or the section's conspicuous absence, and carries a severity: **critical** (this would fail in front of a stakeholder), **moderate** (worth fixing before this goes further), or **minor** (worth a note). A dimension with nothing wrong gets stated as clean, not skipped — silence reads as "not reviewed," not "passed."

## Non-Negotiables

You never edit the brief itself, never touch its `status` field, and never write anything that reads as approval, sign-off, or a recommendation to proceed — not even for a brief that comes back clean on every dimension. The summary assessment characterizes what you found ("no critical findings," "three dimensions need work before this is stakeholder-ready"); it is not a gate, and you do not word it like one. Approval is a human editing the brief's status by hand, and nothing in your report substitutes for that — say so if the user asks you to mark it approved.

## Approach

### Logging convention for this flow

Every step below ends with a `skill:agent-project-logger` call — pass or fail, this flow logs each step it takes, not just the terminal outcome. Every call passes `--stage "brief"`, `--agent "experion-brief-review/RB"`, `--user "{user_name}"`, and `--doc-status "<value>"`, where `<value>` is the brief's current frontmatter `status` value read fresh at the moment of logging (this flow never changes it, so it should read the same at start and end).

Log `'brief review started'` now, before reading the brief.

Read the whole brief before writing anything — a finding on dimension three that contradicts something dimension one already established is worth catching before it ships. Cite lines or quote fragments rather than paraphrasing what's wrong; a finding someone can't locate in the source document isn't actionable. If the brief is missing a section a dimension depends on (no "Who This Serves" section at all, say), that absence is itself the finding for that dimension, not a reason to skip it.

Compute `target_version` (the brief's current frontmatter `version`, 0 if absent, plus one) before writing. Write or overwrite `review-report.md` with frontmatter `brief_version: {target_version}` (plus `title` and `date`) followed by the report body — this replaces whatever was there for a prior version, since only the review of the version about to be approved has standing use.

Then stage and commit just that file: `git add review-report.md && git commit -m "Review brief v{target_version}"`, run from `{brief-folder}`. A failed commit doesn't undo the write — report the git error to the user rather than treating it as a review failure.

Log `'brief review completed - report at <resolved report path>, brief_version {target_version}'`, tell the user the path, and stop — you are not the one who decides what happens next.
