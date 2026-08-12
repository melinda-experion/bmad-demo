"""
Regex-based validator.

Scans the prompt against a configurable list of regular expressions defined
in `policy.yaml` under `regex_rules`. Each rule carries its own category and
risk score, so new patterns can be added/tuned without code changes.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from models.prompt_result import Finding, Severity, ValidatorResult

_SEVERITY_BANDS = (
    (85, Severity.CRITICAL),
    (65, Severity.HIGH),
    (40, Severity.MEDIUM),
    (1, Severity.LOW),
)


def _severity_for(score: float) -> Severity:
    for threshold, severity in _SEVERITY_BANDS:
        if score >= threshold:
            return severity
    return Severity.INFO


class RegexValidator:
    name = "regex"

    def __init__(self, rules: List[Dict[str, Any]] | None = None):
        self.rules = rules or []
        self._compiled = []
        for rule in self.rules:
            try:
                pattern = re.compile(rule["pattern"], re.MULTILINE)
            except re.error as exc:
                raise ValueError(f"Invalid regex in rule '{rule.get('name')}': {exc}") from exc
            self._compiled.append((pattern, rule))

    def validate(self, text: str) -> ValidatorResult:
        findings: List[Finding] = []
        try:
            for pattern, rule in self._compiled:
                match = pattern.search(text)
                if match:
                    snippet = match.group(0)
                    findings.append(
                        Finding(
                            name=rule["name"],
                            category=rule.get("category", "regex_match"),
                            risk_score=float(rule.get("risk_score", 50)),
                            description=rule.get("description", ""),
                            matched_snippet=snippet[:80],
                            severity=_severity_for(float(rule.get("risk_score", 50))),
                        )
                    )
        except Exception as exc:  # pragma: no cover - defensive
            return ValidatorResult(validator=self.name, passed=True, risk_score=0.0, error=str(exc))

        risk_score = max((f.risk_score for f in findings), default=0.0)
        return ValidatorResult(
            validator=self.name,
            passed=len(findings) == 0,
            risk_score=risk_score,
            findings=findings,
            metadata={"rules_evaluated": len(self._compiled)},
        )
