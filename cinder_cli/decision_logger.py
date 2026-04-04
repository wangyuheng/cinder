"""
Decision logger module for recording and querying proxy decisions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cinder_cli.database import DecisionDatabase


class DecisionLogger:
    """High-level interface for decision logging."""

    def __init__(self, db_path: Path):
        self.db = DecisionDatabase(db_path)

    def log_decision(
        self,
        context: dict[str, Any],
        soul_rules: dict[str, Any],
        decision: dict[str, Any],
        confidence: float,
        requires_human: bool,
    ) -> int:
        """Log a proxy decision."""
        return self.db.insert_decision(
            context=context,
            soul_rules=soul_rules,
            decision=decision,
            confidence=confidence,
            requires_human=requires_human,
        )

    def get_decision(self, decision_id: int) -> dict[str, Any] | None:
        """Get a decision by ID."""
        return self.db.get_decision(decision_id)

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
        return self.db.list_decisions(
            limit=limit,
            offset=offset,
            min_confidence=min_confidence,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get decision statistics."""
        return self.db.get_statistics()

    def update_review(
        self,
        decision_id: int,
        reviewed: bool,
        review_result: str | None = None,
        review_reason: str | None = None,
    ) -> None:
        """Update review status of a decision."""
        self.db.update_review(
            decision_id=decision_id,
            reviewed=reviewed,
            review_result=review_result,
            review_reason=review_reason,
        )

    def delete_old_decisions(self, days: int, archive: bool = False) -> int:
        """Delete decisions older than specified days."""
        return self.db.delete_old_decisions(days=days, archive=archive)
