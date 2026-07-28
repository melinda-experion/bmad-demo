"""
Enterprise Prompt Gateway - FastAPI application entrypoint.

Run with:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import ensure_directories, get_settings, load_policy
from models.schemas import (
    AuditRecordResponse,
    HealthResponse,
    PolicyResponse,
    PromptValidateRequest,
    PromptValidateResponse,
    StatsResponse,
)
from utils.audit_db import AuditLogger
from utils.logger import configure_logging, get_logger, log_with_fields
from utils.prompt_utils import hash_prompt, safe_preview
from validators.decision_engine import DecisionEngine

settings = get_settings()
ensure_directories()
configure_logging(log_dir=settings.log_dir)
logger = get_logger("prompt_gateway")

policy = load_policy()
# Environment variables (.env) take precedence over policy.yaml defaults for
# the local-LLM connection, so the same policy file can point at different
# Ollama hosts across dev/staging/prod without editing YAML per environment.
policy.setdefault("llm_validator", {})
policy["llm_validator"]["base_url"] = settings.ollama_base_url
policy["llm_validator"]["model"] = settings.ollama_model
policy["llm_validator"]["timeout_seconds"] = settings.ollama_timeout_seconds

decision_engine = DecisionEngine(policy)
audit_logger = AuditLogger(settings.audit_db_path)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise-grade gateway that validates prompts before they reach an "
        "LLM: regex rules, PII/secret detection, toxicity screening, prompt-"
        "injection detection, token limits, and a local-LLM (Ollama) risk "
        "assessment, combined via a configurable policy-driven decision engine."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if not settings.require_api_key:
        return
    if not settings.api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception processing %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "type": exc.__class__.__name__},
    )


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
async def health() -> HealthResponse:
    ollama_ok = await decision_engine.llm_validator.check_health()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        ollama_reachable=ollama_ok,
    )


@app.get("/api/v1/policy", response_model=PolicyResponse, tags=["Policy"], dependencies=[Depends(verify_api_key)])
async def get_policy() -> PolicyResponse:
    return PolicyResponse(
        version=policy.get("version", 1),
        decision_thresholds=policy.get("decision", {}),
        weights=policy.get("weights", {}),
        allowed_models=policy.get("allowed_models", []),
    )


@app.post(
    "/api/v1/validate",
    response_model=PromptValidateResponse,
    tags=["Validation"],
    dependencies=[Depends(verify_api_key)],
)
async def validate_prompt(payload: PromptValidateRequest) -> PromptValidateResponse:
    if payload.model and policy.get("allowed_models") and payload.model not in policy["allowed_models"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{payload.model}' is not in the allowed_models policy list",
        )

    result = await decision_engine.evaluate(payload.prompt)

    audit_cfg = policy.get("audit", {})
    if audit_cfg.get("enabled", True):
        preview = (
            payload.prompt if audit_cfg.get("store_raw_prompt") else safe_preview(
                payload.prompt, audit_cfg.get("preview_chars", 120)
            )
        )
        audit_logger.record(
            request_id=result.request_id,
            timestamp=result.timestamp,
            decision=result.decision.value,
            risk_score=result.risk_score,
            prompt_hash=hash_prompt(payload.prompt),
            prompt_preview=preview,
            categories_triggered=result.categories_triggered,
            validator_results=[r.to_dict() for r in result.validator_results],
            reason=result.reason,
            user_id=payload.user_id,
            model=payload.model,
            token_count=result.token_count,
        )

    log_with_fields(
        logger,
        logging.INFO,
        "prompt validated",
        request_id=result.request_id,
        decision=result.decision.value,
        risk_score=result.risk_score,
        user_id=payload.user_id,
    )

    return PromptValidateResponse(**result.to_dict())


@app.get(
    "/api/v1/audit/{request_id}",
    response_model=AuditRecordResponse,
    tags=["Audit"],
    dependencies=[Depends(verify_api_key)],
)
async def get_audit_record(request_id: str) -> AuditRecordResponse:
    record = audit_logger.get(request_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit record not found")
    return AuditRecordResponse(
        request_id=record["request_id"],
        timestamp=record["timestamp"],
        user_id=record.get("user_id"),
        model=record.get("model"),
        decision=record["decision"],
        risk_score=record["risk_score"],
        prompt_preview=record.get("prompt_preview") or "",
        prompt_hash=record["prompt_hash"],
        categories_triggered=record["categories_triggered"],
    )


@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Audit"], dependencies=[Depends(verify_api_key)])
async def get_stats() -> StatsResponse:
    return StatsResponse(**audit_logger.stats())


@app.get("/", tags=["Operations"])
async def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
