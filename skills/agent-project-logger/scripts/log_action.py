#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Append one timestamped action row to a project's CSV log.

Creates the log file with a
`date,time,user,action,stage,agent,doc_status,confidence,confidence_label,
confidence_rationale,doc_path` header on first write. If an existing log
still has an older, narrower header (e.g. `date,time,user,action` or
`date,time,user,action,stage,agent,doc_status`), that header row is widened
in place to the current schema — existing logged rows are never rewritten,
reordered, or truncated, only the header label itself is brought up to
date. Rows logged before the confidence/doc_path columns existed simply
have fewer values than the widened header; that's expected for an
append-only log.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

HEADER = [
    "date",
    "time",
    "user",
    "action",
    "stage",
    "agent",
    "doc_status",
    "confidence",
    "confidence_label",
    "confidence_rationale",
    "doc_path",
]


def resolve_path(pattern: str, project_name: str, output_dir: Path) -> Path:
    filename = pattern.format(project_name=project_name)
    return output_dir / filename


def append_row(
    log_path: Path,
    user: str,
    action: str,
    stage: str,
    agent: str,
    doc_status: str,
    now: datetime,
    *,
    confidence: str = "",
    confidence_label: str = "",
    confidence_rationale: str = "",
    doc_path: str = "",
) -> list:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    if log_path.exists():
        with log_path.open("r", newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))

    if not rows:
        rows = [HEADER]
    elif rows[0] != HEADER:
        rows[0] = HEADER

    row = [
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        user,
        action,
        stage,
        agent,
        doc_status,
        confidence,
        confidence_label,
        confidence_rationale,
        doc_path,
    ]
    rows.append(row)

    with log_path.open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    return row


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append one action row to a project's CSV log. "
        "Creates the file with a date,time,user,action,stage,agent,doc_status header if it doesn't exist. "
        "Never reorders or deletes existing rows."
    )
    parser.add_argument("--project-name", required=True, help="Project name substituted into the filename pattern")
    parser.add_argument("--action", required=True, help="Action description to record")
    parser.add_argument("--user", required=True, help="User to attribute the row to")
    parser.add_argument(
        "--stage",
        default="",
        help="Development-cycle stage the action concerns, e.g. brief/prd/architecture/stories (default: empty)",
    )
    parser.add_argument(
        "--agent",
        default="",
        help="Name/code of the skill or agent persona that was executing when this action occurred (default: empty)",
    )
    parser.add_argument(
        "--doc-status",
        default="",
        help="Current status of the document the action concerns, e.g. draft/approved (default: empty)",
    )
    parser.add_argument(
        "--confidence",
        default="",
        help="Confidence score (0-100) for the document/artifact this action concerns (default: empty)",
    )
    parser.add_argument(
        "--confidence-label",
        default="",
        help="Confidence label, e.g. Low/Medium/High (default: empty)",
    )
    parser.add_argument(
        "--confidence-rationale",
        default="",
        help="One to two sentence rationale for the confidence score (default: empty)",
    )
    parser.add_argument(
        "--doc-path",
        default="",
        help="Resolved path to the document/file this action concerns (default: empty)",
    )
    parser.add_argument(
        "--pattern",
        default="{project_name}-project-log.csv",
        help="Filename pattern; {project_name} is substituted (default: %(default)s)",
    )
    parser.add_argument("--output-dir", required=True, help="Directory the log file lives in")
    parser.add_argument("-o", "--output", help="Write result JSON here instead of stdout")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    pattern = args.pattern or "{project_name}-project-log.csv"
    output_dir = Path(args.output_dir)
    log_path = resolve_path(pattern, args.project_name, output_dir)

    if args.verbose:
        print(f"Resolved log path: {log_path}", file=sys.stderr)

    try:
        row = append_row(
            log_path,
            args.user,
            args.action,
            args.stage,
            args.agent,
            args.doc_status,
            datetime.now(),
            confidence=args.confidence,
            confidence_label=args.confidence_label,
            confidence_rationale=args.confidence_rationale,
            doc_path=args.doc_path,
        )
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    import json

    result = {"path": str(log_path), "row": row}
    output_text = json.dumps(result)

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
