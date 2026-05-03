"""
Invitation code validator.
"""

from __future__ import annotations

from cinder_cli.database.connection import DatabaseConnection
from cinder_cli.database.models import InvitationCode
from cinder_cli.invitation.loader import InvitationLoader


class InvitationValidator:
    """Validates invitation codes."""
    
    def __init__(self, loader: InvitationLoader | None = None):
        self.loader = loader or InvitationLoader()
        self.db = DatabaseConnection()
    
    def validate(self, code_value: str) -> tuple[bool, str]:
        """
        Validate an invitation code.
        
        Returns:
            Tuple of (is_valid, message)
        """
        code = self.loader.get_code_by_value(code_value)
        
        if code is None:
            return False, "邀请码无效"
        
        if not code.is_active:
            return False, "邀请码已被禁用"
        
        db_code = self._get_db_code(code_value)
        
        if db_code:
            used_count = db_code["used_count"]
            
            if code.is_single_use and used_count > 0:
                return False, "邀请码已被使用"
            
            if code.max_uses is not None and used_count >= code.max_uses:
                return False, "邀请码已达到使用上限"
        
        return True, "邀请码有效"
    
    def record_usage(self, code_value: str) -> None:
        """Record usage of an invitation code."""
        code = self.loader.get_code_by_value(code_value)
        if code is None:
            return
        
        db_code = self._get_db_code(code_value)
        
        if db_code:
            self.db.execute(
                "UPDATE invitation_codes SET used_count = used_count + 1 WHERE code = ?",
                (code_value,),
            )
        else:
            self.db.execute(
                """
                INSERT INTO invitation_codes 
                (code, is_single_use, used_count, max_uses, created_at, is_active)
                VALUES (?, ?, 1, ?, ?, ?)
                """,
                (
                    code.code,
                    code.is_single_use,
                    code.max_uses,
                    code.created_at,
                    code.is_active,
                ),
            )
    
    def _get_db_code(self, code_value: str) -> dict | None:
        """Get invitation code from database."""
        return self.db.fetch_one(
            "SELECT * FROM invitation_codes WHERE code = ?",
            (code_value,),
        )
