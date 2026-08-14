# Story 1.2: PromptGateway Adapter — Screening With Fail-Open

As a Triaging Agent,
I want ticket text screened for PII/secrets before it reaches the triage LLM,
So that sensitive customer information doesn't leak to an LLM call I didn't intend to risk.

**Acceptance Criteria:**

**Given** ticket text
**When** `lib/promptGatewayClient.js` calls PromptGateway (`POST /api/v1/validate`)
**Then** it returns `decision` exactly as PromptGateway reported (`ALLOW`/`FLAG`/`BLOCK`), normalized into `{decision, reason, categories_triggered}` (FR4, AD-2)

**Given** PromptGateway is unreachable or exceeds the 20s timeout
**When** the call fails
**Then** the adapter catches it internally and returns `decision: "UNREACHABLE"` with `reason`/`categories_triggered` always populated (never throws, never `null`) (NFR2, AD-3)

**Given** PromptGateway's `REQUIRE_API_KEY` is enabled
**When** the adapter calls PromptGateway
**Then** it forwards `X-API-Key` (AD-2)

**And** no new npm HTTP client dependency is added — uses Node's native `fetch` (AD-2)
