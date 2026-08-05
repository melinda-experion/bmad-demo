#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for confidence_score.py."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "confidence_score.py"
spec = importlib.util.spec_from_file_location("confidence_score", SCRIPT_PATH)
confidence_score = importlib.util.module_from_spec(spec)
sys.modules["confidence_score"] = confidence_score
spec.loader.exec_module(confidence_score)


def make_args(**overrides):
    defaults = dict(
        file_path="src/example.py",
        tests_passed=0,
        tests_failed=0,
        no_tests_score=50,
        lint_errors=0,
        lint_warnings=0,
        error_penalty=20,
        warning_penalty=5,
        lines_changed=0,
        file_size=100,
        revision_cycles=0,
        doc_status=None,
        state_file=None,
        doc_type=None,
        test_weight=40,
        lint_weight=25,
        diff_weight=20,
        revision_weight=15,
        diff_ratio_cutoffs=confidence_score.DEFAULT_DIFF_RATIO_CUTOFFS,
        revision_cycle_cutoffs=confidence_score.DEFAULT_REVISION_CYCLE_CUTOFFS,
        label_cutoffs=confidence_score.DEFAULT_LABEL_CUTOFFS,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class BucketTests(unittest.TestCase):
    def test_bucket_score_picks_first_matching_ascending_cutoff(self):
        cutoffs = [[0.1, 100], [0.3, 80], [999, 20]]
        self.assertEqual(confidence_score.bucket_score(0.05, cutoffs), 100)
        self.assertEqual(confidence_score.bucket_score(0.2, cutoffs), 80)
        self.assertEqual(confidence_score.bucket_score(5, cutoffs), 20)

    def test_bucket_label_picks_first_matching_descending_threshold(self):
        cutoffs = [[80, "High"], [50, "Medium"], [0, "Low"]]
        self.assertEqual(confidence_score.bucket_label(95, cutoffs), "High")
        self.assertEqual(confidence_score.bucket_label(60, cutoffs), "Medium")
        self.assertEqual(confidence_score.bucket_label(10, cutoffs), "Low")


class ComputeTests(unittest.TestCase):
    def test_all_signals_clean_scores_high(self):
        args = make_args(tests_passed=5, tests_failed=0, lines_changed=5, file_size=100)
        result = confidence_score.compute(args)
        self.assertEqual(result["confidence"], 100)
        self.assertEqual(result["confidence_label"], "High")
        self.assertEqual(result["confidence_rationale"], "No weak signals detected.")

    def test_test_failures_and_revision_cycles_drive_rationale(self):
        args = make_args(tests_passed=3, tests_failed=2, revision_cycles=3, lines_changed=5, file_size=100)
        result = confidence_score.compute(args)
        self.assertIn("2 test failures", result["confidence_rationale"])
        self.assertIn("3 revision cycles", result["confidence_rationale"])
        self.assertLess(result["confidence"], 80)

    def test_no_tests_touching_file_uses_neutral_score(self):
        args = make_args(tests_passed=0, tests_failed=0, no_tests_score=50)
        result = confidence_score.compute(args)
        self.assertEqual(result["components"]["test"]["score"], 50)
        self.assertIn("no tests touch this file", result["confidence_rationale"])

    def test_lint_errors_reduce_score_and_appear_in_rationale(self):
        args = make_args(tests_passed=5, lint_errors=2, lint_warnings=1)
        result = confidence_score.compute(args)
        self.assertEqual(result["components"]["lint"]["score"], 100 - 2 * 20 - 1 * 5)
        self.assertIn("lint error", result["confidence_rationale"])

    def test_large_diff_ratio_lowers_diff_score(self):
        args = make_args(tests_passed=5, lines_changed=90, file_size=100)
        result = confidence_score.compute(args)
        self.assertLess(result["components"]["diff"]["score"], 100)

    def test_confidence_clamped_between_0_and_100(self):
        args = make_args(
            tests_passed=0,
            tests_failed=10,
            lint_errors=20,
            lint_warnings=20,
            revision_cycles=10,
            lines_changed=1000,
            file_size=10,
        )
        result = confidence_score.compute(args)
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 100)

    def test_explicit_revision_cycles_skips_state_file(self):
        args = make_args(revision_cycles=1, state_file="/does/not/exist.json", doc_type="story-1")
        result = confidence_score.compute(args)
        self.assertEqual(result["components"]["revision"]["score"], 80)


class StateFileResolutionTests(unittest.TestCase):
    def test_resolve_from_state_missing_entry_is_unapproved(self):
        with TemporaryDirectory() as tmp:
            state_file = Path(tmp) / "approval-state.json"
            state_file.write_text(json.dumps({}), encoding="utf-8")
            cycles, status = confidence_score.resolve_from_state(str(state_file), "story-1")
            self.assertEqual(cycles, 0)
            self.assertEqual(status, "unapproved")

    def test_resolve_from_state_superseded_entry_is_draft(self):
        with TemporaryDirectory() as tmp:
            doc_path = Path(tmp) / "story-1.md"
            doc_path.write_text("---\nstatus: draft\nversion: 2\n---\nbody\n", encoding="utf-8")
            state_file = Path(tmp) / "approval-state.json"
            state_file.write_text(
                json.dumps({"story-1": {"doc_path": str(doc_path), "superseded": True}}), encoding="utf-8"
            )
            cycles, status = confidence_score.resolve_from_state(str(state_file), "story-1")
            self.assertEqual(cycles, 2)
            self.assertEqual(status, "draft")

    def test_resolve_from_state_approved_entry_reads_version(self):
        with TemporaryDirectory() as tmp:
            doc_path = Path(tmp) / "story-1.md"
            doc_path.write_text("---\nstatus: approved\nversion: 1\n---\nbody\n", encoding="utf-8")
            state_file = Path(tmp) / "approval-state.json"
            state_file.write_text(
                json.dumps({"story-1": {"doc_path": str(doc_path)}}), encoding="utf-8"
            )
            cycles, status = confidence_score.resolve_from_state(str(state_file), "story-1")
            self.assertEqual(cycles, 1)
            self.assertEqual(status, "approved")


if __name__ == "__main__":
    unittest.main()
