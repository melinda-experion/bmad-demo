# Review: Version / Currency Check — ARCHITECTURE-SPINE.md

**Reviewed:** 2026-07-29
**Scope:** Stack table version/LTS claims (Node.js) and the deferred Anthropic Claude LLM provider assumption, checked against live web sources rather than training-data recall.

## Verdict

One factual error was found and confirmed via web search — the spine's claim that Node.js 22 is "Maintenance LTS through Apr 2028" is wrong (that date belongs to Node.js 24; Node.js 22 actually exits maintenance/EOLs April 30, 2027) — while the Node 24 and Anthropic Claude claims check out as accurate and current.

## Findings

### 🔴 High — Node.js 22 EOL date is wrong (off by one release line)

The Stack table states:

> Node.js `>=22` (local dev on `v22.15.0`, **Maintenance LTS through Apr 2028**; Node 24 recommended for a fresh setup — Active LTS as of 2026-07)

Per Node.js's official release schedule (confirmed via multiple independent sources as of 2026-07-29):

- **Node.js 22 ("Jod")**: Active LTS start 2024-10-29 → Maintenance LTS start **2025-10-21** → **End-of-life 2027-04-30**.
- **Node.js 24 ("Krypton")**: Active LTS start 2025-10-28 → Maintenance start 2026-10-20 → **End-of-life 2028-04-30**.

The spine has attached Node 24's EOL date (Apr 2028) to Node 22. Node 22's actual maintenance window ends **April 2027**, a full year earlier than stated. This reads as a copy/transposition error — the "Apr 2028" figure is real, but it belongs to the *other* model mentioned two words later in the same sentence, not to Node 22.

**Why it matters:** the whole point of citing an EOL date in an architecture spine is to bound how long the "local dev" runtime choice remains supportably current. Overstating it by a year could lead a team to treat Node 22 as safe to keep as the floor for longer than it actually is. Given the PRD/architecture's own text already flags Node 24 as "Active LTS ... recommended for a fresh setup," the spine's own internal signal (prefer 24) is right, but the stated justification for tolerating 22 (long remaining maintenance runway) is inflated.

**Recommended fix:** change "Maintenance LTS through Apr 2028" to "Maintenance LTS through Apr 2027" for Node 22, or drop the specific date and just say "Maintenance LTS (EOL 2027-04-30)."

Sources:
- Node.js official release schedule / endoflife.date aggregation — Node 22 Maintenance start 2025-10-21, EOL 2027-04-30; Node 24 Active LTS, EOL 2028-04-30.
- Corroborated by independent third-party summaries (PocketLantern, PkgPulse, HeroDevs, endoflife.date) all agreeing on 2027-04-30 for Node 22 and 2028-04-30 for Node 24.

### 🟢 Low / Informational — Node 24 "Active LTS as of 2026-07" claim is accurate

Confirmed: Node.js 24 entered Active LTS on 2025-10-28 and remains Active LTS through 2026-10-20 (when it moves to Maintenance), so "Active LTS as of 2026-07" is correct for the stated current date (2026-07-29). No change needed.

### 🟢 Low / Informational — "Node.js >=22" as a floor, CommonJS, `node --test`, no web framework

These are project-convention decisions (matching the existing `server.js`), not claims about the external world that need web verification — nothing to flag. They don't depend on Node.js's own release-support timeline being right, only on the runtime existing and supporting `node --test` and core `http`, which it does on both 22 and 24.

### 🟢 Low / Informational — "Anthropic Claude" as illustrative, swappable default LLM provider is a reasonable, currently-existing choice

Checked against a live, actively maintained internal catalog of current Anthropic models and API surface (cached 2026-06-24, i.e. current relative to the 2026-07-29 architecture date). Anthropic Claude is a real, actively developed, first-party API product line as of the review date — current models include Claude Opus 5, Claude Sonnet 5, and Claude Fable 5, with mature SDKs (Python, TypeScript, Java, Go, Ruby, C#, PHP), the standard Messages API, and well-documented auth (API key or `ant auth login`). Since the spine already treats this as an `[ASSUMPTION]` naming a swappable default behind AD-2's provider-adapter boundary (not a locked-in dependency), and doesn't cite a specific model ID, pricing, or API shape that could go stale, there is nothing here that needed deeper verification — it remains a safe, low-commitment placeholder. No change needed.

## Summary of what was NOT independently re-verified

- The observed local dev version `v22.15.0` — this is asserted as an observation of the actual local environment, not a general claim about the world, so it isn't something web search can confirm or deny; it was left as-is.
- No other library/framework versions are named in the spine (no web framework, no other dependencies pinned), so there was nothing else in the Stack table to check.
