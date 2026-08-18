## LLM Wiki

This project maintains an LLM-curated wiki at `wiki/` following Andrej Karpathy's "LLM Wiki" pattern, capturing project knowledge (decisions, architecture, bugs, lessons, people, workflows) — not the code itself, which is derivable from git.

Before answering questions that rely on knowledge accumulated in this project, read `wiki/index.md` and use its one-line summaries to find the pages you need. Cite with `[[wikilinks]]`. If the index does not surface good candidates, fall back to `wiki_search.py` from the `llm-wiki` skill for local hybrid retrieval; add `--no-embed` for dependency-free BM25.

To add a new source, follow the `llm-wiki` skill's ingest workflow: decide placement under `wiki/architecture/`, `wiki/bugs/`, `wiki/decisions/`, `wiki/lessons/`, `wiki/people/`, `wiki/workflows/`, `wiki/concepts/`, `wiki/glossary/`, `wiki/references/`, or `wiki/sources/`/`wiki/entities/`/`wiki/synthesis/`; identify touched pages and make surgical edits rather than rewrites; update the index; append a one-line entry to `wiki/log.md`.

Scaling discipline: atomic pages (400-line soft cap, 800-line hard cap), sharded indexes past ~150 pages or 300 index lines, required YAML frontmatter on every page, `[[wikilinks]]` for every cross-reference.

Full conventions live in `wiki/SCHEMA.md`. Treat it as authoritative when it disagrees with this summary.
