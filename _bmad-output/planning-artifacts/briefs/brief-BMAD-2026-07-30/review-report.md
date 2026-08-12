---
title: Review — BMAD Idea Launcher Implementation Status Brief
brief_version: 1
date: 2026-07-30
---

# Adversarial Review: BMAD Idea Launcher — Implementation Status Brief

## Summary Assessment

No critical findings. This brief is unusually well-grounded for its type — nearly every claim traces to a specific file and line rather than inference — but two dimensions (defensibility of stated goals, target-user definition) are effectively absent rather than weak, and one moderate scope-creep tension runs through the Open Questions and Branch Context sections despite the Purpose section's explicit "no new scope" claim. Four dimensions need a look before this goes to a wider audience; none block the document from serving its stated purpose as-is.

## 1. Problem Statement Clarity — Moderate

The Purpose section (lines 13–15) states *what* the document does ("answers one question... of what v1 promised, what has been built?") but never states *why this needed answering now* — what decision, risk, or trigger made this audit necessary. Without that, a stakeholder reading cold has no way to judge urgency or weigh the audit against other work. Compare to the v1 brief it's built on, which opens with an explicit problem statement ("The Problem" section). This document has no equivalent — the closest is the implicit framing "it is the factual base a future v2 scoping decision would start from," which describes a *use*, not a *problem*.

## 2. Defensibility of Stated Goals — Moderate (section absent)

There is no goals or success-criteria section, and none of the fixed dimensions this document could be checked against are stated explicitly. That's a defensible choice for a status report — but the Open Questions section then asks normative questions ("Should FR-4 be treated as the next priority?" — line 62 as of last full read) without stating what evidence or criteria would answer them. A skeptic's "how would we know if we failed at this?" has no anchor: there's no stated bar for what makes the *audit itself* complete or correct (e.g., what would count as a missed implementation detail, how confident the "Not implemented" calls are for behavior that might exist but wasn't grep-able).

## 3. Hidden or Unstated Assumptions — Moderate

Two assumptions aren't surfaced anywhere, including the Assumptions Index (which currently names only one — the story-doc-currency assumption):

- **Working-tree state vs. committed state.** The audit read `server.js`/`public/app.js`/etc. as they exist in the working tree at the time of audit, but never states whether that reflects the last commit, uncommitted local changes, or a mix. Given this session independently discovered uncommitted deletions of other planning artifacts in this same working tree, treating the working tree as "the implementation" without that caveat is a real gap — a reader can't tell if this status would hold after a `git status` check.
- **Absence-as-proof via static search.** Every "Not implemented" verdict rests on the absence of a pattern (grep for "favorite", "localStorage", "gateway", etc.) in specific files. That's reasonable evidence but isn't proof — a differently-named implementation, a feature behind a build step not inspected, or dead code elsewhere wouldn't be caught. The document states each finding with the same confidence as the "Implemented" findings, which had direct positive evidence; the asymmetry isn't flagged.

## 4. Scope-Creep Risk — Moderate

The Purpose section is explicit: "It commits to no new scope." But two places lean past pure diagnosis into implicit recommendation:

- **Branch Context section** (PromptGateway) ends with a `[NOTE FOR PM]` suggesting the LLM service "should" call PromptGateway before hitting the LLM — a design recommendation, not a status observation.
- **Open Questions 2 and 3** are phrased as "should X be the next priority" / "should X route through Y" rather than as diagnostic questions ("is X blocked by Y," "does X exist"). Phrasing goals as "should" questions is a half-step into scoping the very v2 work the Purpose section says this document doesn't commit to. Not a hard violation, but the boundary the brief promises is softer in practice than the Purpose section claims.

## 5. Gaps in Target-User Definition — Moderate (section absent)

No section states who this document is for. The brief was clearly produced for a PM making a v2 scoping call (per this session's conversation), but that's nowhere in the document itself — a reader encountering only `brief.md` (an engineer picking it up cold, say) has no signal for how much implementation detail is load-bearing versus how much is there to support a PM's later decision. Given the document mixes file-and-line evidence (engineer-legible) with "no new scope" / "next BMAD steps" framing (PM-legible), naming the intended reader would resolve real ambiguity about how the document should be used.
