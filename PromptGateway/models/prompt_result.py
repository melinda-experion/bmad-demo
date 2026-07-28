"""
Internal data structures used to carry validation results through the
pipeline. These are plain dataclasses (not API schemas) so validators stay
decoupled from the FastAPI/pydantic layer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Decision(str, Enum):
    ALLOW = "ALLOW"
    FLAG = "FLAG"
    BLOCK = "BLOCK"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    """A single rule/detector hit produced by a validator."""

    name: str
    category: str
    risk_score: float
    description: str = ""
    matched_snippet: Optional[str] = None
    severity: Severity = Severity.LOW

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "risk_score": self.risk_score,
            "description": self.description,
            "matched_snippet": self.matched_snippet,
            "severity": self.severity.value,
        }


@dataclass
class ValidatorResult:
    """Output of a single validator run."""

    validator: str
    passed: bool
    risk_score: float
    findings: List[Finding] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validator": self.validator,
            "passed": self.passed,
            "risk_score": self.risk_score,
            "findings": [f.to_dict() for f in self.findings],
            "metadata": self.metadata,
            "error": self.error,
        }


@dataclass
class PromptResult:
    """Aggregate result returned to the API layer / caller."""

    request_id: str
    decision: Decision
    risk_score: float
    validator_results: List[ValidatorResult] = field(default_factory=list)
    token_count: int = 0
    sanitized_prompt: Optional[str] = None
    categories_triggered: List[str] = field(default_factory=list)
    timestamp: str = ""
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "decision": self.decision.value,
            "risk_score": self.risk_score,
            "token_count": self.token_count,
            "sanitized_prompt": self.sanitized_prompt,
            "categories_triggered": self.categories_triggered,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "validator_results": [v.to_dict() for v in self.validator_results],
        }
