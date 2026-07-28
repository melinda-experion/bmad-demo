"""
Prompt injection / jailbreak detection validator.

Matches against a configurable list of patterns from `policy.yaml` under
`injection.patterns` (instruction-override attempts, role-escape/jailbreak
phrasing, delimiter confusion, system-prompt exfiltration attempts, and
suspicious base64-shaped payloads that may hide an obfuscated instruction).
"""
from __future__ import annotations

import base64
import re
from typing import Any, Dict, List

from models.prompt_result import Finding, Severity, ValidatorResult


def _severity_for(score: float) -> Severity:
    if score >= 80:
        return Severity.CRITICAL
    if score >= 60:
        return Severity.HIGH
    if score >= 35:
        return Severity.MEDIUM
    return Severity.LOW


def _looks_like_instruction(decoded: str) -> bool:
    keywords = ("ignore", "system", "prompt", "instruction", "override", "jailbreak")
    lowered = decoded.lower()
    return any(k in lowered for k in keywords)


class InjectionValidator:
    name = "injection"

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._compiled = []
        for rule in self.config.get("patterns", []):
            try:
                pattern = re.compile(rule["pattern"])
            except re.error as exc:
                raise ValueError(f"Invalid injection pattern '{rule.get('name')}': {exc}") from exc
            self._compiled.append((pattern, rule))

    def validate(self, text: str) -> ValidatorResult:
        if not self.enabled:
            return ValidatorResult(validator=self.name, passed=True, risk_score=0.0)

        findings: List[Finding] = []

        for pattern, rule in self._compiled:
            if rule.get("name") == "base64_payload":
                findings.extend(self._check_base64(pattern, text, rule))
                continue
            match = pattern.search(text)
            if match:
                risk_score = float(rule.get("risk_score", 50))
                findings.append(
                    Finding(
                        name=rule["name"],
                        category=rule.get("category", "injection"),
                        risk_score=risk_score,
                        description=f"Matched injection heuristic '{rule['name']}'",
                        matched_snippet=match.group(0)[:80],
                        severity=_severity_for(risk_score),
                    )
                )

        risk_score = max((f.risk_score for f in findings), default=0.0)
        return ValidatorResult(
            validator=self.name,
            passed=len(findings) == 0,
            risk_score=risk_score,
            findings=findings,
            metadata={"patterns_evaluated": len(self._compiled)},
        )

    def _check_base64(self, pattern: re.Pattern, text: str, rule: Dict[str, Any]) -> List[Finding]:
        findings: List[Finding] = []
        for match in pattern.finditer(text):
            candidate = match.group(0)
            try:
                decoded = base64.b64decode(candidate, validate=True).decode("utf-8", errors="ignore")
            except Exception:
                continue
            if _looks_like_instruction(decoded):
                risk_score = float(rule.get("risk_score", 40)) + 20  # decoded payload confirms intent
                findings.append(
                    Finding(
                        name="base64_obfuscated_injection",
                        category="critical_injection",
                        risk_score=min(risk_score, 100.0),
                        description="Base64-encoded payload decodes to instruction-like text",
                        matched_snippet=candidate[:40],
                        severity=Severity.CRITICAL,
                    )
                )
        return findings
