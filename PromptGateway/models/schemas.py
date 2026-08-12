"""
Pydantic request/response schemas exposed by the FastAPI layer.
Kept separate from `models/prompt_result.py` (internal dataclasses) so the
public API contract can evolve independently of internal pipeline types.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class PromptValidateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=50_000, description="Raw user prompt to validate")
    user_id: Optional[str] = Field(None, description="Identifier of the calling user/service")
    model: Optional[str] = Field(None, description="Target downstream LLM this prompt would be sent to")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional free-form context/metadata")

    @field_validator("prompt")
    @classmethod
    def prompt_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("prompt must not be blank")
        return v


class FindingSchema(BaseModel):
    name: str
    category: str
    risk_score: float
    description: str
    matched_snippet: Optional[str] = None
    severity: str


class ValidatorResultSchema(BaseModel):
    validator: str
    passed: bool
    risk_score: float
    findings: List[FindingSchema]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class PromptValidateResponse(BaseModel):
    request_id: str
    decision: str
    risk_score: float
    token_count: int
    sanitized_prompt: Optional[str] = None
    categories_triggered: List[str]
    timestamp: str
    reason: str
    validator_results: List[ValidatorResultSchema]


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    ollama_reachable: Optional[bool] = None


class PolicyResponse(BaseModel):
    version: int
    decision_thresholds: Dict[str, Any]
    weights: Dict[str, float]
    allowed_models: List[str]


class AuditRecordResponse(BaseModel):
    request_id: str
    timestamp: str
    user_id: Optional[str]
    model: Optional[str]
    decision: str
    risk_score: float
    prompt_preview: str
    prompt_hash: str
    categories_triggered: List[str]


class StatsResponse(BaseModel):
    total_requests: int
    allowed: int
    flagged: int
    blocked: int
    average_risk_score: float
    top_categories: Dict[str, int]
