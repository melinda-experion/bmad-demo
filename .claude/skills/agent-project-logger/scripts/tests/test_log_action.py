#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for log_action.py."""

import csv
import importlib.util
import sys
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "log_action.py"
spec = importlib.util.spec_from_file_location("log_action", SCRIPT_PATH)
log_action = importlib.util.module_from_spec(spec)
sys.modules["log_action"] = log_action
spec.loader.exec_module(log_action)


class ResolvePathTests(unittest.TestCase):
    def test_default_pattern_substitutes_project_name(self):
        path = log_action.resolve_path("{project_name}-project-log.csv", "acme", Path("/out"))
        self.assertEqual(path, Path("/out/acme-project-log.csv"))

    def test_custom_pattern(self):
        path = log_action.resolve_path("logs-{project_name}.csv", "acme", Path("/out"))
        self.assertEqual(path, Path("/out/logs-acme.csv"))


class AppendRowTests(unittest.TestCase):
    def test_creates_file_with_header_on_first_write(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "acme-project-log.csv"
            now = datetime(2026, 7, 17, 14, 32, 5)
            log_action.append_row(log_path, "Mel", "Deployed v2 to staging", "prd", "agent-project-logger/LOG", "draft", now)

            with log_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(rows[0], log_action.HEADER)
            self.assertEqual(
                rows[1],
                ["2026-07-17", "14:32:05", "Mel", "Deployed v2 to staging", "prd", "agent-project-logger/LOG", "draft", "", "", "", ""],
            )

    def test_appends_without_rewriting_existing_rows(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "acme-project-log.csv"
            first = datetime(2026, 7, 17, 9, 0, 0)
            second = datetime(2026, 7, 17, 10, 0, 0)

            log_action.append_row(log_path, "Mel", "First action", "brief", "experion-brief-review/RB", "draft", first)
            log_action.append_row(log_path, "Sam", "Second action", "prd", "", "", second)

            with log_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(len(rows), 3)
            self.assertEqual(
                rows[1],
                ["2026-07-17", "09:00:00", "Mel", "First action", "brief", "experion-brief-review/RB", "draft", "", "", "", ""],
            )
            self.assertEqual(rows[2], ["2026-07-17", "10:00:00", "Sam", "Second action", "prd", "", "", "", "", "", ""])

    def test_no_header_written_when_file_already_exists(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "acme-project-log.csv"
            now = datetime(2026, 7, 17, 9, 0, 0)

            log_action.append_row(log_path, "Mel", "First action", "", "", "", now)
            log_action.append_row(log_path, "Mel", "Second action", "", "", "", now)

            with log_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            header_count = sum(1 for row in rows if row == log_action.HEADER)
            self.assertEqual(header_count, 1)

    def test_confidence_columns_recorded(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "acme-project-log.csv"
            now = datetime(2026, 7, 30, 9, 0, 0)

            log_action.append_row(
                log_path,
                "Mel",
                "Confidence scored: 82 (High) for prd.md",
                "prd",
                "bmad-prd",
                "final",
                now,
                confidence="82",
                confidence_label="High",
                confidence_rationale="All FRs traced to confirmed input; no unresolved assumptions.",
                doc_path="_bmad-output/planning-artifacts/prd/prd.md",
            )

            with log_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(rows[0], log_action.HEADER)
            self.assertEqual(
                rows[1],
                [
                    "2026-07-30",
                    "09:00:00",
                    "Mel",
                    "Confidence scored: 82 (High) for prd.md",
                    "prd",
                    "bmad-prd",
                    "final",
                    "82",
                    "High",
                    "All FRs traced to confirmed input; no unresolved assumptions.",
                    "_bmad-output/planning-artifacts/prd/prd.md",
                ],
            )

    def test_widens_older_seven_column_header_in_place(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "acme-project-log.csv"
            old_header = ["date", "time", "user", "action", "stage", "agent", "doc_status"]
            with log_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(
                    [old_header, ["2026-07-17", "09:00:00", "Mel", "First action", "brief", "", "draft"]]
                )

            now = datetime(2026, 7, 30, 9, 0, 0)
            log_action.append_row(log_path, "Mel", "Second action", "", "", "", now)

            with log_path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(rows[0], log_action.HEADER)
            self.assertEqual(rows[1], ["2026-07-17", "09:00:00", "Mel", "First action", "brief", "", "draft"])


if __name__ == "__main__":
    unittest.main()
