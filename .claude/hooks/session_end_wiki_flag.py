#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""SessionEnd hook: record that a session finished so the next session can review it.

SessionEnd can only run a plain command (no LLM access), so this script does no
judgment of its own -- it just copies the transcript into a durable local queue
and records {session_id, transcript_path, ended_at}. The actual "is this
wiki-ingest-worthy?" reasoning happens later, in-band, when
session_start_wiki_review.py surfaces the queue to a live Claude session via
SessionStart's additionalContext.

The transcript is copied (not just referenced by path) so this queue survives
Claude Code's own transcript cleanup (cleanupPeriodDays) independent of how
long it takes for you to next open a session here -- reviews are never lost to
that cleanup, only ever explicitly cleared once handed off in
session_start_wiki_review.py.

Fails silently: a queue write failure must never block session shutdown.
"""

import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"
QUEUE_PATH = HOOKS_DIR / ".wiki-review-pending.jsonl"
PENDING_DIR = HOOKS_DIR / "pending-review"
# Backstop only -- the queue is drained on every SessionStart, so this guards
# against a stuck/broken drain, not normal accumulation.
MAX_QUEUE_ENTRIES = 500


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    transcript_path = payload.get("transcript_path") or ""
    session_id = payload.get("session_id") or "unknown"
    ended_at = payload.get("timestamp") or ""

    if not transcript_path:
        return 0

    try:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        copy_path = PENDING_DIR / f"{session_id}.jsonl"
        shutil.copy2(transcript_path, copy_path)
        stored_path = str(copy_path)
    except Exception:
        # Fall back to the original path -- still useful if it's read before cleanup.
        stored_path = transcript_path

    try:
        entries = []
        if QUEUE_PATH.exists():
            for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("session_id") != session_id:
                    entries.append(entry)

        entries.append({
            "session_id": session_id,
            "transcript_path": stored_path,
            "ended_at": ended_at,
        })
        entries = entries[-MAX_QUEUE_ENTRIES:]

        HOOKS_DIR.mkdir(parents=True, exist_ok=True)
        QUEUE_PATH.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n",
            encoding="utf-8",
        )
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
