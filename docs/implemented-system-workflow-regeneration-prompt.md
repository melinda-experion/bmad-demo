# Prompt: Regenerate the Implemented System Workflow Diagram

Use this prompt with an agent that has read access to this repository.

```text
Act as a technical architect documenting the repository's currently implemented workflows. Create or replace `docs/implemented-system-workflow.md` with a precise, evidence-based Markdown document containing editable Mermaid diagrams.

Scope:
1. BMAD delivery workflow and every repository-local customization.
2. The root BMAD Idea Launcher runtime.
3. `PromptGateway/` runtime.
4. Explicit integration/non-integration boundaries between these surfaces.

Non-negotiable method:
- Treat checked-in code and active configuration as the source of truth. Do not present a planned artifact as implemented behavior.
- Before writing, inspect at least: `CLAUDE.md`; `_bmad/_config/bmad-help.csv`; `_bmad/bmm/config.yaml`; `_bmad/custom/*.toml`; `skills/agent-approval-gate-check/`; `skills/agent-approval-grant/`; `skills/agent-project-logger/`; `skills/experion-brief-review/`; `_bmad-output/planning-artifacts/`; `_bmad-output/bmad-idea-launcher-project-log.csv`; `server.js`; `lib/ideaService.js`; `public/`; relevant `test/`; `.ai-context*.md`; `PromptGateway/app.py`; `PromptGateway/config.py`; `PromptGateway/policy.yaml`; all `PromptGateway/validators/`; `PromptGateway/utils/audit_db.py`; `PromptGateway/Dockerfile`; `PromptGateway/docker-compose.yml`; and `PromptGateway/README.md`.
- Inspect `git status --short` first and do not overwrite unrelated user changes.
- Keep “implemented”, “configured”, “approved/planned”, “deferred”, and “not integrated” distinct. Call out gaps where a current implementation differs from approved artifacts.
- Never assume that services in the same repository call each other. Prove a runtime edge from source before drawing it.
- Do not reveal secret values from `.env`; only document configuration names and data-flow boundaries.

Required output structure:
1. Title, as-of date, scope/evidence note, and Mermaid rendering note.
2. One landscape Mermaid flowchart showing: human, BMAD control plane, approval state, output artifacts, Idea Launcher runtime, Prompt Gateway runtime, and any proven boundaries.
3. BMAD lifecycle flowchart from product brief through development/code review, including optional UX, advisory catalog ordering vs hard gates, Sentry, Warden, Ledger, Voss, status/hash invalidation, review regeneration, confidence scoring, story mirrors, dev-plan exact-phrase gate, and fresh-session code review/diff-plan reconciliation.
4. A document-lifecycle Mermaid state diagram.
5. A detailed Idea Launcher sequence diagram. Document endpoint/static routes, client validation, adapter errors, current implementation, and any documented-but-not-yet-built requirements separately.
6. A detailed Prompt Gateway Mermaid flowchart with config precedence, API validation, every validator, weighted-score composition, hard blocks, fail-open local classifier behavior, auditing, and Docker/Ollama topology.
7. A concise evidence list with paths.
8. A link to this regeneration prompt.

Mermaid requirements:
- Use valid `flowchart`, `sequenceDiagram`, and `stateDiagram-v2` syntax.
- Keep node labels concise; put detail in surrounding prose/tables.
- Use dashed edges only for optional, advisory, or explicitly non-runtime relationships and label them.
- State the exact meaning of every dashed non-integration edge in prose.

Accuracy checks before handoff:
- Confirm the current approval state file keys and gate behavior.
- Verify the actual current root server and client behavior separately from architecture/epic intentions.
- Verify the Prompt Gateway policy thresholds, hard-block categories, weights, audit behavior, and LLM fail-open setting from `policy.yaml` and code.
- Confirm whether a true runtime call connects Idea Launcher and Prompt Gateway. If none exists, say so prominently.
- Do not modify application code, policy, BMAD configuration, planning artifacts, or logs; write only the requested documentation file (and this prompt file only if it is missing/outdated).
```
