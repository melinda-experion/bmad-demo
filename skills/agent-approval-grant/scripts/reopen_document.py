#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Reopen a previously approved document for revision.

Edits the `status:` line inside the document's leading `---` frontmatter
block to the reopen value, saves the file, then marks the matching
`doc_type` entry in the shared JSON state file as superseded. The entry
itself is kept, not deleted, so the prior approval stays on record for
audit purposes -- only a `superseded: true` flag is added to it. Other
doc_type entries in that file are preserved untouched (read-modify-write
merge, never a full overwrite).
"""

import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def set_status(text: str, status_field: str, reopen_value: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("no YAML frontmatter block found at the top of the file")

    frontmatter = match.group(1)
    field_re = re.compile(rf"^({re.escape(status_field)}\s*:\s*).*$", re.MULTILINE)
    if not field_re.search(frontmatter):
        raise ValueError(f"no '{status_field}:' field found in frontmatter")

    new_frontmatter = field_re.sub(rf"\g<1>{reopen_value}", frontmatter, count=1)
    return text[: match.start(1)] + new_frontmatter + text[match.end(1) :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doc-path", required=True, help="Path to the document to reopen")
    parser.add_argument("--doc-type", required=True, help="State-file key for this document type, e.g. 'brief'")
    parser.add_argument("--state-file", required=True, help="Path to the shared approval-state.json")
    parser.add_argument("--status-field", default="status", help="Frontmatter field name (default: %(default)s)")
    parser.add_argument("--reopen-value", default="draft", help="Value to set (default: %(default)s)")
    args = parser.parse_args()

    doc_path = Path(args.doc_path)
    if not doc_path.exists():
        print(f"error: doc_path does not exist: {doc_path}", file=sys.stderr)
        return 2

    text = doc_path.read_text(encoding="utf-8")
    try:
        new_text = set_status(text, args.status_field, args.reopen_value)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    doc_path.write_text(new_text, encoding="utf-8")

    resolved_doc_path = str(doc_path.resolve())

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

    entry = state.get(args.doc_type)
    superseded = False
    if isinstance(entry, dict) and entry.get("doc_path") == resolved_doc_path:
        entry["superseded"] = True
        state[args.doc_type] = entry
        state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        superseded = True

    result = {
        "doc_path": resolved_doc_path,
        "doc_type": args.doc_type,
        "reopen_value": args.reopen_value,
        "state_file": str(state_file.resolve()),
        "superseded": superseded,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
