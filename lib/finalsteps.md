Full Process Executed — Support Ticket Triage Demo
Stage 0 — Environment fixes (pre-BMAD)

0.1 Fix husky npm error 126 — chmod +x on .husky/pre-commit + node_modules/.bin/husky
0.2 Fix PromptGateway ModuleNotFoundError: fastapi — activate .venv (deps were already installed)
0.3 Refuse pasted API key → investigate why PromptGateway didn't flag it
0.4 Fix pii_validator.py regex gap (vendor-prefix + digit-required rules), add 3 tests, 40/40 pass
Stage 1 — Idea Brainstorm

1.1 Propose one app idea → user picks "Support Ticket Triage"
Stage 2 — Product Brief (bmad-product-brief + experion-brief-review)

2.1 Fast-path draft with [ASSUMPTION] tags
2.2 Reconciliation pass against inputs
2.3 Voss adversarial 5-dimension review → review-report.md
2.4 User finalize ("yes go ahead") → agent-approval-grant (2 confirmations) → hash recorded in approval-state.json
Stage 3 — PRD (bmad-prd)

3.1 Fast-path draft (FR-1…FR-6, NFR-1…NFR-4)
3.2 §5.2 PromptGateway wiring decision via AskUserQuestion ("Wire it in")
3.3 Reconciliation vs brief + addendum
3.4 Reviewer-gate (rubric)
3.5 User finalize → approval-grant
Stage 4 — Architecture (bmad-architecture, Coaching path — skipped UX)

4.1 Real dialogue before drafting (paradigm, PromptGateway boundary, fail-open placement, output-validation approach, error taxonomy — each explicitly confirmed)
4.2 Draft ARCHITECTURE-SPINE.md (AD-1…AD-6)
4.3 Reconciliation (4/4 gaps fixed)
4.4 3-reviewer gate: rubric + version-check + adversarial (2 critical + 2 high + 2 medium found, all fixed)
4.5 Round 2 re-check (approval-grant's own currency check caught AD-3 timeout math was still wrong — 20s vs true ~30s worst case) → fixed
4.6 User approve → approval-grant
Stage 5 — Project Context (bmad-generate-project-context)

5.1 Derive Do-Not-Do rules from approved spine (12 rules)
5.2 Write project-context.md (stack, source layout, data conventions)
5.3 Fix 3 stale toml persistent_facts pointing at dead pre-reset .ai-context\*.md refs
Stage 6 — Epics & Stories (bmad-create-epics-and-stories)

6.1 Extract requirements (FR/NFR inventory) from PRD
6.2 Design epics — single Epic 1 (deliberately not split)
6.3 Write 3 stories (1.1 triage adapter, 1.2 PromptGateway adapter, 1.3 endpoint+UI) with BDD ACs
6.4 Self-caught error: reverted premature FR-coverage-map fill during step 1
6.5 User approve each gate
Stage 7 — Implementation Readiness (bmad-check-implementation-readiness)

7.1 Document discovery
7.2 PRD analysis
7.3 Epic coverage validation (100% FR coverage)
7.4 UX alignment (no UX doc — assessed low-risk)
7.5 Epic quality review — found + fixed epics.md's stale scaffolding bullet; flagged 1.1/1.2 standalone-value as accepted-as-is
7.6 Final assessment → READY
Stage 8 — Sprint Planning (bmad-sprint-planning)

8.1 Parse epics → build development_status keys
8.2 Status-detect (all backlog)
8.3 Write sprint-status.yaml
Stage 9 — Create Story 1.1 (bmad-create-story)

9.1 Resolve target (epic 1, story 1) → flip epic-1 to in-progress
9.2 Load/analyze epics, architecture, project-context
9.3 Write story file (ACs, Tasks/Subtasks, Dev Notes incl. LLM-provider decision) → ready-for-dev
9.4 Sync sprint-status
Stage 10 — Dev Story 1.1 (bmad-dev-story)

10.1 Discover story, mark in-progress, stamp baseline_commit
10.2 Plan-first hard gate: write -plan.md (confidence 76 Medium), log via agent-project-logger, HALT
10.3 User approval phrase #1 → mid-flight discovery (project-context + prior app precedent contradicts SDK choice) → revise plan → HALT again
10.4 User approval phrase #2 → red (failing tests) → green (implement lib/triageService.js) → refactor
10.5 Full regression pass (11/11)
10.6 Mark tasks complete, File List, Completion Notes, Status → review
10.7 on_complete → confidence-scorer per file (88/High × 2), logged
Stage 11 — Code Review (bmad-code-review) — detailed breakdown given previously

11.1 Flag self-review-bias rule → user chose "proceed here, independent subagents"
11.2 Gather context (staged diff, spec=story file, full mode)
11.3 Launch Blind Hunter + Edge Case Hunter + Acceptance Auditor in parallel
11.4 Triage: dedupe → read code → severity → route (2 decision-needed, 7 patch, 3 defer, 1 dismiss)
11.5 Write findings to story + deferred-work.md
11.6 Resolve 2 decisions with user (CONFIG failure class; add prompt-injection delimiter)
11.7 Apply all 7 patches, add 4 new tests → 15/15
11.8 Status → done, sprint-status synced
11.9 Confidence-score the review pass itself (92/High), logged
