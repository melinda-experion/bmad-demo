# Story 1.1: Triage Adapter — Structured Output With Validated Fallbacks

As a Triaging Agent,
I want the system to turn my raw ticket text into a validated Category, Priority, Summary, and Draft Reply,
So that I never see a broken or out-of-scope value in a triage result.

**Acceptance Criteria:**

**Given** ticket text describing a billing issue
**When** `lib/triageService.js` processes it
**Then** it returns `category="billing"` (one of the 5-value enum), a `priority` from the 3-value enum, a one-sentence summary, and a non-empty draft reply (FR2)

**Given** ticket text that doesn't clearly match bug/billing/feature-request/question
**When** processed
**Then** `category` resolves to `"other"` without erroring (FR3)

**Given** a triage LLM response that isn't valid structured data (invalid JSON, or a missing/wrong-typed key)
**When** processed
**Then** the adapter reports a `MALFORMED`-class failure rather than guessing a value (AD-4)

**Given** a triage LLM response with a `category` or `priority` value outside its enum (right type, wrong value)
**When** processed
**Then** they resolve to `other`/`medium` respectively — never the raw out-of-enum value (AD-4)

**And** two calls with identical input each invoke the LLM — no caching or memoization (NFR1)
