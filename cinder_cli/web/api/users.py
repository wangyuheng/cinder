"""
User API endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cinder_cli.database.user_dao import UserDAO

router = APIRouter()


class CreateUserRequest(BaseModel):
    """Create user request model."""
    
    name: str = Field(..., min_length=1, max_length=50, description="User name")


class UserResponse(BaseModel):
    """User response model."""
    
    id: int
    name: str
    created_at: str
    soul_path: str | None = None
    onboarding_completed: bool = False


@router.post("", response_model=UserResponse)
async def create_user(request: CreateUserRequest) -> dict[str, Any]:
    """Create a new user."""
    dao = UserDAO()
    user = dao.create(request.name)
    
    if user is None:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at,
        "soul_path": user.soul_path,
        "onboarding_completed": user.onboarding_completed,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int) -> dict[str, Any]:
    """Get current user information."""
    dao = UserDAO()
    user = dao.get_by_id(user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "name": user.name,
        "created_at": user.created_at,
        "soul_path": user.soul_path,
        "onboarding_completed": user.onboarding_completed,
    }
