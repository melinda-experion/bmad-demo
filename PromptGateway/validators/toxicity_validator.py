"""
Lightweight lexicon-based toxicity validator.

This is a fast, dependency-free first pass (word-list + leetspeak
normalization). It intentionally does NOT try to be a full ML classifier —
for higher-fidelity toxicity/harassment/hate-speech judgments, the pipeline
also runs `LLMValidator`, which asks a local Ollama model for a nuanced
assessment. This validator exists to catch cheap, obvious cases quickly and
cheaply even when Ollama is unavailable.
"""
from __future__ import annotations

import re
from typing import Dict, List, Set

from models.prompt_result import Finding, Severity, ValidatorResult

_LEET_MAP = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})

# Deliberately small, generic severity buckets. Extend via policy in a real
# deployment (e.g. load from an external, maintained lexicon file).
_LEXICON: Dict[str, Set[str]] = {
    "profanity": {"damn", "hell", "crap", "shit", "fuck", "bitch", "asshole", "bastard"},
    "hate_speech": {"nazi", "racist", "bigot"},
    "harassment": {"kill yourself", "idiot", "moron", "loser", "worthless"},
    "violence": {"kill you", "murder you", "beat you up", "shoot you"},
    "self_harm": {"suicide", "self harm", "cut myself", "end my life"},
}

_CATEGORY_WEIGHT = {
    "profanity": 0.25,
    "hate_speech": 0.9,
    "harassment": 0.6,
    "violence": 0.85,
    "self_harm": 0.95,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().translate(_LEET_MAP))


class ToxicityValidator:
    name = "toxicity"

    def __init__(self, config: Dict | None = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.block_threshold = float(self.config.get("block_threshold", 0.75))
        self.flag_threshold = float(self.config.get("flag_threshold", 0.4))

    def validate(self, text: str) -> ValidatorResult:
        if not self.enabled:
            return ValidatorResult(validator=self.name, passed=True, risk_score=0.0)

        normalized = _normalize(text)
        findings: List[Finding] = []
        max_score = 0.0

        for category, terms in _LEXICON.items():
            for term in terms:
                if term in normalized:
                    score = _CATEGORY_WEIGHT[category]
                    max_score = max(max_score, score)
                    findings.append(
                        Finding(
                            name=f"toxicity_{category}",
                            category=category,
                            risk_score=round(score * 100, 1),
                            description=f"Lexicon match for '{category}' category",
                            matched_snippet=term,
                            severity=Severity.HIGH if score >= self.block_threshold else Severity.MEDIUM,
                        )
                    )
                    break  # one finding per category is enough signal

        risk_score = round(max_score * 100, 1)
        return ValidatorResult(
            validator=self.name,
            passed=max_score < self.flag_threshold,
            risk_score=risk_score,
            findings=findings,
            metadata={"normalized_score": max_score},
        )
