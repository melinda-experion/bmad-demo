---
title: BMAD Idea Launcher v2 — Favoriting & Real LLM Backend
approval_status: review
created: 2026-07-30
updated: 2026-07-30
confidence: 55
confidence_label: Medium
confidence_rationale: The FR content itself (LLM backend, favoriting) is well-grounded in the approved gap brief and user-confirmed scope decisions. But confidence is capped at Medium by one deliberately unresolved, high-impact item — whether this entire PRD duplicates already-approved architecture/epics artifacts not available on disk (Open Question 1, explicitly deferred rather than checked) — plus 3 remaining [ASSUMPTION] tags and 5 Open Questions overall.
---

# PRD: BMAD Idea Launcher v2 — Favoriting & Real LLM Backend

## 1. Document Purpose

**`[NOTE, highest-priority]` This PRD may be redundant with already-approved work.** v1's PRD, the project's architecture spine, and its epics appear to already specify requirements adjacent to this scope (FR-2, FR-4, AD-1 through AD-6, Stories 1.1/1.2/1.3) — those artifacts were not available on disk at the time of this PRD's drafting. Before this PRD is treated as authoritative, that overlap must be checked (see Open Question 1); it is not resolved here.

This PRD scopes two specific gaps surfaced by the implementation-status brief (`brief-BMAD-2026-07-30`, approved v1): favoriting (not implemented) and the real LLM-backed Idea Generation Service (currently a hardcoded stub). Both gap findings carry the brief's own evidentiary caveats forward — see §3.1 and §3.2 — rather than restating them as settled fact. It does not restate v1's PRD (`prd-BMAD-2026-07-27`) in full — v1 remains the source of truth for everything already shipped (prompt input, three-card rendering, the `Clear` button). This document exists to carry the two open gaps to implementation-ready requirements.

## 2. Scope

### 2.1 In Scope

- **Real LLM-backed Idea Generation Service**: replace the hardcoded stub in the idea-generation backend with a genuine call to an LLM provider.
- **Favoriting**: a single-select favorite toggle on idea cards, matching v1's original FR-4 intent (highlighted state, resets on new generation, session-only — no persistence).

### 2.2 Out of Scope

- PromptGateway integration (routing generated prompts through the policy-check service on this branch) — left as an explicit open question, not committed here.
- Saving the favorite in `localStorage` — stays deferred, per user decision during this PRD's discovery.
- Any other v1-deferred or vision item (categories, workflow helper, export) not named above.

## 3. Features

### 3.1 Real LLM-Backed Idea Generation

**Description:** The idea-generation backend calls a genuine LLM provider instead of returning template-string stub ideas, while preserving the existing request/response contract (prompt in, exactly 3 `{title, description}` ideas out). `[ASSUMPTION: the brief's finding that the backend is a hardcoded stub was based on a working-tree read, not explicitly cross-checked against the last commit — treated as current here, but not independently re-verified for this PRD.]`

#### FR-1: LLM provider call

Given a non-empty prompt, the backend calls a configured LLM provider and returns exactly 3 ideas for rendering, replacing today's hardcoded stub.

**Consequences (testable):**

- A successful call returns exactly 3 well-formed `{title, description}` entries; the service never pads, truncates, or fabricates entries to force conformance to "exactly 3" — a malformed provider response is an error, not a repaired one.
- Two separate calls with the identical prompt each independently reach the provider — no caching or memoization of responses by prompt text (carries forward v1's SM-C1 counter-metric intent).
- The response contract (`{ ideas: [...] }`) is unchanged from what the client already consumes — no client-side changes required for this FR.

**Feature-specific NFRs:**

- The LLM API key is read only from a server-side environment variable and never appears in any client-served response or asset. `[ASSUMPTION: env var name and exact provider/model are an implementation decision, not fixed by this PRD — see Open Questions.]`
- A provider call that fails or times out surfaces an inline error to the user with the typed prompt preserved for retry, consistent with v1's FR-2 error-handling intent.

**Out of Scope:**

- Retry-with-backoff or queuing beyond a single user-initiated retry (unchanged from v1).
- Naming or requiring a specific LLM provider — this PRD is provider-agnostic by user decision.

### 3.2 Favoriting

**Description:** Each idea card gets a favorite toggle. Exactly one card can be favorited at a time; selecting a new favorite clears any previous one. State is session-only. `[ASSUMPTION: the brief's "not implemented" verdict for favoriting rests on the absence of favorite-related markup/handlers in the audited files — evidence of absence, not proof; this PRD treats it as accurate but that residual uncertainty isn't independently re-verified here.]`

#### FR-2: Favorite an idea card

User can toggle a favorite state on any one idea card, with a clearly highlighted visual state when active.

**Consequences (testable):**

- Clicking the favorite toggle on a card visibly changes its highlighted state (visually distinct border/background, not conveyed by color alone).
- Favoriting a second card automatically un-favorites whatever was previously favorited — at most one favorited card at any time.
- Favorite state resets on a new `Generate ideas` click and is not persisted across page reloads (session-only, no `localStorage`, by user decision during this PRD's discovery).

## 4. Success Metrics

**Primary**

- **SM-1**: A `Generate ideas` click with the real LLM backend still renders three cards within 30 seconds under normal network conditions — v1's original target, carried forward as-is pending resolution of Open Question 4 (whether a real provider call needs a looser bound).
- **SM-2**: A user can favorite exactly one card and see it clearly distinguished from the other two.

**Counter-metrics (do not optimize)**

- **SM-C1** (from v1, still binding here): don't cache or reuse LLM responses across different prompts to improve perceived speed — every prompt gets a genuinely fresh generation call.

## 5. Open Questions

1. **Reconciliation with pre-existing planning artifacts.** This session found evidence of an already-approved architecture spine and epics document scoping this same work (Stories 1.1/1.2/1.3), which were not present on disk when this PRD was drafted. This should be resolved before anything else on this list (see the highest-priority note in §1) — if those artifacts are current and authoritative, this PRD may be redundant with (or need to defer to) them rather than standing alone.
2. **Story doc currency.** Is the existing implementation-artifact story doc (`1-1-real-llm-backed-idea-generation.md`), currently marked in-progress with all tasks unchecked, still accurate — or has it stalled or been superseded? (Carried forward from the brief's own Open Question 1, not yet resolved by this PRD.)
3. **Provider/model choice.** This PRD deliberately stays provider-agnostic; which LLM provider and model actually gets called, and what the exact environment-variable name is, is left to implementation. `[NOTE: that same story doc already assumes Anthropic Claude and an `IDEA_LLM_API_KEY` env var, and flags that a specific model ID could not be reliably confirmed — worth reconciling with that doc before implementation starts, rather than this PRD and that story silently diverging.]`
4. **Timeout target.** Does v1's 30-second render target still hold once a real (non-stub) LLM call is in the path, or does this PRD need its own, looser target?
5. **PromptGateway.** Should the LLM call route through the PromptGateway service that already exists on this branch? Explicitly out of scope for this PRD, but unresolved.

## 6. Assumptions Index

- §1 — Assumed prior architecture/epics artifacts referenced by an existing story doc were unavailable rather than intentionally superseded; flagged as Open Question 1 rather than resolved.
- §3.1 FR-1 NFR — Provider/model and env-var naming left unspecified, by explicit user decision to keep this PRD provider-agnostic.
- §3.2 FR-2 — Favoriting kept session-only (no `localStorage`), by explicit user decision during this PRD's discovery.
