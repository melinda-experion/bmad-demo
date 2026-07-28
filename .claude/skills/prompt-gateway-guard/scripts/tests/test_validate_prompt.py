#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for validate_prompt.py, using a local http.server stand-in for PromptGateway."""

import json
import subprocess
import sys
import threading
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "validate_prompt.py"


class StubHandler(BaseHTTPRequestHandler):
    response_body = {"decision": "ALLOW", "risk_score": 0, "reason": "ok"}
    response_status = 200
    received = {}

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        StubHandler.received["body"] = json.loads(self.rfile.read(length))
        StubHandler.received["headers"] = dict(self.headers)
        payload = json.dumps(StubHandler.response_body).encode("utf-8")
        self.send_response(StubHandler.response_status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        pass


class ValidatePromptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), StubHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def run_script(self, *extra_args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--prompt", "hello", "--base-url", f"http://127.0.0.1:{self.port}", *extra_args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_allow_decision_passthrough(self):
        StubHandler.response_body = {"decision": "ALLOW", "risk_score": 5, "reason": "clean"}
        StubHandler.response_status = 200
        result = self.run_script()
        payload = json.loads(result.stdout)
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertEqual(StubHandler.received["body"]["prompt"], "hello")
        self.assertNotIn("X-Api-Key", StubHandler.received["headers"])

    def test_api_key_header_sent_when_provided(self):
        StubHandler.response_body = {"decision": "ALLOW", "risk_score": 0}
        StubHandler.response_status = 200
        self.run_script("--api-key", "secret123")
        self.assertEqual(StubHandler.received["headers"].get("X-Api-Key"), "secret123")

    def test_block_decision_passthrough(self):
        StubHandler.response_body = {
            "decision": "BLOCK",
            "risk_score": 95,
            "reason": "Hard-block category triggered: secret_leak",
            "categories_triggered": ["secret_leak"],
        }
        StubHandler.response_status = 200
        result = self.run_script()
        payload = json.loads(result.stdout)
        self.assertEqual(payload["decision"], "BLOCK")
        self.assertIn("secret_leak", payload["categories_triggered"])

    def test_unreachable_service_reports_cleanly(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--prompt", "hello", "--base-url", "http://127.0.0.1:1", "--timeout", "1"],
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "unreachable")

    def test_http_error_reports_status_and_body(self):
        StubHandler.response_body = {"detail": "boom"}
        StubHandler.response_status = 500
        result = self.run_script()
        payload = json.loads(result.stdout)
        self.assertEqual(payload["result"], "http_error")
        self.assertEqual(payload["status"], 500)


if __name__ == "__main__":
    unittest.main()
