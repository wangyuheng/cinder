"""
User feedback collection system for progress tracking.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FeedbackType:
    """Feedback type constants."""
    ESTIMATION_ACCURACY = "estimation_accuracy"
    PROGRESS_DISPLAY = "progress_display"
    PERFORMANCE = "performance"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class FeedbackRating:
    """Feedback rating constants."""
    VERY_POOR = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5


class UserFeedback(BaseModel):
    """User feedback model."""
    execution_id: int
    feedback_type: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    estimated_time: Optional[float] = None
    actual_time: Optional[float] = None
    estimation_accuracy: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FeedbackCollector:
    """Collects and manages user feedback."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER NOT NULL,
                feedback_type TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                estimated_time REAL,
                actual_time REAL,
                estimation_accuracy REAL,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_execution
            ON user_feedback(execution_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_type
            ON user_feedback(feedback_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
            ON user_feedback(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def submit_feedback(self, feedback: UserFeedback) -> int:
        """Submit user feedback."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_feedback (
                execution_id, feedback_type, rating, comment,
                estimated_time, actual_time, estimation_accuracy,
                timestamp, user_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            feedback.execution_id,
            feedback.feedback_type,
            feedback.rating,
            feedback.comment,
            feedback.estimated_time,
            feedback.actual_time,
            feedback.estimation_accuracy,
            feedback.timestamp.isoformat(),
            feedback.user_id,
            json.dumps(feedback.metadata) if feedback.metadata else None,
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_feedback_by_execution(self, execution_id: int) -> List[Dict[str, Any]]:
        """Get all feedback for an execution."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_feedback
            WHERE execution_id = ?
            ORDER BY timestamp DESC
        """, (execution_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_feedback_by_type(
        self,
        feedback_type: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get feedback by type."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_feedback
            WHERE feedback_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (feedback_type, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                COUNT(*) as total_feedback,
                AVG(rating) as average_rating,
                feedback_type
            FROM user_feedback
            GROUP BY feedback_type
        """)
        
        type_stats = {}
        for row in cursor.fetchall():
            type_stats[row[2]] = {
                "count": row[0],
                "average_rating": row[1],
            }
        
        cursor.execute("""
            SELECT AVG(estimation_accuracy)
            FROM user_feedback
            WHERE estimation_accuracy IS NOT NULL
        """)
        
        avg_accuracy = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM user_feedback
            WHERE timestamp >= date('now', '-30 days')
        """)
        
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_feedback": sum(s["count"] for s in type_stats.values()),
            "average_rating": avg_accuracy,
            "estimation_accuracy": avg_accuracy,
            "recent_feedback_count": recent_count,
            "by_type": type_stats,
        }
    
    def get_estimation_accuracy_metrics(self) -> Dict[str, Any]:
        """Get estimation accuracy metrics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                estimated_time,
                actual_time,
                estimation_accuracy
            FROM user_feedback
            WHERE estimated_time IS NOT NULL
            AND actual_time IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                "total_samples": 0,
                "average_accuracy": None,
                "average_error": None,
            }
        
        accuracies = [row[2] for row in rows if row[2] is not None]
        errors = [
            abs(row[0] - row[1]) / row[1] * 100
            for row in rows
            if row[0] and row[1]
        ]
        
        return {
            "total_samples": len(rows),
            "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
            "average_error": sum(errors) / len(errors) if errors else None,
            "min_accuracy": min(accuracies) if accuracies else None,
            "max_accuracy": max(accuracies) if accuracies else None,
        }
    
    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            "id": row[0],
            "execution_id": row[1],
            "feedback_type": row[2],
            "rating": row[3],
            "comment": row[4],
            "estimated_time": row[5],
            "actual_time": row[6],
            "estimation_accuracy": row[7],
            "timestamp": row[8],
            "user_id": row[9],
            "metadata": json.loads(row[10]) if row[10] else None,
            "created_at": row[11],
        }
