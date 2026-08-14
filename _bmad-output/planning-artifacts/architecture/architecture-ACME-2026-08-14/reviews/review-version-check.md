---
review: version-and-reality-check
target: ARCHITECTURE-SPINE.md (architecture-ACME-2026-08-14)
date: '2026-08-14'
---

# Version & Reality Check — Support Ticket Triage Spine

## Verdict

**Conditional pass.** The two explicitly-named claims (Node.js version/fetch,
PromptGateway endpoint) are accurate when checked now. But the check surfaced
one load-bearing technical claim that is asserted, not reality-checked, and
would likely fail in practice (AD-3's 8s timeout vs. PromptGateway's own
internal 15s Ollama timeout), plus a broader provenance problem: the spine's
central precedent — "the prior demo app" — does not exist as code anywhere in
this repository.

## 1. Node.js >=22, native fetch, no framework — ACCURATE, but unexamined framing

- Web-verified (Aug 2026): `fetch` has been in Node core since v18
  (experimental) and stable since v21 — no flag needed. Node 22 has it as a
  stable global. The claim is technically correct.
- However, as of Aug 2026 the supported lines are Node 26 (Current), Node 24
  (Active LTS), and **Node 22 (Maintenance LTS only, EOL 2027-04-30)**. The
  spine's `>=22` floor still works (24/26 satisfy it), but the spine presents
  22 as if it were simply "the" current baseline with no acknowledgment that
  it's now the maintenance-mode floor, not the actively-recommended line. Not
  wrong, but reads as asserted from training-data familiarity ("Node 22 has
  fetch") rather than a live check of where 22 currently sits in the support
  cycle.
- `node --test` claim is accurate and consistent with the repo's own root
  `package.json` (`"test": "node --test"`).

Sources: nodejs.org release notes, endoflife.date/nodejs, HeroDevs Node EOL post (Jul 2026).

## 2. PromptGateway integration boundary — ACCURATE against actual repo files

Verified directly against `/Users/shameersn/Projects/Poc/bmad-demo/PromptGateway/`:

- `app.py:115-121` — `POST /api/v1/validate` exists, is a real FastAPI route.
- `models/prompt_result.py:13-16` — `Decision` enum is exactly
  `ALLOW`/`FLAG`/`BLOCK`, uppercase — matches the spine's Consistency
  Conventions table verbatim.
- `models/schemas.py:45-54` — response includes `decision`, `reason`,
  `categories_triggered` fields, so AD-2's normalized-shape claim is
  achievable without invention.
- `requirements.txt` — FastAPI 0.115.0, confirming "FastAPI service" is
  accurate, not assumed.

This claim was correctly reality-checkable and holds up.

### 2a. New finding — AD-3's 8s timeout is not verified against PromptGateway's actual latency budget

AD-3 fixes an 8-second client-side timeout and cites `.claude/hooks/
prompt_gateway_check.py` as the "real precedent." That hook does pass
`--timeout 8` to `validate_prompt.py` (confirmed), so the *number* is
faithfully copied. But nothing in the spine checks whether 8s is actually
long enough for PromptGateway to finish a **normal, successful** validation:

- `PromptGateway/validators/decision_engine.py:44` awaits
  `self.llm_validator.validate(normalized)` synchronously, in-line, before
  `/api/v1/validate` returns.
- `PromptGateway/validators/llm_validator.py:41` and `PromptGateway/config.py:48`
  both default that Ollama call's own timeout to **15 seconds**
  (`ollama_timeout_seconds: float = 15.0`), with `max_retries=1` (so a slow
  Ollama could legitimately take close to 30s before LLMValidator itself
  gives up and fails open).

Net effect: a healthy PromptGateway with a merely-slow local Ollama can take
longer than 8s to answer a legitimate request. The Node adapter's 8s client
timeout would then fire first and report `unreachable`, which AD-3 defines as
"screening didn't run" — even though PromptGateway was up and mid-validation.
This isn't a new bug the spine invented; the same mismatch already exists
between the hook's `--timeout 8` and `validate_prompt.py`'s own 15s default
timeout — but the spine presents "8s, matches real precedent" as a settled,
safe fact rather than something checked against PromptGateway's actual
worst-case response time. Worth a story-level note or a bumped timeout.

### 2b. Minor gap — optional API-key auth not addressed

`PromptGateway/config.py:53-55` and `.env.example` show `/api/v1/validate` is
gated by an optional `X-API-Key` header (`REQUIRE_API_KEY`, default `false`).
AD-2 doesn't mention this at all. Harmless under current defaults, but the
adapter contract was written without checking whether auth could be required.

## 3. Broader finding — "the prior demo app" precedent is unverifiable in this repo

Both the PRD and the spine repeatedly justify structural decisions (thin
`server.js`, `lib/` adapter layout, the exact `TIMEOUT:504`/`NETWORK:502`/
`MALFORMED:500` taxonomy, the `{"error": "<message>"}` envelope, the
2000-char cap / `MAX_PROMPT_LENGTH`) as extending "the prior demo app's own
precedent." Checked against the actual repo:

- `git log --all --oneline -- server.js lib/` → no history, ever.
- `grep -rn "TIMEOUT:504\|NETWORK:502\|MALFORMED:500\|MAX_PROMPT_LENGTH"` across
  the whole tree → matches **only** inside this project's own planning
  documents (PRD, spine, prior reviews) — never in any actual source file.
- `brief-ACME-2026-08-14/brief.md` contains **zero** mentions of "prior demo
  app" — the PRD is the earliest traceable source of the phrase, and it
  offers no file reference either.

So the spine's own Design Paradigm section ("extending the prior demo app's
own precedent rather than introducing new vocabulary") rests on a precedent
that cannot be located anywhere in this codebase. This is exactly the kind of
claim that needed a repo check before being treated as settled fact, and
wasn't — every AD that cites "prior app precedent" (AD-5's error taxonomy,
the 2000-char cap, the error envelope) inherits this same unverified
foundation.

## Summary Table

| Claim | Status | Verified against |
| --- | --- | --- |
| Node.js >=22 has stable native `fetch` | Accurate | Node.js release notes, endoflife.date |
| Node 22 is a reasonable "current" baseline | Partially stale framing | Node 22 is Maintenance LTS as of Aug 2026, not Active LTS (24 is) |
| PromptGateway is in-repo FastAPI, `POST /api/v1/validate` | Accurate | `PromptGateway/app.py`, `models/schemas.py`, `models/prompt_result.py` |
| AD-3's 8s timeout is safe/matches precedent | Not fully verified — likely too short | `PromptGateway/config.py`, `validators/llm_validator.py` (15s internal default) |
| Optional PromptGateway API-key auth | Unaddressed | `PromptGateway/config.py`, `.env.example` |
| "Prior demo app" precedent exists in-repo | **Unverifiable — no such code found** | `git log --all`, whole-tree grep, brief.md |
