"""
PII / secrets detection validator.

Detects common personally-identifiable-information patterns (emails, phone
numbers, SSNs, credit cards) as well as credential-shaped secrets (AWS keys,
generic API tokens, password= assignments). Credit card candidates are
verified with a Luhn checksum to cut down on false positives.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from models.prompt_result import Finding, Severity, ValidatorResult

_PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone_number": re.compile(r"(?<!\d)(\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "ip_address": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "aws_access_key": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    # Vendor-style prefixes (sk-/pk-) are near-unambiguous outside of secrets
    # (Stripe, OpenAI, Anthropic keys all use them), so hyphen/underscore
    # segments in the body -- e.g. "sk-ant-api03-AAAA...", "pk_live_51H8..."
    # -- are allowed with no extra guard. Word-ish prefixes (api/token/key)
    # collide with ordinary hyphenated prose ("key-value-store"), so those
    # require a digit somewhere in the body to reduce false positives.
    "generic_api_key": re.compile(
        r"\b(sk|pk)[-_][A-Za-z0-9][A-Za-z0-9_-]{14,}[A-Za-z0-9]\b|"
        r"\b(api|token|key)[-_](?=[A-Za-z0-9_-]*\d)[A-Za-z0-9][A-Za-z0-9_-]{14,}[A-Za-z0-9]\b|"
        r"\b[A-Za-z0-9_\-]{32,}\b(?=.{0,5}$)"
    ),
    "password_field": re.compile(r"(?i)\b(password|passwd|pwd|secret)\s*[:=]\s*\S+"),
}


def _luhn_valid(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _severity_for(score: float) -> Severity:
    if score >= 85:
        return Severity.CRITICAL
    if score >= 60:
        return Severity.HIGH
    if score >= 30:
        return Severity.MEDIUM
    return Severity.LOW


class PIIValidator:
    name = "pii"

    def __init__(self, rules: Dict[str, Any] | None = None):
        self.rules = rules or {}

    def _enabled(self, key: str) -> bool:
        cfg = self.rules.get(key, {})
        return cfg.get("enabled", True)

    def _risk(self, key: str, default: float = 40.0) -> float:
        return float(self.rules.get(key, {}).get("risk_score", default))

    def redact(self, text: str) -> str:
        """Return a copy of `text` with all enabled PII/secret patterns
        replaced by a `[REDACTED_<TYPE>]` placeholder."""
        redacted = text
        for key, pattern in _PATTERNS.items():
            if not self._enabled(key):
                continue
            redacted = pattern.sub(f"[REDACTED_{key.upper()}]", redacted)
        return redacted

    def validate(self, text: str) -> ValidatorResult:
        findings: List[Finding] = []

        if self._enabled("email"):
            m = _PATTERNS["email"].search(text)
            if m:
                findings.append(self._finding("email_detected", "pii_email", self._risk("email", 20), m))

        if self._enabled("phone_number"):
            m = _PATTERNS["phone_number"].search(text)
            if m:
                findings.append(self._finding("phone_detected", "pii_phone", self._risk("phone_number", 20), m))

        if self._enabled("ssn"):
            m = _PATTERNS["ssn"].search(text)
            if m:
                findings.append(self._finding("ssn_detected", "pii_ssn", self._risk("ssn", 60), m))

        if self._enabled("credit_card"):
            for m in _PATTERNS["credit_card"].finditer(text):
                candidate = re.sub(r"[ -]", "", m.group(0))
                if _luhn_valid(candidate):
                    findings.append(
                        self._finding("credit_card_detected", "credit_card", self._risk("credit_card", 90), m)
                    )
                    break

        if self._enabled("ip_address"):
            m = _PATTERNS["ip_address"].search(text)
            if m:
                findings.append(self._finding("ip_address_detected", "pii_ip", self._risk("ip_address", 10), m))

        if self._enabled("aws_access_key"):
            m = _PATTERNS["aws_access_key"].search(text)
            if m:
                findings.append(
                    self._finding("aws_key_detected", "secret_leak", self._risk("aws_access_key", 95), m)
                )

        if self._enabled("generic_api_key"):
            m = _PATTERNS["generic_api_key"].search(text)
            if m:
                findings.append(
                    self._finding("api_key_detected", "secret_leak", self._risk("generic_api_key", 85), m)
                )

        if self._enabled("password_field"):
            m = _PATTERNS["password_field"].search(text)
            if m:
                findings.append(
                    self._finding("password_field_detected", "secret_leak", self._risk("password_field", 50), m)
                )

        risk_score = max((f.risk_score for f in findings), default=0.0)
        return ValidatorResult(
            validator=self.name,
            passed=len(findings) == 0,
            risk_score=risk_score,
            findings=findings,
        )

    def _finding(self, name: str, category: str, risk_score: float, match: re.Match) -> Finding:
        snippet = match.group(0)
        masked = snippet[:2] + "*" * max(len(snippet) - 4, 1) + snippet[-2:] if len(snippet) > 4 else "*" * len(snippet)
        return Finding(
            name=name,
            category=category,
            risk_score=risk_score,
            description=f"Detected potential {category.replace('_', ' ')}",
            matched_snippet=masked,
            severity=_severity_for(risk_score),
        )
