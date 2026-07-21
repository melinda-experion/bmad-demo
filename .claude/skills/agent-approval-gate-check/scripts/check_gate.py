#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Check whether a document is approved and hasn't been edited since.

Reads the shared approval-state.json, looks up `doc_type`, and compares the
recorded approved_mtime against the document's current on-disk mtime. If the
document was edited after approval, reverts its frontmatter status back to
draft (atomically, as part of this check) and reports it as stale.

Prints one JSON object to stdout:
  {"result": "ok", "approved_mtime": "..."}
  {"result": "blocked", "reason": "missing"}       -- doc_path does not exist
  {"result": "blocked", "reason": "unapproved"}     -- no matching approval on record
  {"result": "blocked", "reason": "stale", "approved_mtime": "...", "current_mtime": "..."}
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def set_status(text: str, status_field: str, draft_value: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return text
    frontmatter = match.group(1)
    field_re = re.compile(rf"^({re.escape(status_field)}\s*:\s*).*$", re.MULTILINE)
    if not field_re.search(frontmatter):
        return text
    new_frontmatter = field_re.sub(rf"\g<1>{draft_value}", frontmatter, count=1)
    return text[: match.start(1)] + new_frontmatter + text[match.end(1) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-path", required=True, help="Path to the document to check")
    parser.add_argument("--doc-type", required=True, help="State-file key for this document type, e.g. 'brief'")
    parser.add_argument("--state-file", required=True, help="Path to the shared approval-state.json")
    parser.add_argument("--status-field", default="status", help="Frontmatter field name (default: %(default)s)")
    parser.add_argument("--draft-value", default="draft", help="Value to revert to (default: %(default)s)")
    args = parser.parse_args()

    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        print(json.dumps({"result": "blocked", "reason": "missing"}))
        return 0

    resolved_doc_path = str(doc_path.resolve())

    state_file = Path(args.state_file)
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}
    if not isinstance(state, dict):
        state = {}

    entry = state.get(args.doc_type)
    if not entry or entry.get("doc_path") != resolved_doc_path:
        print(json.dumps({"result": "blocked", "reason": "unapproved"}))
        return 0

    approved_mtime = entry.get("approved_mtime")
    current_mtime = datetime.fromtimestamp(doc_path.stat().st_mtime, tz=timezone.utc).isoformat()

    try:
        is_stale = approved_mtime is None or current_mtime > approved_mtime
    except TypeError:
        is_stale = True

    if is_stale:
        text = doc_path.read_text(encoding="utf-8")
        new_text = set_status(text, args.status_field, args.draft_value)
        if new_text != text:
            doc_path.write_text(new_text, encoding="utf-8")
        print(
            json.dumps(
                {
                    "result": "blocked",
                    "reason": "stale",
                    "approved_mtime": approved_mtime,
                    "current_mtime": current_mtime,
                }
            )
        )
        return 0

    print(json.dumps({"result": "ok", "approved_mtime": approved_mtime}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
