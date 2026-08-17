---
project_name: 'Support Ticket Triage'
user_name: 'Mel'
date: '2026-08-14'
sections_completed: ['technology_stack', 'source_layout', 'data_conventions', 'anti_patterns']
status: 'complete'
rule_count: 12
optimized_for_llm: true
existing_patterns_found: 0
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- Node.js >=22 — core `http` module + native `fetch` only, no framework
- PromptGateway — sibling FastAPI service, `POST /api/v1/validate` (not a Node dependency, a separate process reached over HTTP)
- `node --test` — built-in runner, no other test framework
- No npm dependencies beyond `husky` (dev-only, git hooks)

## Critical Implementation Rules

_Sourced from the approved architecture spine's ADs
(`_bmad-output/planning-artifacts/architecture/architecture-ACME-2026-08-14/ARCHITECTURE-SPINE.md`,
v1) — no code exists yet to scan for patterns._

### Source Layout

- `server.js` — HTTP layer only: routing + orchestration, no external-call logic.
- `lib/promptGatewayClient.js` — sole caller of PromptGateway.
- `lib/triageService.js` — sole caller of the triage LLM.
- `public/` — client (text area, submit, result area).
- `test/` — `node --test` specs.

### Data Conventions

- `Category` ∈ `bug` | `billing` | `feature-request` | `question` | `other` (lowercase, hyphenated where multi-word).
- `Priority` ∈ `low` | `medium` | `high` (lowercase).
- `Screening Decision` ∈ `ALLOW` | `FLAG` | `BLOCK` | `UNREACHABLE` (uppercase — the first three match PromptGateway's own contract verbatim; `UNREACHABLE` is this app's own addition, never returned by PromptGateway itself, never re-cased).
- Error envelope: `{"error": "<message>"}`.
- Success envelope: `{"category", "priority", "summary", "draftReply", "screeningWarning"}` — `screeningWarning` is `null` on `ALLOW`, a message string on `FLAG`/`UNREACHABLE`.

### Global Do-Not-Do Rules (Always Enforced)

- Do NOT introduce a web framework (Express, Fastify, etc.) — Node core `http` only (AD-1).
- Do NOT add a database, session store, or any server-side persistence — all state is client-side, session-only (AD-6).
- Do NOT cache or memoize the triage LLM call — every submission that passes screening is a genuinely fresh call (AD-6).
- Do NOT let `server.js` call PromptGateway or the triage LLM directly — only through their respective adapters, and adapters never call each other (AD-1, AD-2).
- Do NOT let `lib/promptGatewayClient.js` throw on unreachable/timeout — it must catch internally and return `decision: "UNREACHABLE"` (AD-3).
- Do NOT treat an `UNREACHABLE` screening result as silent `ALLOW` — it's surfaced like `FLAG`, with a visible warning (AD-3).
- Do NOT let raw LLM text reach the response as `Category`/`Priority` — validate against the fixed enums first (AD-4).
- Do NOT skip the "parses as structured data" schema check (valid JSON + `category`/`priority`/`summary`/`draftReply` keys, all strings) before applying fallback logic — a response that fails this check is `MALFORMED:500`, not a soft default; only a same-type-wrong-value case gets the `other`/`medium` fallback (AD-4).
- Do NOT invent a new error-shape convention — extend AD-5's taxonomy (`TIMEOUT:504` / `NETWORK:502` / `MALFORMED:500` / `400` for over-length input / `403` for `BLOCK`).
- Do NOT pick a triage LLM provider or add its SDK without flagging it first — the provider is explicitly undecided (spine Deferred; PRD is deliberately provider-agnostic).
- Do NOT architect deployment/CI/infra — explicitly deferred (spine Deferred, matches prior app precedent).
- Do NOT add an npm HTTP client dependency for either external call — Node's native `fetch` covers both (AD-2).
- Do NOT modify files outside the current story's approved plan scope.

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option.
- Update this file if new patterns emerge.

**For Humans:**

- Keep this file lean and focused on agent needs.
- Update when the architecture spine changes (new/amended ADs).
- Remove rules that become obvious once real code exists.

Last Updated: 2026-08-14
