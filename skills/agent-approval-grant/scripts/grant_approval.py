#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Mark a document's frontmatter status as approved and record the approval.

Edits the `status:` line inside the document's leading `---` frontmatter
block to the approved value, saves the file, then reads the file's own
post-save mtime and records {doc_path, approved_mtime} under `doc_type` in
a shared JSON state file. Other doc_type entries in that file are preserved
untouched (read-modify-write merge, never a full overwrite).
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def set_status(text: str, status_field: str, approved_value: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("no YAML frontmatter block found at the top of the file")

    frontmatter = match.group(1)
    field_re = re.compile(rf"^({re.escape(status_field)}\s*:\s*).*$", re.MULTILINE)
    if not field_re.search(frontmatter):
        raise ValueError(f"no '{status_field}:' field found in frontmatter")

    new_frontmatter = field_re.sub(rf"\g<1>{approved_value}", frontmatter, count=1)
    return text[: match.start(1)] + new_frontmatter + text[match.end(1) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-path", required=True, help="Path to the document to approve")
    parser.add_argument("--doc-type", required=True, help="State-file key for this document type, e.g. 'brief'")
    parser.add_argument("--state-file", required=True, help="Path to the shared approval-state.json")
    parser.add_argument("--status-field", default="status", help="Frontmatter field name (default: %(default)s)")
    parser.add_argument("--approved-value", default="approved", help="Value to set (default: %(default)s)")
    args = parser.parse_args()

    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        print(f"error: doc_path does not exist: {doc_path}", file=sys.stderr)
        return 2

    text = doc_path.read_text(encoding="utf-8")
    try:
        new_text = set_status(text, args.status_field, args.approved_value)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    doc_path.write_text(new_text, encoding="utf-8")

    approved_mtime = datetime.fromtimestamp(doc_path.stat().st_mtime, tz=timezone.utc).isoformat()

    state_file = Path(args.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}
    if not isinstance(state, dict):
        state = {}

    resolved_doc_path = str(doc_path.resolve())
    state[args.doc_type] = {"doc_path": resolved_doc_path, "approved_mtime": approved_mtime}
    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    result = {
        "doc_path": resolved_doc_path,
        "doc_type": args.doc_type,
        "approved_mtime": approved_mtime,
        "state_file": str(state_file.resolve()),
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
