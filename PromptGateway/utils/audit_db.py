"""
SQLite-backed audit log for the Prompt Gateway.

Every validated prompt (allowed, flagged, or blocked) is recorded here for
compliance/audit purposes. By default the raw prompt text is NOT stored —
only a SHA-256 hash and a short truncated preview — controlled by
`audit.store_raw_prompt` in policy.yaml.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    request_id          TEXT PRIMARY KEY,
    timestamp           TEXT NOT NULL,
    user_id             TEXT,
    model               TEXT,
    decision            TEXT NOT NULL,
    risk_score          REAL NOT NULL,
    token_count         INTEGER,
    prompt_hash         TEXT NOT NULL,
    prompt_preview      TEXT,
    categories_triggered TEXT,
    validator_results   TEXT,
    reason              TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_decision ON audit_log(decision);
"""


class AuditLogger:
    """Thread-safe wrapper around a single SQLite audit database file."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(_SCHEMA)

    def record(
        self,
        request_id: str,
        timestamp: str,
        decision: str,
        risk_score: float,
        prompt_hash: str,
        prompt_preview: str,
        categories_triggered: List[str],
        validator_results: List[Dict[str, Any]],
        reason: str = "",
        user_id: Optional[str] = None,
        model: Optional[str] = None,
        token_count: int = 0,
    ) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_log (
                    request_id, timestamp, user_id, model, decision, risk_score,
                    token_count, prompt_hash, prompt_preview, categories_triggered,
                    validator_results, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    timestamp,
                    user_id,
                    model,
                    decision,
                    risk_score,
                    token_count,
                    prompt_hash,
                    prompt_preview,
                    json.dumps(categories_triggered),
                    json.dumps(validator_results),
                    reason,
                ),
            )

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM audit_log WHERE request_id = ?", (request_id,)).fetchone()
            return self._row_to_dict(row) if row else None

    def list_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def stats(self) -> Dict[str, Any]:
        with self._lock, self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS c FROM audit_log").fetchone()["c"]
            by_decision = {
                r["decision"]: r["c"]
                for r in conn.execute(
                    "SELECT decision, COUNT(*) AS c FROM audit_log GROUP BY decision"
                ).fetchall()
            }
            avg_risk_row = conn.execute("SELECT AVG(risk_score) AS avg_risk FROM audit_log").fetchone()
            avg_risk = avg_risk_row["avg_risk"] or 0.0

            category_counts: Dict[str, int] = {}
            for row in conn.execute("SELECT categories_triggered FROM audit_log").fetchall():
                try:
                    cats = json.loads(row["categories_triggered"] or "[]")
                except json.JSONDecodeError:
                    cats = []
                for cat in cats:
                    category_counts[cat] = category_counts.get(cat, 0) + 1

            top_categories = dict(
                sorted(category_counts.items(), key=lambda kv: kv[1], reverse=True)[:10]
            )

            return {
                "total_requests": total,
                "allowed": by_decision.get("ALLOW", 0),
                "flagged": by_decision.get("FLAG", 0),
                "blocked": by_decision.get("BLOCK", 0),
                "average_risk_score": round(avg_risk, 2),
                "top_categories": top_categories,
            }

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        d["categories_triggered"] = json.loads(d.get("categories_triggered") or "[]")
        d["validator_results"] = json.loads(d.get("validator_results") or "[]")
        return d
