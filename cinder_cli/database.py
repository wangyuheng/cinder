"""
Database module for SQLite decision logging.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


class DecisionDatabase:
    """Manages SQLite database for decision logging."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        context TEXT NOT NULL,
        soul_rules TEXT NOT NULL,
        decision TEXT NOT NULL,
        confidence REAL NOT NULL,
        requires_human BOOLEAN NOT NULL,
        reviewed BOOLEAN DEFAULT FALSE,
        review_result TEXT,
        review_reason TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_timestamp ON decisions(timestamp);
    CREATE INDEX IF NOT EXISTS idx_confidence ON decisions(confidence);
    CREATE INDEX IF NOT EXISTS idx_reviewed ON decisions(reviewed);
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database with schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.SCHEMA)
            conn.commit()

    def insert_decision(
        self,
        context: dict[str, Any],
        soul_rules: dict[str, Any],
        decision: dict[str, Any],
        confidence: float,
        requires_human: bool,
    ) -> int:
        """Insert a new decision record."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO decisions 
                (timestamp, context, soul_rules, decision, confidence, requires_human)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    json.dumps(context, ensure_ascii=False),
                    json.dumps(soul_rules, ensure_ascii=False),
                    json.dumps(decision, ensure_ascii=False),
                    confidence,
                    requires_human,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_decision(self, decision_id: int) -> dict[str, Any] | None:
        """Get a decision by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM decisions WHERE id = ?", (decision_id,)
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def list_decisions(
        self,
        limit: int = 10,
        offset: int = 0,
        min_confidence: float | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        """List decisions with optional filtering."""
        query = "SELECT * FROM decisions WHERE 1=1"
        params: list[Any] = []

        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)

        if from_date:
            query += " AND timestamp >= ?"
            params.append(from_date)

        if to_date:
            query += " AND timestamp <= ?"
            params.append(to_date)

        if search:
            query += " AND context LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_decisions(
        self,
        min_confidence: float | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        search: str | None = None,
    ) -> int:
        """Count decisions with optional filtering."""
        query = "SELECT COUNT(*) FROM decisions WHERE 1=1"
        params: list[Any] = []

        if min_confidence is not None:
            query += " AND confidence >= ?"
            params.append(min_confidence)

        if from_date:
            query += " AND timestamp >= ?"
            params.append(from_date)

        if to_date:
            query += " AND timestamp <= ?"
            params.append(to_date)

        if search:
            query += " AND context LIKE ?"
            params.append(f"%{search}%")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]

    def update_review(
        self,
        decision_id: int,
        reviewed: bool,
        review_result: str | None = None,
        review_reason: str | None = None,
    ) -> None:
        """Update review status of a decision."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE decisions 
                SET reviewed = ?, review_result = ?, review_reason = ?
                WHERE id = ?
                """,
                (reviewed, review_result, review_reason, decision_id),
            )
            conn.commit()

    def get_statistics(self) -> dict[str, Any]:
        """Get decision statistics."""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}

            cursor = conn.execute("SELECT COUNT(*) FROM decisions")
            stats["total"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT AVG(confidence) FROM decisions")
            stats["avg_confidence"] = cursor.fetchone()[0] or 0.0

            cursor = conn.execute(
                "SELECT COUNT(*) FROM decisions WHERE requires_human = 1"
            )
            stats["requires_human_count"] = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM decisions WHERE reviewed = 1")
            stats["reviewed_count"] = cursor.fetchone()[0]

            return stats

    def delete_old_decisions(self, days: int, archive: bool = False) -> int:
        """Delete decisions older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 86400)
        cutoff_date = datetime.fromtimestamp(cutoff).isoformat(timespec="seconds")

        with sqlite3.connect(self.db_path) as conn:
            if archive:
                pass

            cursor = conn.execute(
                "DELETE FROM decisions WHERE timestamp < ?", (cutoff_date,)
            )
            conn.commit()
            return cursor.rowcount

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a database row to dictionary."""
        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "context": json.loads(row["context"]),
            "soul_rules": json.loads(row["soul_rules"]),
            "decision": json.loads(row["decision"]),
            "confidence": row["confidence"],
            "requires_human": bool(row["requires_human"]),
            "reviewed": bool(row["reviewed"]),
            "review_result": row["review_result"],
            "review_reason": row["review_reason"],
        }
