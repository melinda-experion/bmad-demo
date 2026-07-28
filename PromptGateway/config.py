"""
Centralized configuration for the Prompt Gateway.

Environment variables (see .env.example) override defaults. The enterprise
policy document (policy.yaml) is loaded once and cached; call
`get_settings.cache_clear()` / `load_policy.cache_clear()` in tests that need
a fresh reload.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App metadata ---
    app_name: str = "Enterprise Prompt Gateway"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Paths ---
    policy_path: str = str(BASE_DIR / "policy.yaml")
    log_dir: str = str(BASE_DIR / "logs")
    audit_db_path: str = str(BASE_DIR / "logs" / "audit.db")

    # --- Ollama / local LLM ---
    # ollama_base_url: str = "http://localhost:11434"
    # ollama_model: str = "llama3.2"
    ollama_base_url: str = "http://192.168.1.5:11434"
    ollama_model: str = "llama3:latest"
    ollama_timeout_seconds: float = 15.0

    # --- CORS ---
    cors_allow_origins: str = "*"

    # --- Auth (optional API key gate for the gateway itself) ---
    api_key: str | None = None
    require_api_key: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_policy(policy_path: str | None = None) -> Dict[str, Any]:
    """Load and cache the enterprise policy YAML document."""
    path = Path(policy_path or get_settings().policy_path)
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        policy = yaml.safe_load(fh) or {}
    return policy


def reload_policy() -> Dict[str, Any]:
    """Force a reload of the policy file (bypasses cache)."""
    load_policy.cache_clear()
    return load_policy()


def ensure_directories() -> None:
    settings = get_settings()
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.audit_db_path).parent.mkdir(parents=True, exist_ok=True)
