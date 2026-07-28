"""
Small stateless helpers shared across validators: text normalization,
hashing, truncation, and safe-preview generation for logging/audit.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid

_ZERO_WIDTH_RE = re.compile(r"[​‌‍⁠﻿]")
_WHITESPACE_RE = re.compile(r"\s+")


def new_request_id() -> str:
    return str(uuid.uuid4())


def normalize_text(text: str) -> str:
    """Unicode-normalize and strip zero-width/invisible characters that are
    commonly used to evade regex/keyword filters."""
    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH_RE.sub("", text)
    return text


def collapse_whitespace(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def hash_prompt(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"


def safe_preview(text: str, max_chars: int = 120) -> str:
    """A truncated, whitespace-collapsed preview safe to persist in logs
    even when raw-prompt storage is disabled by policy."""
    return truncate(collapse_whitespace(text), max_chars)


def redact_span(text: str, start: int, end: int, mask: str = "*") -> str:
    span_len = end - start
    return text[:start] + (mask * min(span_len, 8)) + text[end:]
