# BMAD Workflow: Brief → PRD (Detailed Flow)

This document maps the exact, granular sequential flow of the BMAD SDLC skills from **Product Brief** through **PRD**, as actually wired in this repo (including the Experion/org customization layer on top of the stock BMad skills). It covers every step, every user decision point, every automated gate, and every deviation/branch path.

Sources: `.claude/skills/bmad-product-brief/`, `.claude/skills/bmad-prd/`, `.claude/skills/agent-approval-gate-check/`, `.claude/skills/agent-approval-grant/`, `.claude/skills/experion-brief-review/`, `.claude/skills/agent-project-logger/`, `.claude/skills/bmad-advanced-elicitation/`, `.claude/skills/bmad-customize/`, and the resolved customization files under `_bmad/custom/*.toml`.

> **Note on personas**: Ledger = `agent-project-logger`, Sentry = `agent-approval-gate-check`, Warden = `agent-approval-grant`, Voss = `experion-brief-review`.

---

## 0. Orchestration & hand-off model

Phase order is declared in `_bmad/_config/bmad-help.csv` (read by the `bmad-help` skill):

| Skill | Phase | Preceded by | Required | Output |
|---|---|---|---|---|
| `bmad-product-brief` | `1-analysis` | — | No | product brief |
| `bmad-prd` | `2-planning` | `bmad-product-brief` | **Yes** | PRD |

`preceded-by`/`followed-by` in that catalog are **soft suggestions only**. The real, hard hand-off gate is wired entirely through the org customization layer (`_bmad/custom/bmad-prd.toml`), not through `bmad-help`. `agent-approval-gate-check`, `agent-approval-grant`, `experion-brief-review`, and `agent-project-logger` are **not** in `bmad-help.csv` at all — they are org-added cross-cutting skills invoked automatically as side effects of running Brief/PRD, not menu items a user picks directly.

Shared state file: **`_bmad/custom/approval-state.json`** — `{ "brief": {doc_path, approved_hash}, "prd": {...}, "architecture": {...} }`. This is the literal object that hands approval state from one phase to the next.

```mermaid
flowchart LR
    A["bmad-product-brief\n(phase 1-analysis)"] -- "approval-state.json\nbrief entry: approved_hash" --> G["agent-approval-gate-check\n(Sentry)"]
    G -- "result: ok" --> B["bmad-prd\n(phase 2-planning, required)"]
    G -- "result: missing / unapproved / stale / check-failed" --> X["PRD generation BLOCKED\nno bypass"]
    B -- "approval-state.json\nprd entry" --> N["bmad-ux / bmad-architecture / ...\n(out of scope)"]
```

---

## PHASE 1 — Product Brief (`bmad-product-brief`)

Files: `SKILL.md`, `customize.toml` (+ org override `_bmad/custom/bmad-product-brief.toml`), `assets/brief-template.md` (overridden by `_bmad/custom/templates/brief-template.md`), `references/confidence-scoring.md`.

### 1.1 Activation sequence

```mermaid
flowchart TD
    A1["1. Resolve customization\nresolve_customization.py\nbase → team .toml → user .toml"] -->|"script fails"| A1F["Fallback: read customize.toml directly\n(LOSES org on_complete/gate chain — silent risk)"]
    A1 -->|"script ok"| A2["2. Run activation_steps_prepend\n(org): Ledger — 'Brief generation started'"]
    A1F --> A2
    A2 --> A3["3. Load persistent_facts\nproject-context.md +\norg rule: revert approved→draft on edit"]
    A3 --> A4["4. Load external_sources registry\n(on-demand only, empty by default)"]
    A4 --> A5["5. Load config.yaml/.user.yaml\nuser_name, language, planning_artifacts, project_name, date"]
    A5 --> A6{"6. Greet user,\ndetect intent"}
    A6 -->|"interactive & ambiguous"| A6Q["Ask user: Create / Update / Validate"]
    A6 -->|"headless & ambiguous"| A6B["Halt: status=blocked, reason\n(no prompting allowed)"]
    A6Q --> A7
    A6 -->|"unambiguous"| A7["7. Run activation_steps_append\n(empty by default)"]
    A7 --> A8["8. Confirm activation complete"]
    A8 --> INT{"Intent?"}
    INT -->|Create| CREATE["Create flow"]
    INT -->|Update| UPDATE["Update flow"]
    INT -->|Validate| VALIDATE["Validate flow"]
```

### 1.2 Intent = Create → Discovery → Finalize

```mermaid
flowchart TD
    C0["Create intent confirmed"] --> D1["Discovery: surface what user brings,\nwhy brief exists, domain, form-factor"]
    D1 --> D2["Ask for source material first\n(memo/deck/transcript/prior brief)\nRead what exists; ask only what's missing"]
    D2 --> D3["'Anything else?' prompt"]
    D3 --> D4["Stakes read: hobby / internal pitch /\ninvestor / public launch"]
    D4 --> D5["Spawn parallel web-research subagents\n(parent gets digest only, not raw results)"]
    D5 --> D5B{"Exhaustive research needed?"}
    D5B -->|yes, deviation| D5H["Hand off to bmad-market-research /\nbmad-domain-research (out of this skill's scope)"]
    D5B -->|no| D6{"User decision:\nWorking mode"}
    D6 -->|"Fast path"| D6F["Batch remaining gaps into 1-2 questions;\ndraft with inline [ASSUMPTION] tags;\nuser reviews/iterates"]
    D6 -->|"Coaching path"| D6C["Walk section-by-section together;\npush back on thin assumptions"]
    D6F --> W1
    D6C --> W1
    W1["Bind workspace:\n_bmad-output/planning-artifacts/briefs/brief-{project}-{date}/\nWrite brief.md skeleton\n(approval_status: draft — org template)"] --> W2["Seed .memlog.md via memlog.py init\n(persistence checkpoint on disk)"]
    W2 --> W3["Draft brief.md\n(template = starting structure, not contract;\nsections added/dropped/reordered freely)"]
    W3 --> W4{"User volunteers downstream depth?\n(rejected alternatives, sizing data,\npersonas, constraints)"}
    W4 -->|yes| W4A["Capture live in addendum.md\n(never audit/override info)"]
    W4 -->|no| W5
    W4A --> W5["Resume support: offer resume if\nprior in-progress draft exists"]
    W5 --> FIN["Run Finalize"]
```

### 1.3 Intent = Update (branches)

```mermaid
flowchart TD
    U0["Update intent, existing brief folder\n(NOT a fresh workspace)"] --> U1["Read brief.md, addendum.md,\n.memlog.md, original inputs"]
    U1 --> U2["Re-run Discovery posture against\nthe new change signal"]
    U2 --> U3{".memlog.md exists?"}
    U3 -->|no, legacy brief| U3A["Branch: init memlog fresh\n(this update = its first entry)"]
    U3 -->|yes| U4
    U3A --> U4["Surface conflicts with prior\nlogged decisions before applying"]
    U4 --> U5{"Headless mode?"}
    U5 -->|yes| U5A["Log override via memlog.py\n(reversal + rationale), then apply"]
    U5A --> U5B{"Intent ambiguous?"}
    U5B -->|yes| U5C["Branch: halt status=blocked\n(no prompting headless)"]
    U5B -->|no| U6
    U5 -->|no| U6{"Change is fundamental,\nnot a patch?"}
    U6 -->|yes| U6A["Branch: offer Create instead\n(deviate out of Update flow)"]
    U6 -->|no| U7["Apply patch"]
    U7 --> U8{"brief.md approval_status\n== approved?"}
    U8 -->|yes| U8A["Org rule: revert to draft first/together\nwith edit; Ledger log\n'Brief updated via chat: <summary>'\n(include 'status reverted to draft')"]
    U8 -->|no| FIN["Run Finalize"]
    U8A --> FIN
```

### 1.4 Intent = Validate (standalone, no Finalize)

```mermaid
flowchart TD
    V1["Read brief, addendum, .memlog.md,\noriginal inputs"] --> V2["Honest critique against brief's\nOWN stated purpose; cite lines;\ncaveat what can't be evaluated"]
    V2 --> V3["Output returned INLINE in conversation\n(no file written unless user asks)"]
    V3 --> V4["Always offer to roll findings\ninto an Update (offer_to_update:true)"]
    V4 --> V5(["End — Finalize/on_complete NOT run"])
```

*Note: this is the authoring skill's own lightweight self-critique — distinct from the dedicated adversarial `experion-brief-review` (§4), which always runs all five fixed dimensions.*

### 1.5 Finalize (Create & Update only) → org `on_complete` approval chain

```mermaid
flowchart TD
    F1["1. Memlog audit + addendum review\n(USER CHECKPOINT: every entry ->\ncaptured in brief / addendum / set aside)"] --> F2["2. Polish: parallel subagent passes\nbmad-editorial-review-structure\nTHEN bmad-editorial-review-prose"]
    F2 --> F3["3. Confidence score\n(references/confidence-scoring.md)\nconfidence/confidence_label/confidence_rationale\ninto frontmatter"]
    F3 --> F4["4. External handoffs\n(empty by default; skip+flag if\nMCP tool unavailable)"]
    F4 --> F5["5. Tell user it's ready:\npaths + confidence; invoke bmad-help\nfor next-step suggestion"]
    F5 --> OC1["6. on_complete chain (org override):"]
    OC1 --> OC1a["Ledger: 'Brief generated'"]
    OC1a --> OC1b["Ledger: 'Confidence scored: <label>\n(<score>/100) for brief'\n(stage=brief, doc_status=draft)"]
    OC1b --> OC1c["experion-brief-review (Voss)\n→ writes review-report.md"]
    OC1c --> OC1d["Ledger: 'Brief review report generated'"]
    OC1d --> OC1e["Set approval_status = 'review', save"]
    OC1e --> OC1f["agent-approval-grant (Warden)\ndoc_type=brief"]
    OC1f --> APPROVE{"Warden's Grant-Approval flow\n(see §3)"}
    APPROVE -->|both confirmations affirmed| DONE(["approval_status = approved, version+1\ncommitted to git"])
    APPROVE -->|declined at either step| STAYS(["stays draft/review, logged, stop"])
```

**Brief lifecycle status progression:** `draft` → (Finalize on_complete) → `review` → (Warden double-confirms) → `approved` — or reverts to `draft` on any decline, on any post-approval edit, or on a Sentry staleness hit.

---

## PHASE 2 — PRD (`bmad-prd`)

Files: `SKILL.md`, `customize.toml` (+ org override `_bmad/custom/bmad-prd.toml`), `assets/prd-template.md` (overridden), `assets/prd-validation-checklist.md`, `assets/validation-report-template.html`, `assets/headless-schemas.md`, `references/confidence-scoring.md`, `references/headless.md`, `references/validate.md`.

### 2.1 Activation sequence — the hard Brief→PRD gate

```mermaid
flowchart TD
    P1["1. Resolve customization\n(base → team → user)"] -->|"fails"| P1F["Fallback to customize.toml defaults\n(LOSES gate-check/logger chain — silent risk)"]
    P1 -->|"ok"| P2A["2a. GATE: agent-approval-gate-check\ndoc_type=brief, downstream_label='PRD generation'\n(org activation_steps_prepend, step 1)"]
    P1F --> P2A
    P2A --> GATE{"Sentry result?"}
    GATE -->|"ok"| P2B["2b. Ledger: 'PRD generation started'"]
    GATE -->|"missing"| GX1(["BLOCKED: brief does not exist\n→ tell user to create it first, STOP"])
    GATE -->|"unapproved"| GX2(["BLOCKED: brief not approved\n→ tell user to approve it first, STOP"])
    GATE -->|"stale (hash mismatch)"| GX3(["BLOCKED: brief auto-reverted to draft\n→ tell user to re-approve, STOP"])
    GATE -->|"check_gate.py failed/errored"| GX4(["BLOCKED — failure treated as block,\nnever a pass (no_bypass_policy), STOP"])
    P2B --> P3["3. Load config.yaml/.user.yaml\n(missing keys → neutral defaults)"]
    P3 --> P4{"4. Headless?"}
    P4 -->|yes| P4H["Follow references/headless.md\nfor entire run (see §2.6)"]
    P4 -->|no| P4I["Greet by name/language;\nmention bmad-party-mode &\nbmad-advanced-elicitation as available"]
    P4I --> MIS{"Misroute scan on\nfirst message"}
    MIS -->|"it's a game"| MIS1(["Off-ramp: BMad GDS"])
    MIS -->|"express build"| MIS2(["Off-ramp: bmad-quick-dev"])
    MIS -->|"one-pager only"| MIS3(["Off-ramp: bmad-product-brief"])
    MIS -->|"vet an idea"| MIS4(["Off-ramp: bmad-prfaq"])
    MIS -->|"agent/skill build"| MIS5(["Off-ramp: bmad-workflow-builder"])
    MIS -->|"none — proceed"| P5{"5. Detect intent:\nCreate/Update/Validate"}
    P5 -->|"ambiguous"| P5Q["Ask user"]
    P5 -->|"Create"| P5C{"Prior in-progress PRD\nrun found (status != final)?"}
    P5C -->|yes| P5CR["Branch: offer resume\ninstead of fresh workspace"]
    P5C -->|no| P6
    P5Q --> P6["6. Run activation_steps_append (empty)"]
    P5CR --> P6
    P5 -->|"Update/Validate"| P6
    P6 --> P7["7. Confirm activation complete"]
    P7 --> INT{"Intent?"}
    INT -->|Create| PC["Create flow"]
    INT -->|Update| PU["Update flow"]
    INT -->|Validate| PV["Validate flow"]
```

### 2.2 Intent = Create → Discovery

```mermaid
flowchart TD
    PC0["Bind workspace:\n_bmad-output/planning-artifacts/prds/prd-{project}-{date}/\nWrite prd.md skeleton (approval_status: draft)"] --> PC1["Seed .memlog.md via memlog.py init"]
    PC1 --> PC2["Tell user the path"] --> DIS

    DIS["Discovery (fixed order)"] --> DIS1["1. Brain dump: verbal context +\nexisting inputs (explicitly incl.\nproduct brief, research, transcripts,\nprior PRD draft, design docs)"]
    DIS1 --> DIS2["2. Spawn web-research subagents\n(parent gets digest only)"]
    DIS2 --> DIS3{"3. LLM catches itself\nnaming wedges/MVP cuts unprompted?"}
    DIS3 -->|yes| DIS3A["Branch: STOP — hand the pen back\n(elicit, don't direct)"]
    DIS3 -->|no| DIS4
    DIS3A --> DIS4["4. Stakes calibration:\nhobby / internal / launch"]
    DIS4 --> DIS5{"5. User decision:\nWorking mode"}
    DIS5 -->|Fast path| DIS5F["Batched gaps, [ASSUMPTION]-tagged\nfull draft, user reviews"]
    DIS5 -->|Coaching path| DIS5C{"Sub-decision:\nentry point"}
    DIS5C -->|"Vision+Features\n(capability-first)"| DIS5C1
    DIS5C -->|"Journey-led\n(user-first)"| DIS5C1
    DIS5C -->|"'let me suggest'"| DIS5C1
    DIS5C1["Entry point sets section\norder for whole document"]
    DIS5F --> DIS6
    DIS5C1 --> DIS6["6. Concern scan: compliance,\nintegration, SLAs, hardware, API\ncontracts, monetization, data gov.\n(drives Adapt-In Menu clusters)"]
    DIS6 --> DIS7["7. Form-factor probe if not\nalready stated"]
    DIS7 --> DIS8{"8. Warranted?\n(consumer/B2B/meaningful UX)"}
    DIS8 -->|yes| DIS8A["User narrates named-persona\nsession → LLM structures as UJ-N,\nconfirms with user"]
    DIS8 -->|"no (internal tool,\nregulatory-only, hobby, pure tech)"| DIS8B["Downscale/drop User Journeys"]
    DIS8A --> FIN2["Run Finalize"]
    DIS8B --> FIN2
```

### 2.3 Intent = Update / Validate (PRD)

```mermaid
flowchart TD
    subgraph UPDATE["Intent = Update"]
    PU1["Reconcile PRD with change signal;\nsource-extract vs prd/addendum/memlog/inputs"] --> PU2{".memlog.md missing?"}
    PU2 -->|yes| PU2A["Branch: init fresh +\nbootstrap subagent reverse-engineers\na thin log from existing PRD"]
    PU2 -->|no| PU3
    PU2A --> PU3["Surface conflicts with prior\nlogged decisions before applying"]
    PU3 --> PU4{"approval_status\n== approved?"}
    PU4 -->|yes| PU4A["Org rule: revert to draft live,\nLedger 'PRD updated via chat: <summary>'"]
    PU4 -->|no| PUF["Run Finalize"]
    PU4A --> PUF
    end

    subgraph VALIDATE["Intent = Validate (standalone — no Finalize)"]
    PV1["Orient: source-extract vs\nmemlog/inputs/prd/addendum"] --> PV2["Run Reviewer Gate\n(mandatory rubric walker, see §2.4)"]
    PV2 --> PV3["Synthesis pipeline (mandatory,\n'do not skip')"]
    PV3 --> PV3A["Read every review-*.md;\nfill validation-report.html +\nmarkdown twin (grade: Excellent/\nGood/Fair/Poor, mechanical)"]
    PV3A --> PV4{"Headless?"}
    PV4 -->|no| PV4A["Open HTML in default browser"]
    PV4 -->|yes| PV4B["Skip browser-open"]
    PV4A --> PV5["Surface paths; ALWAYS offer\nto roll findings into Update"]
    PV4B --> PV5
    PV5 --> PV6["Re-run overwrites consolidated\nreport in place (review-*.md preserved)"]
    end
```

### 2.4 Reviewer Gate (shared by Validate and Finalize step 3)

```mermaid
flowchart TD
    RG1["Assemble menu: rubric walker\n(mandatory, 7-dim checklist) +\nfinalize_reviewers (empty by default) +\nany warranted ad-hoc reviewers"] --> RG2{"Stakes level?"}
    RG2 -->|"hobby/solo"| RG2A["May run quietly or skip"]
    RG2 -->|"higher stakes"| RG2B["User decision:\nall / subset / skip"]
    RG2A --> RG3
    RG2B --> RG3{"Subagents available?"}
    RG3 -->|yes| RG3A["Dispatch in parallel;\neach writes full review to disk,\nreturns compact summary only"]
    RG3 -->|no| RG3B["Branch: sequential fallback —\nwrite file first, then flush\nfrom working context"]
    RG3A --> RG4
    RG3B --> RG4["Surface tiered: gate verdict\n(1 sentence) → critical+high findings\nindividually → medium/low rolled up\n'plus N more in {file}'"]
    RG4 --> RG5{"Per finding,\nuser decision"}
    RG5 -->|autofix| RG5A["Apply fix"]
    RG5 -->|discuss| RG5B["Discuss"]
    RG5 -->|defer| RG5C["Add to Open Questions"]
    RG5 -->|ignore| RG5D["Ignore"]
```

### 2.5 Finalize (PRD) → org `on_complete` approval chain

```mermaid
flowchart TD
    PF1["1. Memlog audit (USER CHECKPOINT):\nevery entry -> captured in PRD /\naddendum / set aside"] --> PF2["2. Input reconciliation:\none subagent per source input vs\nprd+addendum → reconcile-{slug}.md\n(compact gap summary)\nMUST run before polish"]
    PF2 --> PF3["3. Reviewer Gate\n(§2.4) — MUST resolve before polish\n(deviation loop: findings may send\nauthor back to revise content)"]
    PF3 --> PF4["4. Triage open items:\nOpen Questions, [ASSUMPTION],\n[NOTE FOR PM]"]
    PF4 --> PF4A{"Phase-blocker?\n(would break UX/arch/epics)"}
    PF4A -->|yes| PF4B["Resolve one at a time with user"]
    PF4A -->|no| PF4C["Defer with owner + revisit\ncondition, logged via memlog"]
    PF4B --> PF4D{"High phase-blocker\ncount?"}
    PF4D -->|yes| PF4E["Branch: explicit flag to user\n(soft branch, not hard stop)"]
    PF4D -->|no| PF5
    PF4C --> PF5
    PF4E --> PF5["5. Polish: parallel across docs,\nsequential within (structure THEN prose)"]
    PF5 --> PF6["6. Confidence score →\nconfidence/label/rationale frontmatter"]
    PF6 --> PF7["7. External handoffs\n(empty by default)"]
    PF7 --> PF8["8. Close: status=final, updated=date;\nmemlog event 'PRD finalized';\nshare paths + confidence;\nname bmad-ux/bmad-architecture/\nbmad-create-epics-and-stories via bmad-help"]
    PF8 --> OC2["9. on_complete chain (org override):"]
    OC2 --> OC2a["Ledger: 'PRD generated'"]
    OC2a --> OC2b["Ledger: 'Confidence scored: <label>\n(<score>/100) for PRD'\n(stage=prd, doc_status=draft)"]
    OC2b --> OC2c["Set approval_status = 'review', save"]
    OC2c --> OC2d["agent-approval-grant (Warden)\ndoc_type=prd — NO review_skill arg\npassed (asymmetry vs. Brief chain)"]
    OC2d --> APPROVE2{"Warden's Grant-Approval flow\n(§3) — falls back to\nreview_skill_defaults.prd = bmad-prd\n(re-invokes itself, Validate intent,\nif review-rubric.md stale/missing)"}
    APPROVE2 -->|both confirmations affirmed| DONE2(["approval_status = approved,\nversion+1, committed to git"])
    APPROVE2 -->|declined| STAYS2(["stays draft/review, logged, stop"])
```

**PRD lifecycle status progression:** `draft` → (Finalize on_complete) → `review` → (Warden double-confirms, regenerating `review-rubric.md` via self-invocation if stale) → `approved` — or reverts on decline/edit/staleness, identical mechanics to the Brief.

**Structural asymmetry vs. Brief:** the Brief's `on_complete` explicitly invokes `experion-brief-review` and logs a `'Brief review report generated'` step before handing off to Warden. The PRD's `on_complete` does **not** explicitly invoke a review skill — it relies entirely on Warden's own staleness-check fallback (`review_skill_defaults.prd = "bmad-prd"`) to lazily regenerate `review-rubric.md` by calling `bmad-prd` in its own Validate intent.

### 2.6 Headless mode (either phase)

```mermaid
flowchart TD
    H1["Detected: headless:true flag /\nnon-interactive caller / no TTY /\npre-supplied automation payload"] --> H2["Never ask the user anything.\nComplete using given/discoverable inputs"]
    H2 --> H3{"Still ambiguous\nafter inference?"}
    H3 -->|yes| H3A(["Halt: status=blocked + reason\nno prompt, no greeting"])
    H3 -->|no| H4["Populate assumptions[] and\nopen_questions[] arrays"]
    H4 --> H5["Status semantics:\ncomplete = stands alone\npartial = should be reviewed\nblocked = nothing produced"]
    H5 --> H6["Validate override: always write\nboth .html and .md; always\noffer_to_update:true; skip browser-open"]
```

---

## 3. Approval Gate / Grant / Reopen subroutines

These three subroutines are shared machinery invoked by both phases (and, per `approval-state.json`, by architecture downstream).

### 3.1 `agent-approval-gate-check` (Sentry) — hard, unbypassable

```mermaid
flowchart TD
    S1["Invoked with doc_type, doc_path,\ndoc_label, downstream_label"] --> S2["Ledger: '{downstream_label} gate check\nstarted for {doc_label}'"]
    S2 --> S3["Run check_gate.py"]
    S3 --> S4{"doc_path exists?"}
    S4 -->|no| S4A(["missing → BLOCK\nLedger + tell user to create it"])
    S4 -->|yes| S5{"state[doc_type] exists AND\ndoc_path matches exactly?"}
    S5 -->|no| S5A(["unapproved → BLOCK\nLedger + tell user to approve it"])
    S5 -->|yes| S6{"SHA-256(current bytes)\n== approved_hash?"}
    S6 -->|no/null| S6A["stale → script ITSELF rewrites\nfrontmatter status back to draft\n(side effect on disk)"]
    S6A --> S6B(["BLOCK — Ledger 'modified after\napproval, reverted to draft';\ntell user to re-approve"])
    S6 -->|yes| S7(["ok → Ledger 'started - approved';\nlet caller continue"])
    S3 -->|"script errors/non-zero exit/\nunparseable output"| S8(["Treated identically to blocked —\nNEVER a pass. no_bypass_policy=true,\neven with user override request"])
```

### 3.2 `agent-approval-grant` (Warden) — double confirmation

```mermaid
flowchart TD
    G1["Invoked with doc_type, doc_path, doc_label\n(+ optional review_skill/label/filename,\nelse doc_type defaults)"] --> G2["Resolve user_name strictly from\nconfig.user.yaml → bmm/config.yaml →\nconfig.yaml → 'unknown'"]
    G2 --> G3["Ledger: '{doc_label} approval\nflow started'"]
    G3 --> G4{"git status --porcelain\non doc_path dirty?"}
    G4 -->|yes| G4A["Commit now: 'Update {doc_type}\n(draft)' BEFORE anything else\n(keeps later approval commit\nstatus-only, so revert-hook\ndoesn't undo it)"]
    G4 -->|"commit fails"| G4B(["Branch: report git error, STOP"])
    G4 -->|no| G5
    G4A --> G5{"review_skill resolves?"}
    G5 -->|no| G5A["Skip currency check;\nLedger 'skipped: no review\nskill configured'"]
    G5 -->|yes| G6{"Review artifact exists AND\n{doc_type}_version == target_version\n(current version + 1)?"}
    G6 -->|yes| G6A["Ledger: currency check passed"]
    G6 -->|"no (stale/missing)"| G6B["Invoke {review_skill} in\nValidate/standalone intent\n(never Create/Update)"]
    G6B --> G6C{"Now matches\ntarget_version?"}
    G6C -->|no| G6D(["Branch: tell user review couldn't\nbe regenerated, STOP"])
    G6C -->|yes| G7
    G5A --> G7
    G6A --> G7
    G7["1st confirmation:\n'Have you read the {review_artifact}\nand do you approve?'\n(explicit affirmative required)"]
    G7 -->|decline/ambiguous| G7A(["Stays draft; Ledger\n'declined or deferred'; STOP"])
    G7 -->|affirm| G8["2nd confirmation:\n'Confirm you've read the ENTIRE\n{doc_label} document itself'"]
    G8 -->|decline| G8A(["Stays draft; Ledger\n'declined at second confirmation'; STOP"])
    G8 -->|affirm| G9["grant_approval.py:\nstatus→approved, version+1,\nre-hash, merge into approval-state.json,\ngit commit 'Approve {doc_type} v{version}'"]
    G9 --> G10["Ledger: '{doc_label} approved\nby {user_name}'"]
    G10 --> G11{"git commit\nfailed?"}
    G11 -->|yes| G11A(["Approval still stands;\ntell user to commit manually"])
    G11 -->|no| G12(["Done — report doc_path,\napproved_hash, version"])
```

### 3.3 Reopen document (already-approved → back to draft)

```mermaid
flowchart TD
    R1["Invoked with doc_type, doc_path,\ndoc_label"] --> R2["Ledger: '{doc_label} reopen\nflow started'"]
    R2 --> R3["Single confirmation, consequence stated:\n'Reopening will put it back in draft;\nit must be re-approved before anything\ndownstream can build on it. Proceed?'"]
    R3 -->|decline| R3A(["Leave doc + state untouched;\nLedger 'reopen declined'; STOP"])
    R3 -->|affirm| R4["reopen_document.py:\nstatus → draft"]
    R4 --> R5["If a matching approval-state entry\nexists: add superseded:true IN PLACE\n(never deleted — kept as audit record)"]
    R5 --> R6(["Ledger: '{doc_label} reopened for\nreview by {user_name}'; report result"])
```

---

## 4. `experion-brief-review` (Voss) — adversarial review

Runs **always all five fixed dimensions**, every run, regardless of how clean the brief looks:

1. Problem statement clarity
2. Defensibility of stated goals
3. Hidden/unstated assumptions
4. Scope-creep risk
5. Gaps in target-user definition

Each finding cites a line/section (or its absence) and carries severity `critical` / `moderate` / `minor`. A clean dimension is explicitly marked "clean" — never silently skipped.

```mermaid
flowchart TD
    B1["Invoked (3 possible triggers)"] --> T1["1. Automatically from brief's\nFinalize on_complete (every brief run)"]
    B1 --> T2["2. Automatically from Warden's\nstaleness check before brief approval"]
    B1 --> T3["3. Directly, ad hoc, any time\n('talk to Voss') — not gated to once"]
    T1 --> V1["Review all 5 dimensions"]
    T2 --> V1
    T3 --> V1
    V1 --> V2["Write review-report.md\n(overwritten each re-review, not\none-per-run); frontmatter\nbrief_version = current+1"]
    V2 --> V3["git commit 'Review brief v{target}'"]
    V3 -->|"commit fails"| V3A(["Report git error —\ndoes NOT undo the write"])
    V3 --> V4["Ledger logs start + completion"]
    V4 --> V5(["Never edits brief, never touches\nstatus, never implies approval —\napproval is a separate human act"])
```

**Mandatory in practice** for brief→approval: hard-wired into both `bmad-product-brief`'s `on_complete` and Warden's staleness-fallback for `doc_type=brief`. Not listed in `bmad-help.csv`, so it's invisible to a user browsing that catalog — it only surfaces as an automatic side effect.

---

## 5. `bmad-advanced-elicitation` — optional deeper-critique loop

Entirely **optional, user-triggered**. Both `bmad-product-brief` and `bmad-prd` merely mention it's available during their opening greeting; neither invokes it automatically at any fixed step.

```mermaid
flowchart TD
    E1["User explicitly asks for deeper\ncritique or names a method\n(Socratic, first-principles,\npre-mortem, red-team)"] --> E2["Load methods.csv;\npresent 5 candidate methods +\n[r]eshuffle / [a]ll / [x]proceed"]
    E2 --> E3["User picks method"]
    E3 --> E4["Apply to current section content;\nshow enhanced version"]
    E4 --> E5{"User: apply?\n(y/n/other)"}
    E5 -->|yes| E6["Re-present menu for\nfurther iteration"]
    E5 -->|no/other| E6
    E6 --> E7{"x = proceed?"}
    E7 -->|no| E3
    E7 -->|yes| E8(["Return enhanced content to\ninvoking skill/section; signal complete"])
```

---

## 6. Customization layer (`bmad-customize`) — what's actually overridden here

`bmad-customize` is a meta-skill that authors TOML overrides under `_bmad/custom/` for any skill's exposed `[workflow]`/`[agent]` surface. It does not itself customize Brief/PRD — it is the tool used to *create* the overrides below, which already exist and materially change the stock flow:

| Override file | Effect |
|---|---|
| `_bmad/custom/bmad-product-brief.toml` | Org `brief-template.md` (frontmatter uses `approval_status`, not `status`); appends live "revert approved→draft on edit" fact; appends Ledger call to `activation_steps_prepend`; **replaces** `on_complete` with the 6-step review→approval chain (§1.5). |
| `_bmad/custom/bmad-prd.toml` | Org `prd-template.md` + org validation checklist; same live revert-on-edit fact; **replaces** `activation_steps_prepend` with the Sentry gate + Ledger start-log (the literal Brief→PRD hard gate — not present in stock defaults); **replaces** `on_complete` with the 4-step chain (no explicit review-skill call, relies on Warden fallback). |
| `_bmad/custom/agent-approval-gate-check.toml` | `status_field = "approval_status"` (overrides stock `"status"`). |
| `_bmad/custom/agent-approval-grant.toml` | `status_field = "approval_status"`; adds `review_skill_defaults` / `review_artifact_label_defaults` / `review_artifact_filename_defaults` tables per `doc_type` — entirely org-added, not in stock `customize.toml`. |
| `_bmad/custom/approval-state.json` | Live data (not a template) — shared hand-off state across brief/prd/architecture. |

**`.agents/skills/` vs `.claude/skills/` divergence:** `bmad-product-brief` and `bmad-prd` themselves are byte-identical across both trees. The real divergence is that `.agents/skills/` is **missing six skill directories entirely** that exist under `.claude/skills/`: `agent-approval-gate-check`, `agent-approval-grant`, `agent-project-logger`, `confidence-scorer`, `experion-brief-review`, `prompt-gateway-guard`. Any harness that resolves skills from `.agents/skills/` would run Brief/PRD's own logic identically, but every gate-check, approval-grant/reopen, adversarial review, and logging step referenced by the org `on_complete`/`activation_steps_prepend` chains would have no skill to resolve to.

---

## 7. Status-field lifecycle (org-customized reality)

| Stage | `approval_status` | Set by | Trigger |
|---|---|---|---|
| Workspace bound (Create intent) | `draft` | authoring skill | workspace bind |
| Content edited after approval, mid-conversation | `draft` (reverted) | authoring skill, live | org persistent_fact |
| Finalize `on_complete` completes | `review` | authoring skill's on_complete | after Voss (brief) / lazily via Warden fallback (PRD) |
| Gate check finds stale hash | `draft` (reverted) | `check_gate.py` itself | Sentry invocation |
| Both Warden confirmations affirmed | `approved`, version +1 | `grant_approval.py` | Warden |
| User reopens an approved doc | `draft`, state entry flagged `superseded:true` (kept) | `reopen_document.py` | Warden (Reopen) |

## 8. Exact Brief → PRD hand-off condition

PRD generation cannot begin Discovery/drafting until `_bmad/custom/bmad-prd.toml`'s `activation_steps_prepend` step 1 (Sentry, `doc_type='brief'`) returns `{"result":"ok"}`, requiring **all** of:

1. `_bmad/custom/approval-state.json` has a `brief` entry.
2. That entry's `doc_path` resolves to the exact same absolute path as the brief being handed to the PRD skill.
3. A fresh SHA-256 of that brief file's current bytes equals the recorded `approved_hash`.

Any mismatch reverts the brief to `draft` (if stale) and hard-blocks PRD generation — `no_bypass_policy = true`, no exceptions, even on script failure.
