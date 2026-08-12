#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Mark a document's frontmatter status as approved and record the approval.

Edits the `status:` line inside the document's leading `---` frontmatter
block to the approved value, bumps the frontmatter `version:` field (default
0 if absent, incremented by 1), saves the file, then hashes the file's own
post-save content and records {doc_path, approved_hash} under `doc_type` in
a shared JSON state file. A content hash is used instead of mtime because
git does not preserve mtimes across clone/pull/checkout -- every teammate's
local checkout would otherwise get a fresh mtime later than the recorded
approval time, making every pull look like a stale edit. Other doc_type
entries in that file are preserved untouched (read-modify-write merge,
never a full overwrite). Finally stages and commits the document via git;
a failed commit is reported in the JSON output rather than raised, since
the approval itself has already succeeded.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
VERSION_FIELD_RE = re.compile(r"^version\s*:\s*(.*)$", re.MULTILINE)


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


def bump_version(text: str) -> tuple[str, int]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("no YAML frontmatter block found at the top of the file")

    frontmatter = match.group(1)
    existing = VERSION_FIELD_RE.search(frontmatter)
    try:
        current_version = int(str(existing.group(1)).strip()) if existing else 0
    except ValueError:
        current_version = 0
    new_version = current_version + 1

    if existing:
        new_frontmatter = VERSION_FIELD_RE.sub(f"version: {new_version}", frontmatter, count=1)
    else:
        new_frontmatter = frontmatter.rstrip("\n") + f"\nversion: {new_version}"

    new_text = text[: match.start(1)] + new_frontmatter + text[match.end(1) :]
    return new_text, new_version


def commit_document(doc_path: Path, doc_type: str, version: int) -> dict:
    commit_message = f"Approve {doc_type} v{version}"
    resolved_doc_path = doc_path.resolve()
    try:
        add_result = subprocess.run(
            ["git", "add", resolved_doc_path.name],
            cwd=resolved_doc_path.parent,
            capture_output=True,
            text=True,
        )
        if add_result.returncode != 0:
            return {"ok": False, "message": commit_message, "error": add_result.stderr.strip()}

        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=resolved_doc_path.parent,
            capture_output=True,
            text=True,
        )
        if commit_result.returncode != 0:
            error = commit_result.stderr.strip() or commit_result.stdout.strip()
            return {"ok": False, "message": commit_message, "error": error}
    except OSError as exc:
        return {"ok": False, "message": commit_message, "error": str(exc)}

    return {"ok": True, "message": commit_message}


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
        new_text, new_version = bump_version(new_text)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    doc_path.write_text(new_text, encoding="utf-8")

    approved_hash = hashlib.sha256(doc_path.read_bytes()).hexdigest()

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
    state[args.doc_type] = {"doc_path": resolved_doc_path, "approved_hash": approved_hash}
    state_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    git_commit = commit_document(doc_path, args.doc_type, new_version)

    result = {
        "doc_path": resolved_doc_path,
        "doc_type": args.doc_type,
        "approved_hash": approved_hash,
        "state_file": str(state_file.resolve()),
        "version": new_version,
        "git_commit": git_commit,
    }
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
