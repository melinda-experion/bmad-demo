"""
Decision engine: orchestrates all validators and aggregates their output
into a single risk score + ALLOW/FLAG/BLOCK decision, per the enterprise
policy document (policy.yaml).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from models.prompt_result import Decision, PromptResult, ValidatorResult
from utils.prompt_utils import new_request_id, normalize_text
from validators.injection_validator import InjectionValidator
from validators.llm_validator import LLMValidator
from validators.pii_validator import PIIValidator
from validators.regex_validator import RegexValidator
from validators.token_validator import TokenValidator
from validators.toxicity_validator import ToxicityValidator


class DecisionEngine:
    def __init__(self, policy: Dict[str, Any]):
        self.policy = policy
        self.weights: Dict[str, float] = policy.get("weights", {})
        self.decision_cfg: Dict[str, Any] = policy.get("decision", {})
        self.hard_block_categories = set(self.decision_cfg.get("hard_block_categories", []))

        self.regex_validator = RegexValidator(policy.get("regex_rules", []))
        self.pii_validator = PIIValidator(policy.get("pii_rules", {}))
        self.toxicity_validator = ToxicityValidator(policy.get("toxicity", {}))
        self.injection_validator = InjectionValidator(policy.get("injection", {}))
        self.token_validator = TokenValidator(policy.get("tokens", {}))
        self.llm_validator = LLMValidator(policy.get("llm_validator", {}))

    async def evaluate(self, text: str, request_id: str | None = None) -> PromptResult:
        request_id = request_id or new_request_id()
        normalized = normalize_text(text)

        token_result = self.token_validator.validate(normalized)
        regex_result = self.regex_validator.validate(normalized)
        pii_result = self.pii_validator.validate(normalized)
        toxicity_result = self.toxicity_validator.validate(normalized)
        injection_result = self.injection_validator.validate(normalized)
        llm_result = await self.llm_validator.validate(normalized)

        weighted_results = [regex_result, pii_result, toxicity_result, injection_result, llm_result]
        all_results: List[ValidatorResult] = [token_result, *weighted_results]

        weighted_score = sum(
            self.weights.get(r.validator, 0.0) * r.risk_score for r in weighted_results
        )
        weighted_score = round(min(weighted_score, 100.0), 2)

        categories_triggered = sorted(
            {finding.category for result in all_results for finding in result.findings}
        )

        decision, reason = self._decide(weighted_score, categories_triggered, token_result)
        sanitized_prompt = self.pii_validator.redact(normalized) if pii_result.findings else normalized

        return PromptResult(
            request_id=request_id,
            decision=decision,
            risk_score=weighted_score,
            validator_results=all_results,
            token_count=token_result.metadata.get("token_count", 0),
            sanitized_prompt=sanitized_prompt,
            categories_triggered=categories_triggered,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
        )

    def _decide(
        self, weighted_score: float, categories_triggered: List[str], token_result: ValidatorResult
    ) -> tuple[Decision, str]:
        if not token_result.passed:
            return Decision.BLOCK, "Prompt exceeds configured token limit"

        hard_hit = self.hard_block_categories.intersection(categories_triggered)
        if hard_hit:
            return Decision.BLOCK, f"Hard-block category triggered: {', '.join(sorted(hard_hit))}"

        block_at = float(self.decision_cfg.get("block_at_or_above", 60))
        allow_below = float(self.decision_cfg.get("allow_below", 30))

        if weighted_score >= block_at:
            return Decision.BLOCK, f"Aggregate risk score {weighted_score} >= block threshold {block_at}"
        if weighted_score >= allow_below:
            return Decision.FLAG, f"Aggregate risk score {weighted_score} in review range (>= {allow_below})"
        return Decision.ALLOW, "No policy violations detected"
