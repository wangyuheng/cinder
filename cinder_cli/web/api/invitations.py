"""
Invitation API endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cinder_cli.invitation.validator import InvitationValidator

router = APIRouter()


class ValidateInvitationRequest(BaseModel):
    """Validate invitation request model."""
    
    code: str


class ValidateInvitationResponse(BaseModel):
    """Validate invitation response model."""
    
    valid: bool
    message: str


@router.post("/validate", response_model=ValidateInvitationResponse)
async def validate_invitation(request: ValidateInvitationRequest) -> dict[str, Any]:
    """Validate an invitation code."""
    validator = InvitationValidator()
    is_valid, message = validator.validate(request.code)
    
    if not is_valid:
        return {
            "valid": False,
            "message": message,
        }
    
    return {
        "valid": True,
        "message": message,
    }
