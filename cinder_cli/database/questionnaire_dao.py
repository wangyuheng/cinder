"""
Questionnaire answer data access object.
"""

from __future__ import annotations

from typing import Any

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.models import QuestionnaireAnswer


class QuestionnaireDAO:
    """Data access object for questionnaire answers."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def save_answer(self, user_id: int, question_key: str, choice: str, reason: str = "") -> QuestionnaireAnswer:
        """Save a questionnaire answer."""
        existing = self.get_answer(user_id, question_key)
        
        if existing:
            self.db.execute(
                """
                UPDATE questionnaire_answers 
                SET choice = ?, reason = ?, created_at = datetime('now')
                WHERE user_id = ? AND question_key = ?
                """,
                (choice, reason, user_id, question_key),
            )
            return self.get_answer(user_id, question_key)
        
        cursor = self.db.execute(
            """
            INSERT INTO questionnaire_answers (user_id, question_key, choice, reason, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            """,
            (user_id, question_key, choice, reason),
        )
        
        answer_id = cursor.lastrowid
        return self.get_answer_by_id(answer_id)
    
    def get_answer(self, user_id: int, question_key: str) -> QuestionnaireAnswer | None:
        """Get answer for a specific question."""
        row = self.db.fetch_one(
            "SELECT * FROM questionnaire_answers WHERE user_id = ? AND question_key = ?",
            (user_id, question_key),
        )
        
        if row:
            return self._row_to_answer(row)
        return None
    
    def get_answer_by_id(self, answer_id: int) -> QuestionnaireAnswer | None:
        """Get answer by ID."""
        row = self.db.fetch_one(
            "SELECT * FROM questionnaire_answers WHERE id = ?",
            (answer_id,),
        )
        
        if row:
            return self._row_to_answer(row)
        return None
    
    def get_all_answers(self, user_id: int) -> list[QuestionnaireAnswer]:
        """Get all answers for a user."""
        rows = self.db.fetch_all(
            "SELECT * FROM questionnaire_answers WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        )
        return [self._row_to_answer(row) for row in rows]
    
    def get_progress(self, user_id: int) -> dict[str, Any]:
        """Get questionnaire progress for a user."""
        answers = self.get_all_answers(user_id)
        return {
            "completed": len(answers),
            "total": 6,
            "answers": {ans.question_key: {"choice": ans.choice, "reason": ans.reason} for ans in answers},
        }
    
    def clear_progress(self, user_id: int) -> None:
        """Clear questionnaire progress for a user."""
        self.db.execute(
            "DELETE FROM questionnaire_answers WHERE user_id = ?",
            (user_id,),
        )
    
    def _row_to_answer(self, row: dict[str, Any]) -> QuestionnaireAnswer:
        """Convert database row to QuestionnaireAnswer model."""
        return QuestionnaireAnswer(
            id=row["id"],
            user_id=row["user_id"],
            question_key=row["question_key"],
            choice=row["choice"],
            reason=row["reason"] or "",
            created_at=row["created_at"],
        )
