"""
Token estimation / size-limit validator.

Uses `tiktoken` when available for an accurate count against the configured
encoding; falls back to a conservative chars/4 heuristic if tiktoken (or its
encoding data) is not available, e.g. on an air-gapped deployment.
"""
from __future__ import annotations

from typing import Any, Dict

from models.prompt_result import Finding, Severity, ValidatorResult

try:
    import tiktoken

    _TIKTOKEN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TIKTOKEN_AVAILABLE = False


class TokenValidator:
    name = "token"

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.max_tokens = int(self.config.get("max_prompt_tokens", 4096))
        self.warn_tokens = int(self.config.get("warn_prompt_tokens", 2048))
        self.encoding_name = self.config.get("encoding", "cl100k_base")
        self._encoder = None
        if _TIKTOKEN_AVAILABLE:
            try:
                self._encoder = tiktoken.get_encoding(self.encoding_name)
            except Exception:  # pragma: no cover - offline fallback
                self._encoder = None

    def count_tokens(self, text: str) -> int:
        if self._encoder is not None:
            return len(self._encoder.encode(text))
        # Heuristic fallback: ~4 characters per token for English text.
        return max(1, len(text) // 4)

    def validate(self, text: str) -> ValidatorResult:
        token_count = self.count_tokens(text)
        findings = []

        if token_count > self.max_tokens:
            findings.append(
                Finding(
                    name="token_limit_exceeded",
                    category="size_limit",
                    risk_score=60.0,
                    description=f"Prompt uses {token_count} tokens, exceeding max of {self.max_tokens}",
                    severity=Severity.HIGH,
                )
            )
        elif token_count > self.warn_tokens:
            findings.append(
                Finding(
                    name="token_limit_warning",
                    category="size_limit",
                    risk_score=15.0,
                    description=f"Prompt uses {token_count} tokens, approaching max of {self.max_tokens}",
                    severity=Severity.LOW,
                )
            )

        risk_score = max((f.risk_score for f in findings), default=0.0)
        return ValidatorResult(
            validator=self.name,
            passed=token_count <= self.max_tokens,
            risk_score=risk_score,
            findings=findings,
            metadata={"token_count": token_count, "estimation_method": "tiktoken" if self._encoder else "heuristic"},
        )
