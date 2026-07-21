#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Append one timestamped action row to a project's CSV log.

Creates the log file with a `date,time,user,action` header on first write.
Never rewrites, reorders, or truncates existing rows.
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

HEADER = ["date", "time", "user", "action"]


def resolve_path(pattern: str, project_name: str, output_dir: Path) -> Path:
    filename = pattern.format(project_name=project_name)
    return output_dir / filename


def append_row(log_path: Path, user: str, action: str, now: datetime) -> list:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not log_path.exists()

    row = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), user, action]

    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(HEADER)
        writer.writerow(row)

    return row


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append one action row to a project's CSV log. "
        "Creates the file with a date,time,user,action header if it doesn't exist. "
        "Never reorders or deletes existing rows."
    )
    parser.add_argument(
        "--project-name",
        required=True,
        help="Project name substituted into the filename pattern",
    )
    parser.add_argument("--action", required=True, help="Action description to record")
    parser.add_argument(
        "--user", required=True, help="BMADUser to attribute the row to"
    )
    parser.add_argument(
        "--pattern",
        default="{project_name}-project-log.csv",
        help="Filename pattern; {project_name} is substituted (default: %(default)s)",
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory the log file lives in"
    )
    parser.add_argument(
        "-o", "--output", help="Write result JSON here instead of stdout"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print diagnostics to stderr"
    )
    args = parser.parse_args()

    pattern = args.pattern or "{project_name}-project-log.csv"
    output_dir = Path(args.output_dir)
    log_path = resolve_path(pattern, args.project_name, output_dir)

    if args.verbose:
        print(f"Resolved log path: {log_path}", file=sys.stderr)

    try:
        row = append_row(log_path, args.user, args.action, datetime.now())
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
