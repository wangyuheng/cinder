"""
Tests for database operations.
"""

import tempfile
from pathlib import Path

import pytest

from cinder_cli.database import DecisionDatabase


class TestDecisionDatabase:
    """Test cases for DecisionDatabase."""

    @pytest.fixture
    def db(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield DecisionDatabase(db_path)

    def test_insert_and_get_decision(self, db):
        """Test inserting and retrieving a decision."""
        decision_id = db.insert_decision(
            context={"question": "test"},
            soul_rules={"rules": ["test_rule"]},
            decision={"choice": "A"},
            confidence=0.8,
            requires_human=False,
        )

        assert decision_id > 0

        decision = db.get_decision(decision_id)
        assert decision is not None
        assert decision["context"] == {"question": "test"}
        assert decision["confidence"] == 0.8

    def test_list_decisions(self, db):
        """Test listing decisions."""
        for i in range(5):
            db.insert_decision(
                context={"test": i},
                soul_rules={},
                decision={},
                confidence=0.5,
                requires_human=False,
            )

        decisions = db.list_decisions(limit=3)
        assert len(decisions) == 3

    def test_update_review(self, db):
        """Test updating review status."""
        decision_id = db.insert_decision(
            context={},
            soul_rules={},
            decision={},
            confidence=0.5,
            requires_human=False,
        )

        db.update_review(
            decision_id,
            reviewed=True,
            review_result="correct",
            review_reason="Good decision",
        )

        decision = db.get_decision(decision_id)
        assert decision["reviewed"] is True
        assert decision["review_result"] == "correct"

    def test_statistics(self, db):
        """Test statistics generation."""
        for i in range(3):
            db.insert_decision(
                context={},
                soul_rules={},
                decision={},
                confidence=0.5 + i * 0.1,
                requires_human=i == 0,
            )

        stats = db.get_statistics()
        assert stats["total"] == 3
        assert stats["requires_human_count"] == 1
