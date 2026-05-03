"""
Session data access object.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.models import UserSession


class SessionDAO:
    """Data access object for user sessions."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def create(self, session_id: str, user_id: int, expires_in_days: int = 7) -> UserSession:
        """Create a new session."""
        created_at = datetime.now().isoformat(timespec="seconds")
        expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat(timespec="seconds")
        
        self.db.execute(
            """
            INSERT INTO user_sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, user_id, created_at, expires_at),
        )
        
        return self.get_by_session_id(session_id)
    
    def get_by_session_id(self, session_id: str) -> UserSession | None:
        """Get session by session ID."""
        row = self.db.fetch_one(
            "SELECT * FROM user_sessions WHERE session_id = ?",
            (session_id,),
        )
        
        if row:
            return self._row_to_session(row)
        return None
    
    def delete(self, session_id: str) -> None:
        """Delete a session."""
        self.db.execute(
            "DELETE FROM user_sessions WHERE session_id = ?",
            (session_id,),
        )
    
    def delete_expired(self) -> int:
        """Delete all expired sessions."""
        cursor = self.db.execute(
            "DELETE FROM user_sessions WHERE expires_at < datetime('now')",
        )
        return cursor.rowcount
    
    def delete_by_user(self, user_id: int) -> None:
        """Delete all sessions for a user."""
        self.db.execute(
            "DELETE FROM user_sessions WHERE user_id = ?",
            (user_id,),
        )
    
    def _row_to_session(self, row: dict[str, Any]) -> UserSession:
        """Convert database row to UserSession model."""
        return UserSession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            expires_at=row["expires_at"],
        )
