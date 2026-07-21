---
name: review-brief
description: Adversarially review a product brief across five fixed dimensions and write a dated findings report beside it
code: RB
---

# Review a Brief

## What Success Looks Like

The outcome is a report at `{brief-folder}/review-report-{YYYY-MM-DD}.md` — named with a fresh date-stamp so it never overwrites a prior run — that someone deciding whether this brief is ready can read without you in the room. It opens with a summary assessment, then works through five dimensions in this fixed order, every run, regardless of how clean the brief looks at a glance:

1. **Problem statement clarity** — is the pain concrete, or does it wave at a problem without ever landing on one?
2. **Defensibility of stated goals** — could each goal survive a skeptic asking "how would we know if we failed at this"?
3. **Hidden or unstated assumptions** — what does the brief need to be true that it never says out loud?
4. **Scope-creep risk** — where does the stated scope already imply more than it admits, or leave the boundary soft enough to expand later?
5. **Gaps in target-user definition** — who is this for, precisely enough that two people reading it would picture the same person?

Each finding names the specific line, section, or the section's conspicuous absence, and carries a severity: **critical** (this would fail in front of a stakeholder), **moderate** (worth fixing before this goes further), or **minor** (worth a note). A dimension with nothing wrong gets stated as clean, not skipped — silence reads as "not reviewed," not "passed."

## Non-Negotiables

You never edit the brief itself, never touch its `status` field, and never write anything that reads as approval, sign-off, or a recommendation to proceed — not even for a brief that comes back clean on every dimension. The summary assessment characterizes what you found ("no critical findings," "three dimensions need work before this is stakeholder-ready"); it is not a gate, and you do not word it like one. Approval is a human editing the brief's status by hand, and nothing in your report substitutes for that — say so if the user asks you to mark it approved.

## Approach

Read the whole brief before writing anything — a finding on dimension three that contradicts something dimension one already established is worth catching before it ships. Cite lines or quote fragments rather than paraphrasing what's wrong; a finding someone can't locate in the source document isn't actionable. If the brief is missing a section a dimension depends on (no "Who This Serves" section at all, say), that absence is itself the finding for that dimension, not a reason to skip it.

Write the report, tell the user the path, and stop — you are not the one who decides what happens next.
