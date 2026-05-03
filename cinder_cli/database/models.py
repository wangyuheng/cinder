"""
Database models for user management and onboarding.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User model."""
    
    id: Optional[int] = None
    name: str = ""
    created_at: str = ""
    soul_path: Optional[str] = None
    onboarding_completed: bool = False
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")


@dataclass
class InvitationCode:
    """Invitation code model."""
    
    code: str
    is_single_use: bool = True
    used_count: int = 0
    max_uses: Optional[int] = None
    created_at: str = ""
    is_active: bool = True
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")
    
    def can_use(self) -> bool:
        """Check if this invitation code can be used."""
        if not self.is_active:
            return False
        
        if self.is_single_use and self.used_count > 0:
            return False
        
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        
        return True


@dataclass
class UserSession:
    """User session model."""
    
    session_id: str
    user_id: int
    created_at: str = ""
    expires_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")
    
    def is_expired(self) -> bool:
        """Check if this session is expired."""
        if not self.expires_at:
            return False
        return datetime.now().isoformat(timespec="seconds") > self.expires_at


@dataclass
class QuestionnaireAnswer:
    """Questionnaire answer model."""
    
    id: Optional[int] = None
    user_id: int = 0
    question_key: str = ""
    choice: str = ""
    reason: str = ""
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")
