"""
Tasks API - REST endpoints for task triggering.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from cinder_cli.config import Config
from cinder_cli.executor import AutonomousExecutor

router = APIRouter()


class TaskRequest(BaseModel):
    """Task request model."""

    goal: str
    mode: str = "dry-run"
    constraints: dict[str, Any] | None = None


class TaskResponse(BaseModel):
    """Task response model."""

    status: str
    goal: str
    mode: str
    message: str = ""


@router.post("")
async def trigger_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    Trigger a new execution task.

    Args:
        request: Task request with goal and mode
        background_tasks: FastAPI background tasks

    Returns:
        Task status
    """
    if request.mode not in ("auto", "interactive", "dry-run"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}. Must be auto, interactive, or dry-run",
        )

    config = Config()
    executor = AutonomousExecutor(config)

    if request.mode == "dry-run":
        result = executor.execute(
            goal=request.goal,
            mode="dry-run",
            constraints=request.constraints,
        )
        return {
            "status": "completed",
            "goal": request.goal,
            "mode": request.mode,
            "result": result,
        }

    if request.mode == "auto":
        background_tasks.add_task(
            executor.execute,
            goal=request.goal,
            mode="auto",
            constraints=request.constraints,
        )
        return {
            "status": "started",
            "goal": request.goal,
            "mode": request.mode,
            "message": "Task started in background",
        }

    return {
        "status": "error",
        "goal": request.goal,
        "mode": request.mode,
        "message": "Interactive mode not supported via API",
    }


@router.get("/modes")
async def get_available_modes() -> dict[str, Any]:
    """Get available execution modes."""
    return {
        "modes": [
            {
                "name": "dry-run",
                "description": "Preview what would be done without executing",
            },
            {
                "name": "auto",
                "description": "Execute automatically without user interaction",
            },
            {
                "name": "interactive",
                "description": "Execute with user confirmation at each step",
            },
        ]
    }
