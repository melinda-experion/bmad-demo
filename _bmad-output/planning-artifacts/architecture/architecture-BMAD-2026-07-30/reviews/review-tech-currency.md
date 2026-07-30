---
name: 'Tech Currency Review — BMAD Idea Launcher v2 Architecture Spine'
type: review
target: architecture-BMAD-2026-07-30/ARCHITECTURE-SPINE.md
date: '2026-07-30'
---

# Tech Currency Review

## Method

Web-searched current Node.js release/LTS schedule, `node --test` maturity/adoption, and CommonJS-vs-ESM guidance as of mid-2026, and checked each against the spine's Stack table and stated rationale (rather than relying on training-data recall).

## Findings

### Node.js `>=22` — STALE, flag

As of July 2026: Node 24 is Active LTS (through April 2028), Node 22 is now in Maintenance LTS (through April 2027), and Node 26 is the Current release (becomes Active LTS October 2026). A floor of `>=22` is not incorrect (22 is still supported until April 2027) but is no longer the currently-recommended baseline for a new small app starting today — it pins to a line that's already past Active LTS and exits support before a typical app's lifetime. `>=24` would be the current reasonable floor. This isn't asserted as "confirmed current" in the spine (no citation either way), so it reads as a training-data-era default that wasn't reality-checked against 2026's actual LTS calendar.
Sources: [nodejs.org release schedule blog](https://nodejs.org/en/blog/announcements/evolving-the-nodejs-release-schedule), [Node.js Release WG](https://github.com/nodejs/Release), [PkgPulse Node 22 vs 24 guide](https://www.pkgpulse.com/guides/nodejs-22-vs-nodejs-24-2026)

### `node --test` as test runner — OK, current best practice for this scope

Confirmed still current and appropriate: the built-in runner is mature, zero-dependency, and explicitly recommended for small libraries/CLIs/simple apps in 2026 (roughly 40%+ adoption share, ~50M weekly downloads). The spine's choice fits a single-screen, no-framework app exactly the way sources describe as the runner's sweet spot. No stale assumption here.
Sources: [HireNodeJS native test runner 2026](https://www.hirenodejs.com/blog/nodejs-native-test-runner-2026), [PkgPulse node:test vs Vitest vs Jest 2026](https://www.pkgpulse.com/guides/node-test-vs-vitest-vs-jest-native-test-runner-2026)

### CommonJS module system — not stale, but rationale should be named explicitly

Current 2026 guidance has shifted: the ecosystem and Node core team now recommend ESM as the default for *new* projects (Node 22 also closed the `require(esm)` interop gap). CommonJS is not deprecated or broken, but it is no longer "the current best-practice default" in the abstract. The spine is not vulnerable here because its stated rationale is explicitly "matching `server.js` as it exists today" — i.e., ratified from existing code, not asserted as a 2026 best-practice pick. That's the correct posture; no fix needed, but worth noting for the record so a future reader doesn't mistake AD's silence for an implicit "CJS is current best practice" claim.
Sources: [jsmanifest ESM/CJS migration guide 2026](https://jsmanifest.com/nodejs-esm-commonjs-migration-2026), [ResumeLens CJS vs ESM 2026](https://www.resumelens.org/blog/nodejs/nodejs-modules-cjs-vs-esm)

### No web framework (AD-1) / no other named libraries

Confirmed: the Stack table lists exactly Node.js, module system, test runner, and "none" for web framework — nothing else is pinned that requires a version check. AD-1 deliberately avoids naming Express/Fastify/etc., so there is no additional library/framework claim to verify.

## Verdict

One stale-but-not-flagged-as-such assumption: **Node.js `>=22`** should be reconsidered against the current 2026 LTS calendar (Node 24 is Active LTS; 22 is Maintenance-only). No other technology claim in the Stack table was asserted as "current" without basis — the test runner choice holds up, and the CommonJS choice is honestly scoped as "match existing code," not a best-practice claim.

## Recommendation

Bump the Stack table's Node.js floor from `>=22` to `>=24` (or explicitly note `>=22` is a deliberate compatibility floor with the existing `server.js`, if that's the actual intent) so the spine doesn't read as asserting 22 is the current recommended baseline.
