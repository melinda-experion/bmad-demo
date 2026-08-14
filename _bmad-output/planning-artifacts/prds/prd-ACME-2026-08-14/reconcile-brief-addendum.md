# Reconciliation: Brief Addendum vs. PRD (+ PRD Addendum)

**Source input:** `_bmad-output/planning-artifacts/briefs/brief-ACME-2026-08-14/addendum.md`
**Downstream:** `_bmad-output/planning-artifacts/prds/prd-ACME-2026-08-14/prd.md` and its `addendum.md`

Method: each of the source addendum's three sections (deferred
favorite/save-step, success-criteria prioritization note, persona note)
checked against the PRD and PRD addendum for whether it was carried
forward faithfully, dropped, or contradicted.

---

## 1. Deferred favorite/save-triage step — mostly carried forward, rationale thinned

**Source says:** Deferred (not rejected) specifically *because* v1 scope
was chosen to keep the demo tight — "one epic, ~3 files, matching the
runbook's ~45-minute demo budget." Natural candidate for epic 2 if the
demo needs a second epic-to-epic pass (sprint planning, second dev/review
cycle).

**PRD/PRD-addendum status:**
- PRD §6 Non-Goals and §7.2 both flag the deferral and cross-reference
  "see brief's addendum.md for the rationale" — they don't restate it.
- PRD addendum's "Favorite/save-triage step" section restates the
  *mechanics* of epic 2 (client-side toggle, no persistence, no backend
  change) but not the *reason* v1 stayed single-epic (the ~3-files /
  ~45-minute-demo-budget constraint) or the specific epic-2 trigger
  (showing epic-to-epic sprint planning, or a second dev/review pass).
- PRD Open Question 2 asks whether epic 2 becomes real, correctly
  attributing "brief's addendum" but again without restating the budget
  reasoning.

**Gap:** Minor. The deferral itself, and its status as "deferred not
rejected," survived intact and is referenced correctly in three places.
What silently dropped is the *specific rationale* (one-epic /~3-files
/~45-min budget) and the *specific epic-2 trigger conditions* (demo
epic-to-epic sprint planning or second dev/review pass) — a reader of the
PRD alone, without opening the brief's addendum, only learns "it's
deferred," not why or under what condition it would be reintroduced.

---

## 2. Success-criteria prioritization note — reflected in the PRD's own metrics, but not carried forward as a directive for future story ACs

**Source says:** "For the PRD workflow: acceptance criteria for **stories**
should overwhelmingly target demo-process success... The triage-quality
bar (product-fiction success) is real but secondary; a PRD that inverts
this priority optimizes the wrong thing for what this repo is actually
for." This is explicitly about how **future story acceptance criteria**
should be weighted, not (only) about the PRD's own metrics.

**PRD status:**
- PRD §8 Success Metrics does structurally mirror the priority: "Primary —
  Demo-process success" (SM-1 through SM-4) vs. "Secondary — Product-
  fiction success" (SM-5, SM-6), explicitly labeled and explained ("kept
  explicit rather than blended... collapsing these into one list would
  misrepresent what this repo is actually for"). This part is a faithful,
  well-executed carry-forward of the *spirit* of the note.
- However, nothing in the PRD (§1 Document Purpose — addressed to
  "whoever builds the architecture, epics, and stories that follow it" —
  Open Questions, or Assumptions Index) explicitly restates the rule for
  the artifact the source addendum actually named: **story-level
  acceptance criteria**. The PRD's FR "Consequences (testable)" blocks
  (FR-1–FR-6) are all product-fiction-flavored by necessity (they describe
  triage behavior, not demo-process gates) — there is no explicit note
  anywhere telling whoever writes epics/stories next that *their*
  acceptance criteria should overwhelmingly skew toward demo-process
  success (gate holds, plan-first refuses bare "yes", confidence scoring
  logs) over triage-quality checks.

**Gap:** Real but partial. The PRD's own Success Metrics section honors
the priority for itself. The explicit *instruction* — carry this same
priority into story acceptance criteria — is not restated anywhere as
forward-looking guidance for the epics/stories author, so the safeguard
the addendum was written to install (prevent a future story-writer from
inverting the priority) has no textual anchor in the PRD itself; it exists
only in the brief's addendum, one document upstream of where it's needed.

---

## 3. Persona note — a different, narrower guardrail survived; the original one is silently dropped

**Source says:** The support-agent persona is explicitly demo-only. If a
future run of this repo wants **the support-agent persona itself** to
carry more weight — the example given: "a customer specifically asks
'would this actually work for our support team'" — that's a signal to
**re-run Discovery on the brief**, rather than let a downstream document
(PRD) **quietly upgrade an illustrative persona into a researched one**.

**PRD/PRD-addendum status:**
- PRD §1 does call the Target User an "illustrative support agent" once,
  which correctly preserves the persona's non-researched status as of
  now.
- PRD addendum's "On the two 'Primary' personas" section discusses
  re-running Discovery — but for a **different trigger**: if a future run
  needs the **demo audience** (the second, discarded persona) to become a
  **formal product user** generating its own FRs (tied to Open Question
  4's "audience view" idea). That is a distinct scenario from the source
  note's concern.
- Nowhere in the PRD or PRD addendum does the specific guardrail from the
  source survive: that if the **support-agent persona's research weight**
  increases (e.g., a real customer asks whether this would work for their
  actual support team), the correct move is to re-run Discovery on the
  **brief**, not let the PRD (or a future PRD revision) silently treat the
  illustrative persona as validated.

**Gap:** Real. The PRD substitutes a related-but-different persona
safeguard (demo-audience-as-second-persona) for the one the source
addendum actually specified (support-agent-persona-as-researched-persona).
The specific trigger example and the specific failure mode it guards
against — the PRD quietly upgrading persona rigor without a Discovery
re-run — has no equivalent anywhere downstream.

---

## Summary Table

| Source addendum item | Carried forward? | Note |
|---|---|---|
| Favorite/save-step deferral (fact) | Yes | Referenced in 3 places |
| Favorite/save-step rationale (why: 1 epic/~3 files/~45min) | No (dropped) | Only cross-referenced, never restated |
| Favorite/save-step epic-2 trigger conditions | No (dropped) | "sprint planning" / "second dev-review pass" triggers not restated |
| Success-metrics Primary/Secondary priority (PRD's own metrics) | Yes | §8 structure faithfully mirrors it |
| Priority as a directive for future story ACs | No (dropped) | No forward-looking instruction to epics/stories author |
| Persona: illustrative status (fact) | Yes | §1 calls it "illustrative" |
| Persona: re-run-Discovery-on-brief guardrail (specific trigger) | No (dropped/substituted) | PRD addendum covers a different persona-related trigger (demo audience becoming formal), not this one |

No outright contradictions were found — all three gaps are omissions
(rationale or directive silently dropped) rather than the PRD stating
something inconsistent with the source addendum.
