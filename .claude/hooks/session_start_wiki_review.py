#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""SessionStart hook: surface prior sessions' transcripts for wiki review.

Pairs with session_end_wiki_flag.py. SessionEnd cannot run LLM reasoning (only
plain commands), so it just queues durable copies of transcripts. This hook
picks up that queue at the start of the next session and injects an
additionalContext note asking the live Claude instance to review those
transcripts against wiki/SCHEMA.md and run the llm-wiki skill's ingest
workflow for anything that qualifies (decisions, architecture rationale,
lessons, bugs/postmortems, workflow notes) -- skipping transcripts with
nothing wiki-worthy.

The queue (and its durable transcript copies) are cleared once surfaced. If
the resulting session is interrupted before the review happens, that review is
simply skipped rather than retried -- avoids an ever-growing backlog or repeat
prompting across sessions.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"
QUEUE_PATH = HOOKS_DIR / ".wiki-review-pending.jsonl"
PENDING_DIR = HOOKS_DIR / "pending-review"


def main() -> int:
    if not QUEUE_PATH.exists():
        return 0

    try:
        raw = QUEUE_PATH.read_text(encoding="utf-8")
    except Exception:
        return 0

    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    try:
        QUEUE_PATH.unlink()
    except Exception:
        pass

    if not entries:
        return 0

    # List every pending entry -- no silent cap. The queue only accumulates
    # entries between now and the last drain, so this stays small in practice.
    lines = [f"- {e.get('transcript_path')} (session {e.get('session_id', '?')}, ended {e.get('ended_at', '?')})"
             for e in entries]

    context = (
        f"{len(entries)} prior Claude Code session(s) ended without a wiki review. "
        "Before continuing, read wiki/SCHEMA.md then skim each transcript below for "
        "anything wiki-ingest-worthy (decisions, architecture rationale, lessons, "
        "bugs/postmortems, workflow notes) per the llm-wiki skill's ingest workflow. "
        "Ingest what qualifies; skip transcripts with nothing durable to capture. "
        f"Once you've reviewed all of them, delete {PENDING_DIR} (it holds durable "
        "copies kept only until this review happens -- once you've read them, they "
        "can go). Do this quietly and briefly mention what (if anything) you filed.\n\n"
        + "\n".join(lines)
    )

    print(json.dumps({
        "systemMessage": f"[wiki] {len(entries)} session(s) pending wiki review.",
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        },
    }))

    return 0


if __name__ == "__main__":
    sys.exit(main())
