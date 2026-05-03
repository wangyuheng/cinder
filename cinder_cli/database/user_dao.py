"""
User data access object.
"""

from __future__ import annotations

from typing import Any

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.models import User


class UserDAO:
    """Data access object for users."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, name: str) -> User:
        """Create a new user."""
        cursor = self.db.execute(
            """
            INSERT INTO users (name, created_at, onboarding_completed)
            VALUES (?, datetime('now'), 0)
            """,
            (name,),
        )
        
        user_id = cursor.lastrowid
        return self.get_by_id(user_id)
    
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        )
        
        if row:
            return self._row_to_user(row)
        return None
    
    def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Get all users."""
        rows = self.db.fetch_all(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return [self._row_to_user(row) for row in rows]
    
    def update_onboarding_status(self, user_id: int, completed: bool) -> None:
        """Update user's onboarding completion status."""
        self.db.execute(
            "UPDATE users SET onboarding_completed = ? WHERE id = ?",
            (completed, user_id),
        )
    
    def update_soul_path(self, user_id: int, soul_path: str) -> None:
        """Update user's soul path."""
        self.db.execute(
            "UPDATE users SET soul_path = ? WHERE id = ?",
            (soul_path, user_id),
        )
    
    def _row_to_user(self, row: dict[str, Any]) -> User:
        """Convert database row to User model."""
        return User(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            soul_path=row["soul_path"],
            onboarding_completed=bool(row["onboarding_completed"]),
        )
