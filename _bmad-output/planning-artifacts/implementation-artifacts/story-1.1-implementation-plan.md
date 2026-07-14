# Implementation Plan — Story 1.1

Scope Summary

- Implement end-to-end prompt → generation flow: frontend prompt input and validation, POST /api/v1/generations API, async job queue + worker, AI integration client, persistence of generation records, status polling, and UX states (busy, success, error). Deliverables: frontend (`public/generate.js` + index.html patch), server routes/controllers/services/models/queue/worker (under `server/`), and tests (unit, integration, E2E).

Impacted Modules & Files

- Frontend: `public/index.html`, `public/app.js` or `public/generate.js`
- Backend routes/controllers/services: `server/routes/generations.js`, `server/controllers/generationController.js`, `server/services/generationService.js`
- Persistence/model: `server/models/generationModel.js`, `server/data/generations.json` (or SQLite)
- Queue & worker: `server/queues/generationQueue.js`, `server/workers/generationWorker.js`
- AI client: `server/integrations/aiClient.js` (+ `aiClient.mock.js`)
- Tests: `server/tests/unit/generationService.test.js`, `server/tests/integration/generation.api.test.js`, `test/story1.test.js` (E2E)
- Config/env: environment variables (`AI_API_KEY`, `AI_ENDPOINT`, `AI_MODEL`, `GENERATIONS_STORE_PATH`)

Detailed Design Approach

- API: POST `/api/v1/generations` accepts `{prompt, options, meta}`; returns 202 with `{id,statusUrl}`. GET `/api/v1/generations/:id/status` returns status/result.
- Flow: controller validates -> create DB record status=pending -> enqueue job -> return 202. Worker dequeues -> call AI client -> persist result status=succeeded or error status=failed. Client polls statusUrl.
- Validation: same rules client/server: trimmed length >=10 && wordCount>=2; limit prompt length (e.g., 2000 chars).
- Persistence: MVP file-backed JSON store; design DB schema to mirror fields for migration.
- AI client: adapter pattern to normalize provider responses; provide mock for tests.
- Queue: in-process queue for MVP, abstract interface to swap to Redis/RabbitMQ later.

Data Model Usage (schema impact)

- New `generations` records with fields: `id (uuid)`, `prompt (text)`, `options (json)`, `status (pending|running|succeeded|failed)`, `result (json)`, `error (json)`, `createdAt`, `startedAt`, `finishedAt`, `userId`.
- Schema impact: new storage only; migration required when moving from JSON file to SQLite/Postgres.

API / Interface Changes

- New endpoints:
  - POST `/api/v1/generations` -> create job (202)
  - GET `/api/v1/generations/:id/status` -> poll for status/result
- Client behavior: POST, then poll `statusUrl`. Ensure server registers route in `server.js`.

Error Handling & Edge Cases

- Validation failures -> 400 `{code: 'VALIDATION_ERROR', fieldErrors}`.
- AI failures -> worker sets record `status='failed'` with `error` details; status endpoint returns error object.
- Timeouts -> worker marks failed; client polling times out (configurable client-side timeout, example 60s) and offers retry.
- Rate limiting -> return 429 when exceeded.
- Storage/queue failures -> return 500 on create or mark job failed; consider compensation/rollback.

Security Considerations

- Keep AI keys in environment variables; do not commit.
- Sanitize and limit prompt length; escape output in frontend.
- Implement per-IP/user rate limiting (e.g., 1 request per 5s) to limit abuse and cost.
- Avoid logging raw prompts in production logs; mask or hash if needed.
- Consider auth for future (`meta.userId`) and CSRF protections if required.

Performance Considerations

- Use async queue to avoid blocking HTTP requests for long AI calls.
- Polling strategy: start 1s, exponential backoff up to 5s, timeout after reasonable window (e.g., 60s).
- For scale: move queue to Redis and scale workers; limit `ideaCount` and result size; consider streaming or SSE/WebSocket for push updates.

Test Strategy

- Unit tests: `generationService.validatePayload`, controller error paths, model persistence mocks, aiClient transformations.
- Integration tests: start server with `aiClient.mock`, POST valid prompt -> 202 + poll -> succeeded; test 400 validation, 429 rate-limit, failed worker flow.
- E2E tests: Playwright/Cypress scenario verifying disabled Generate for invalid prompt, busy state on submit, and results displayed on success (use mock AI in CI).
- CI: run unit+integration with mocks; run E2E in smoke mode using deterministic mocks.

Risks, Assumptions & Dependencies

- Assumptions: Node.js + Express stack (confirmed in `package.json`), static `public/` served by server. AI provider availability and billing. Frontend served same origin.
- Risks: AI provider downtime or high cost, malformed provider responses, unbounded prompt sizes causing cost, abuse by automated requests.
- Dependencies: external AI API, `node-fetch` (or built-in `fetch`), `uuid` package; optional DB library for SQLite/Postgres.

Context Files Consulted

- `_bmad-output/planning-artifacts/implementation-artifacts/story-1.1-lld.md`
- `_bmad-output/planning-artifacts/epics/epic-1-capture-and-generate-starter-ideas/story-1.1-enter-a-prompt-and-submit-a-generation-request.md`
- `package.json`

Rationale Summary

- Async job flow (202 + queue + poll) chosen to avoid blocking HTTP threads for long AI calls and to give clear busy UX and retry semantics.
- File-backed JSON for MVP to reduce infra friction; migrate to SQL for production.
- Mockable AI client ensures deterministic tests and lowers dev cost.

Key evidence 1

- LLD file specifies 202 accepted + `statusUrl` and worker queue flow (sequence diagram and API examples).

Key evidence 2

- Story acceptance criteria require visible busy state and preventing submission for invalid prompts (prompt validation and UX states).

Key evidence 3

- `package.json` indicates Node.js project, confirming implementation language and tooling.

Confidence

- High
