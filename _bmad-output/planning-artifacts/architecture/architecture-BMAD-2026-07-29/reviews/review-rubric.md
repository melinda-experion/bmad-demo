---
title: Good-Spine Checklist Review — BMAD Idea Launcher Architecture Spine
reviewed_document: ../ARCHITECTURE-SPINE.md
reviewed_against: [PRD (prd-BMAD-2026-07-27), server.js, package.json]
created: 2026-07-29
reviewer: Claude (rubric review)
---

# Review: ARCHITECTURE-SPINE.md (BMAD Idea Launcher)

## Verdict

Sound and appropriately lean for a 1-2 hour MVP — its five ADs correctly fix the real client/server and state-ownership divergence points and faithfully ratify `server.js` — but it is silent on two dimensions (request timeout / 30s-target enforcement, and deployment/environment setup) that a feature-altitude spine should at minimum explicitly defer rather than leave unaddressed.

## Findings

### High

- **Deployment/environment/operations dimension is silent, not deferred.** The spine has no mention of how the app is run/hosted (local-only? a `Procfile`/`Dockerfile`? none exist in the repo aside from the unrelated `PromptGateway/Dockerfile`), how the required LLM API key env var is named or supplied for a local build (no `.env.example`, no documented variable name, e.g. `ANTHROPIC_API_KEY`), or whether any CI exists (`.github/` contains only BMAD agent defs, no workflow). The Stack and Deferred sections cover language/runtime/test-runner/rate-limiting/provider choice but never touch this dimension at all. Per the review brief, for a tiny learning-project MVP "not applicable, deploy is out of scope" is an acceptable one-line deferred note — silence is not. This should be an explicit line in Deferred (or a short "Environment & Config" convention row) naming the env var and stating deploy/CI are out of scope.

### Medium

- **The 30-second generation-time target (PRD SM-1/FR-2) is never operationalized into an enforceable Rule.** AD-5 binds "FR-2 (30s target...)" in its header but its actual Rule only fixes request/response *shape*, not a timeout value or behavior. Nothing tells a builder what timeout to set on the server→LLM call, or what happens if the LLM call itself is slow but not yet failed (does the server give up at some bound and return 5xx, or wait indefinitely?). Two implementations of AD-2's adapter could reasonably diverge here (one with no timeout, one with an aggressive one), which is exactly the kind of story-level divergence a spine should close. Recommend adding a concrete timeout figure (e.g., server-side timeout at ~25s, returning 5xx) to AD-5 or AD-2.
- **No env var name is fixed anywhere for the API key**, only "read from `process.env`" (AD-2) and "via environment variables" (Consistency Conventions). Combined with the LLM provider choice being correctly left open (Deferred), a builder has zero named contract to code against and no `.env.example` to follow. Low risk of *incompatible* divergence given this is a single-builder project, but it is a real gap in "build substrate" completeness — a builder has to invent the variable name from scratch.

### Low

- **`package.json` has no `engines` field**, so the Stack table's "Node.js `>=22`" requirement (AD-adjacent, under Stack) is descriptive only — nothing in the repo enforces or even signals it to a builder running `npm install`. Not a correctness bug for a solo 1-2 hour build, but worth a one-line `engines` addition if the spine wants this to be more than aspirational.
- **No production dependency is declared for the LLM call** (package.json has zero `dependencies`, only `devDependencies: husky`). This is consistent with the Deferred provider choice and isn't a spine defect per se, but the spine could note (even in Deferred) that adding an SDK or using plain `fetch`/`https` is the builder's call, so it's clear this isn't an oversight.

## Praiseworthy — do not change

- **AD-1 through AD-5 are each genuinely enforceable and each map to a real, stated divergence risk** (framework creep, API-key leakage, accidental server-side persistence, single- vs multi-select favorite ambiguity, response-shape drift). This is the core job of a spine and it is done well and concisely — five ADs is the right size for this scope, not more.
- **The spine correctly ratifies rather than contradicts `server.js` and `package.json`.** AD-1 (`http` core module, no framework), the CommonJS module system, `node --test` as the test runner, and the exact static-file set (`index.html`, `styles.css`, `app.js`) all match the current code precisely. The Design Paradigm section's `[ADOPTED]` tag is honest about what's inherited vs. new.
- **AD-5's fixed contract genuinely closes off a real two-builder divergence risk**: without it, one implementation might return a bare array vs. a wrapped object, or use inconsistent error-shape between the 400 and 5xx paths. Tying it to the current stub's behavior (which already returns `400`/`{ideas:...}` in the matching shapes) is a good ratification move.
- **Deferred section is scoped correctly for everything it does cover.** LLM provider choice, `localStorage`/Clear-button/help-note extras, and rate limiting are all genuinely safe to leave open because AD-2's adapter boundary and AD-5's fixed contract mean none of them can cause two independently-built pieces to become incompatible — the reasoning given for each is explicit and correct, not hand-waved.
- **The explicit call-out that `PromptGateway/` (the in-repo FastAPI service) is out of scope and unrelated to this app's runtime** is a genuinely useful, non-obvious warning given the two live side-by-side in the same repo — a builder skimming the repo tree could easily have wired it in by mistake. Good instinct to name and dismiss it explicitly rather than leaving it as an unaddressed ambiguity.
- **The Mermaid flow diagram matches the ADs and the actual code path exactly** (browser → handler → adapter → LLM, plus the static-GET branch) — no drift between prose rules and diagram.
