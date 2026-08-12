#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Compute a deterministic 0-100 code-confidence score for a single file.

Combines four signals into one weighted score:
  1. test pass/fail rate for tests touching the file
  2. lint/static-analysis error and warning counts
  3. lines changed relative to file size (diff-size ratio)
  4. revision cycle count for the run (pulled from approval-state.json
     when --state-file/--doc-type are given instead of an explicit
     --revision-cycles)

All raw signal counts (tests passed/failed, lint errors/warnings, lines
changed) are supplied by the caller after running the project's actual
test runner / linter / `git diff --stat` -- this script does no static
analysis of its own and makes no judgment call about the numbers; it only
turns already-measured counts into a score, a label, and a rationale that
spells out every signal's score, weight, and contribution to the final
number (not just the weakest one), so the full "why" is reconstructable
from the logged row alone. Every weight, penalty, and bucket cutoff is a
CLI argument with a sensible default -- none of them are hardcoded past
the argparse defaults, so a team can retune scoring without touching this
file.

Prints one JSON object to stdout (or --output) with the final score, a
fully detailed confidence_rationale, plus the raw per-component breakdown
to audit how it was reached.
"""

import argparse
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
VERSION_FIELD_RE = re.compile(r"^version\s*:\s*(.*)$", re.MULTILINE)

DEFAULT_DIFF_RATIO_CUTOFFS = [[0.1, 100], [0.3, 80], [0.6, 60], [1.0, 40], [999999, 20]]
DEFAULT_REVISION_CYCLE_CUTOFFS = [[0, 100], [1, 80], [2, 60], [3, 40], [999999, 20]]
DEFAULT_LABEL_CUTOFFS = [[80, "High"], [50, "Medium"], [0, "Low"]]


def read_version(doc_path: Path) -> int:
    if not doc_path.exists():
        return 0
    try:
        text = doc_path.read_text(encoding="utf-8")
    except OSError:
        return 0
    match = FRONTMATTER_RE.match(text)
    if not match:
        return 0
    existing = VERSION_FIELD_RE.search(match.group(1))
    if not existing:
        return 0
    try:
        return int(str(existing.group(1)).strip())
    except ValueError:
        return 0


def resolve_from_state(state_file: str, doc_type: str) -> tuple:
    """Return (revision_cycles, doc_status) derived from approval-state.json."""
    path = Path(state_file)
    state = {}
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}
    if not isinstance(state, dict):
        state = {}

    entry = state.get(doc_type)
    if not isinstance(entry, dict):
        return 0, "unapproved"

    doc_status = "draft" if entry.get("superseded") else "approved"
    revision_cycles = read_version(Path(entry["doc_path"])) if entry.get("doc_path") else 0
    return revision_cycles, doc_status


def bucket_score(value: float, cutoffs: list) -> float:
    """First cutoff (ascending max-threshold, score) where value <= threshold."""
    for threshold, score in sorted(cutoffs, key=lambda c: c[0]):
        if value <= threshold:
            return score
    return cutoffs[-1][1]


def bucket_label(score: float, cutoffs: list) -> str:
    """First cutoff (descending min-threshold, label) where score >= threshold."""
    for threshold, label in sorted(cutoffs, key=lambda c: -c[0]):
        if score >= threshold:
            return label
    return sorted(cutoffs, key=lambda c: c[0])[0][1]


def plural(n: int, noun: str) -> str:
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def compute(args) -> dict:
    tests_total = args.tests_passed + args.tests_failed

    if tests_total == 0:
        test_score = args.no_tests_score
        test_phrase = "no tests touch this file"
    elif args.tests_failed > 0:
        test_score = 100 * args.tests_passed / tests_total
        test_phrase = plural(args.tests_failed, "test failure")
    else:
        test_score = 100
        test_phrase = f"{args.tests_passed}/{tests_total} tests passed"

    lint_score = max(0, 100 - args.lint_errors * args.error_penalty - args.lint_warnings * args.warning_penalty)
    lint_parts = []
    if args.lint_errors > 0:
        lint_parts.append(plural(args.lint_errors, "lint error"))
    if args.lint_warnings > 0:
        lint_parts.append(plural(args.lint_warnings, "lint warning"))
    lint_phrase = ", ".join(lint_parts) if lint_parts else "no lint issues"

    file_size = args.file_size
    if file_size is None:
        file_path = Path(args.file_path)
        if file_path.exists():
            try:
                file_size = sum(1 for _ in file_path.open("r", encoding="utf-8", errors="ignore"))
            except OSError:
                file_size = 0
        else:
            file_size = 0

    ratio = args.lines_changed / max(file_size, 1)
    diff_score = bucket_score(ratio, args.diff_ratio_cutoffs)
    diff_phrase = f"{args.lines_changed} lines changed of {file_size} ({ratio:.0%})"

    if args.revision_cycles is not None:
        revision_cycles = args.revision_cycles
    elif args.state_file and args.doc_type:
        revision_cycles, resolved_doc_status = resolve_from_state(args.state_file, args.doc_type)
        if args.doc_status is None:
            args.doc_status = resolved_doc_status
    else:
        revision_cycles = 0

    revision_score = bucket_score(revision_cycles, args.revision_cycle_cutoffs)
    revision_phrase = plural(revision_cycles, "revision cycle") if revision_cycles > 0 else "no revision cycles"

    doc_status = args.doc_status or ""

    weights = {
        "test": args.test_weight,
        "lint": args.lint_weight,
        "diff": args.diff_weight,
        "revision": args.revision_weight,
    }
    total_weight = sum(weights.values()) or 1

    components = {
        "test": {"score": test_score, "weight": weights["test"], "phrase": test_phrase},
        "lint": {"score": lint_score, "weight": weights["lint"], "phrase": lint_phrase},
        "diff": {"score": diff_score, "weight": weights["diff"], "phrase": diff_phrase},
        "revision": {"score": revision_score, "weight": weights["revision"], "phrase": revision_phrase},
    }

    confidence = round(
        sum(c["score"] * c["weight"] for c in components.values()) / total_weight
    )
    confidence = max(0, min(100, confidence))

    confidence_label = bucket_label(confidence, args.label_cutoffs)

    rationale_parts = []
    for name in ("test", "lint", "diff", "revision"):
        c = components[name]
        contrib = c["score"] * c["weight"] / total_weight
        rationale_parts.append(
            f"{name}: {c['phrase']} (score={c['score']:g}, weight={c['weight']:g}%, contrib={contrib:.1f})"
        )
    confidence_rationale = "; ".join(rationale_parts) + f"; total={confidence}"

    return {
        "file_path": args.file_path,
        "confidence": confidence,
        "confidence_label": confidence_label,
        "confidence_rationale": confidence_rationale,
        "doc_status": doc_status,
        "components": components,
    }


def json_pairs(value: str, name: str) -> list:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, list) or not all(isinstance(pair, list) and len(pair) == 2 for pair in parsed):
        raise argparse.ArgumentTypeError(f"{name} must be a JSON list of [threshold, value] pairs")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file-path", required=True, help="Path to the file being scored (recorded as doc_path)")

    parser.add_argument("--tests-passed", type=int, default=0, help="Passing tests touching this file (default: 0)")
    parser.add_argument("--tests-failed", type=int, default=0, help="Failing tests touching this file (default: 0)")
    parser.add_argument(
        "--no-tests-score",
        type=float,
        default=50,
        help="Test sub-score used when no tests touch this file (default: %(default)s)",
    )

    parser.add_argument("--lint-errors", type=int, default=0, help="Lint/static-analysis error count (default: 0)")
    parser.add_argument("--lint-warnings", type=int, default=0, help="Lint/static-analysis warning count (default: 0)")
    parser.add_argument("--error-penalty", type=float, default=20, help="Points deducted per lint error (default: %(default)s)")
    parser.add_argument("--warning-penalty", type=float, default=5, help="Points deducted per lint warning (default: %(default)s)")

    parser.add_argument("--lines-changed", type=int, default=0, help="Lines added+removed for this file in the diff (default: 0)")
    parser.add_argument(
        "--file-size",
        type=int,
        default=None,
        help="Line count of the file; auto-counted from --file-path if omitted",
    )

    parser.add_argument("--revision-cycles", type=int, default=None, help="Explicit revision cycle count; overrides state-file resolution")
    parser.add_argument("--doc-status", default=None, help="Explicit doc_status; overrides state-file resolution")
    parser.add_argument("--state-file", default=None, help="Path to shared approval-state.json for resolving revision cycles/doc_status")
    parser.add_argument("--doc-type", default=None, help="State-file key for the current run, e.g. 'story-3.2'")

    parser.add_argument("--test-weight", type=float, default=40, help="Weight for the test signal (default: %(default)s)")
    parser.add_argument("--lint-weight", type=float, default=25, help="Weight for the lint signal (default: %(default)s)")
    parser.add_argument("--diff-weight", type=float, default=20, help="Weight for the diff-size signal (default: %(default)s)")
    parser.add_argument("--revision-weight", type=float, default=15, help="Weight for the revision-cycle signal (default: %(default)s)")

    parser.add_argument(
        "--diff-ratio-cutoffs",
        type=lambda v: json_pairs(v, "--diff-ratio-cutoffs"),
        default=DEFAULT_DIFF_RATIO_CUTOFFS,
        help="JSON list of [max_ratio, score] pairs, ascending (default: %(default)s)",
    )
    parser.add_argument(
        "--revision-cycle-cutoffs",
        type=lambda v: json_pairs(v, "--revision-cycle-cutoffs"),
        default=DEFAULT_REVISION_CYCLE_CUTOFFS,
        help="JSON list of [max_cycles, score] pairs, ascending (default: %(default)s)",
    )
    parser.add_argument(
        "--label-cutoffs",
        type=lambda v: json_pairs(v, "--label-cutoffs"),
        default=DEFAULT_LABEL_CUTOFFS,
        help="JSON list of [min_score, label] pairs (default: %(default)s)",
    )

    parser.add_argument("-o", "--output", help="Write result JSON here instead of stdout")
    args = parser.parse_args()

    result = compute(args)

    output_text = json.dumps(result)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
