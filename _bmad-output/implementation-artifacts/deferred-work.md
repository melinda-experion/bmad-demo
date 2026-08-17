# Deferred Work

## Deferred from: code review of 1-1-triage-adapter-structured-output-with-validated-fallbacks (2026-08-14)

- Non-string/null/undefined `ticketText` is not validated before being interpolated into the prompt in `lib/triageService.js` — pre-existing scope boundary; empty-string rejection is Story 1.3's client-side job, and a non-string value safely stringifies via template literal rather than crashing, so this is low-urgency.
- `summary`/`draftReply` from the triage LLM are passed through with no output sanitization (control characters/HTML) before being marked `ok:true` in `lib/triageService.js` — belongs to whichever UI layer renders the text (Story 1.3's `public/app.js`), not this backend adapter.
- `lib/triageService.js` has no retry/backoff on transient failures, no distinction between rate-limit/auth errors and generic `NETWORK` failures, and no fallback if the hardcoded `claude-haiku-4-5` model ID is retired — explicitly out of v1 scope per NFR1 ("no hard latency SLA in v1") and the architecture's Deferred section (hardening not designed here).
