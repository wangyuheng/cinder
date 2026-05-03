"""
Session management module.
"""

from __future__ import annotations

import uuid

from cinder_cli.database.session_dao import SessionDAO


class SessionManager:
    """Manages user sessions."""
    
    def __init__(self):
        self.dao = SessionDAO()
    
    def create_session(self, user_id: int, expires_in_days: int = 7) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        self.dao.create(session_id, user_id, expires_in_days)
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """Validate a session."""
        session = self.dao.get_by_session_id(session_id)
        
        if session is None:
            return False
        
        if session.is_expired():
            self.dao.delete(session_id)
            return False
        
        return True
    
    def get_user_id(self, session_id: str) -> int | None:
        """Get user ID from session."""
        session = self.dao.get_by_session_id(session_id)
        
        if session is None or session.is_expired():
            return None
        
        return session.user_id
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        self.dao.delete(session_id)
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        return self.dao.delete_expired()
