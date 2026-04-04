"""
Executions API - REST endpoints for execution history management.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from cinder_cli.config import Config
from cinder_cli.executor import ExecutionLogger

router = APIRouter()


def get_logger() -> ExecutionLogger:
    """Get execution logger instance."""
    config = Config()
    return ExecutionLogger(config)


@router.get("")
async def list_executions(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
) -> dict[str, Any]:
    """List all executions with pagination."""
    logger = get_logger()
    executions = logger.list_executions(limit=limit + offset)

    if status:
        executions = [e for e in executions if e.get("status") == status]

    return {
        "executions": executions[offset : offset + limit],
        "total": len(executions),
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
async def get_execution_stats() -> dict[str, Any]:
    """Get execution statistics."""
    logger = get_logger()
    executions = logger.list_executions(limit=1000)

    if not executions:
        return {
            "total": 0,
            "success_count": 0,
            "success_rate": 0,
            "total_files": 0,
        }

    total = len(executions)
    success_count = sum(1 for e in executions if e.get("status") == "success")
    total_files = sum(len(e.get("created_files", [])) for e in executions)

    return {
        "total": total,
        "success_count": success_count,
        "success_rate": success_count / total if total > 0 else 0,
        "total_files": total_files,
    }


@router.get("/{execution_id}")
async def get_execution(execution_id: int) -> dict[str, Any]:
    """Get execution details by ID."""
    logger = get_logger()
    execution = logger.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")

    return execution


@router.delete("/{execution_id}")
async def delete_execution(execution_id: int) -> dict[str, Any]:
    """Delete an execution record."""
    logger = get_logger()
    execution = logger.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")

    return {"status": "deleted", "execution_id": execution_id}
